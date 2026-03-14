import sqlite3
import os
from datetime import datetime
import pickle
import numpy as np
from settings import MATCH_THRESHOLD
from fingerprint_classical import (
    serialize_classical_features, deserialize_classical_features,
    match_fingerprints_classical
)

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), 'database.db')

def get_connection():
    """
    Create and return a database connection.
    Enables foreign key constraints for CASCADE delete.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')  # Enable CASCADE delete
    return conn

def init_database():
    """
    Initialize the database and create tables if they don't exist.
    Supports multi-sample fingerprints for each user.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            blood_group TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(name)
        )
    ''')
    
    # Create fingerprint_samples table (one user can have multiple samples)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fingerprint_samples (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            fingerprint_hash TEXT NOT NULL UNIQUE,
            fingerprint_features BLOB,
            quality_score REAL,
            captured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

def register_user(name, blood_group, fingerprint_hash, fingerprint_features=None):
    """
    Register a new user with fingerprint(s) and blood group.
    
    Args:
        name (str): User's name
        blood_group (str): User's blood group
        fingerprint_hash (str): SHA256 hash of fingerprint
        fingerprint_features (dict): Features dictionary (keypoints, descriptors, ridge properties, etc.)
    
    Returns:
        dict: Success/error message with user_id on success
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Check if user already exists
        cursor.execute('SELECT id FROM users WHERE name = ?', (name,))
        existing_user = cursor.fetchone()
        
        user_id = None
        if existing_user:
            user_id = existing_user['id']
        else:
            # Insert new user
            cursor.execute('''
                INSERT INTO users (name, blood_group)
                VALUES (?, ?)
            ''', (name, blood_group))
            user_id = cursor.lastrowid
        
        # Serialize features for storage
        features_blob = None
        quality_score = None
        
        if fingerprint_features is not None:
            try:
                # Use serialize_classical_features to make features pickleable
                serializable_features = serialize_classical_features(fingerprint_features)
                features_blob = pickle.dumps(serializable_features)
                quality_score = fingerprint_features.get('quality_score', 0.5)
            except Exception as e:
                print(f"Warning: Could not serialize features: {str(e)}")
                # Continue even if features can't be serialized, just store hash
        
        # Insert fingerprint sample
        cursor.execute('''
            INSERT INTO fingerprint_samples 
            (user_id, fingerprint_hash, fingerprint_features, quality_score)
            VALUES (?, ?, ?, ?)
        ''', (user_id, fingerprint_hash, features_blob, quality_score))
        
        conn.commit()
        conn.close()
        
        action = 'updated' if existing_user else 'registered'
        return {
            'status': 'success',
            'message': f'User {name} {action} successfully with new fingerprint sample!',
            'user_id': user_id
        }
    
    except sqlite3.IntegrityError as e:
        conn.close()
        error_msg = str(e)
        print(f"[DATABASE ERROR] IntegrityError: {error_msg}")
        
        # Check what actually caused the integrity error
        if 'UNIQUE constraint failed: users.name' in error_msg:
            return {
                'status': 'error',
                'message': 'A user with this name already exists!'
            }
        elif 'fingerprint_hash' in error_msg.lower():
            return {
                'status': 'error',
                'message': 'Fingerprint already registered to another user!'
            }
        else:
            return {
                'status': 'error',
                'message': f'Database constraint violation: {error_msg}'
            }
    
    except Exception as e:
        conn.close()
        return {
            'status': 'error',
            'message': f'Database error: {str(e)}'
        }

def verify_fingerprint(fingerprint_hash, fingerprint_features=None, match_threshold=None, strict_mode=True):
    """
    Verify a fingerprint by comparing against all registered samples.
    
    Implements multi-sample verification:
    1. Try exact hash match first (fastest)
    2. If no exact match, try fuzzy matching against all samples
    3. Validate match consistency across samples if multiple samples exist
    4. Reject if match score is inconsistent or below threshold
    
    Args:
        fingerprint_hash (str): SHA256 hash of fingerprint
        fingerprint_features (dict): Features dictionary from verification image
        match_threshold (float): Minimum match score (0-1) for acceptance
        strict_mode (bool): If True, apply stricter matching criteria
    
    Returns:
        dict: User data if match found, error message otherwise
    """
    # Use threshold from settings if not provided (use lower threshold for classical matching robustness)
    if match_threshold is None:
        match_threshold = 0.60  # Lower than MATCH_THRESHOLD (0.80) to handle variations in angles/pressure/distortion
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Step 1: Try exact hash match first
        cursor.execute('''
            SELECT fs.user_id, u.name, u.blood_group, fs.fingerprint_features
            FROM fingerprint_samples fs
            JOIN users u ON fs.user_id = u.id
            WHERE fs.fingerprint_hash = ?
        ''', (fingerprint_hash,))
        
        exact_match = cursor.fetchone()
        
        if exact_match:
            conn.close()
            return {
                'status': 'success',
                'name': exact_match['name'],
                'blood_group': exact_match['blood_group'],
                'match_type': 'exact',
                'match_score': 1.0,
                'confidence': 'Very High'
            }
        
        # Step 2: If no exact match and we have features, try fuzzy matching
        if fingerprint_features is None:
            conn.close()
            return {
                'status': 'error',
                'message': 'Fingerprint not found in database!',
                'confidence': 'N/A'
            }
        
        # Get all fingerprint samples from database
        cursor.execute('''
            SELECT fs.id, fs.user_id, u.name, u.blood_group, fs.fingerprint_features, fs.quality_score
            FROM fingerprint_samples fs
            JOIN users u ON fs.user_id = u.id
            ORDER BY u.id
        ''')
        
        samples = cursor.fetchall()
        
        # Try to match against each sample using classical methods
        user_matches = {}  # user_id -> list of match results
        
        for sample in samples:
            user_id = sample['user_id']
            
            if sample['fingerprint_features']:
                try:
                    stored_features = deserialize_classical_features(sample['fingerprint_features'])
                    if stored_features:
                        # Use classical fingerprint matching (threshold=0.65 handles rotations/distortions/noise)
                        match_result = match_fingerprints_classical(
                            fingerprint_features, 
                            stored_features, 
                            threshold=0.65
                        )
                        
                        if user_id not in user_matches:
                            user_matches[user_id] = {
                                'results': [],
                                'name': sample['name'],
                                'blood_group': sample['blood_group']
                            }
                        
                        user_matches[user_id]['results'].append(match_result)
                
                except Exception as e:
                    print(f"Error matching with sample {sample['id']}: {str(e)}")
                    continue
        
        # Step 3: Validate and find best match
        best_user = None
        best_score = 0
        best_result = None
        
        print(f"\n[VERIFICATION] Total samples in database: {len(samples)}")
        print(f"[VERIFICATION] Match threshold: {match_threshold}")
        
        for user_id, match_data in user_matches.items():
            results = match_data['results']
            
            if results:
                # Get best result for this user
                best_user_result = max(results, key=lambda x: x['score'])
                print(f"[VERIFICATION] User '{match_data['name']}': Best Score = {best_user_result['score']:.4f}")
                print(f"               (Minutiae: {best_user_result['minutiae_score']:.4f}, Correlation: {best_user_result['correlation_score']:.4f}, Pattern: {best_user_result['pattern_score']:.4f})")
                
                if best_user_result['score'] > best_score:
                    best_score = best_user_result['score']
                    best_user = user_id
                    best_result = best_user_result
                    best_match_data = match_data
        
        if best_user and best_score >= match_threshold:
            print(f"[VERIFICATION] ✓ MATCH FOUND! Score {best_score:.4f} >= threshold {match_threshold}")
            conn.close()
            
            return {
                'status': 'success',
                'name': best_match_data['name'],
                'blood_group': best_match_data['blood_group'],
                'match_type': 'classical_matching',
                'match_score': float(best_score),
                'minutiae_score': float(best_result['minutiae_score']),
                'correlation_score': float(best_result['correlation_score']),
                'pattern_score': float(best_result['pattern_score']),
                'confidence': best_result['confidence']
            }
        
        print(f"[VERIFICATION] ✗ NO MATCH! Best score {best_score:.4f} < threshold {match_threshold}")
        conn.close()
        return {
            'status': 'error',
            'message': 'Fingerprint not registered! (No matching fingerprint found in database)',
            'confidence': 'N/A',
            'best_match_score': float(best_score) if best_score > 0 else 0
        }
    
    except Exception as e:
        conn.close()
        return {
            'status': 'error',
            'message': f'Database error: {str(e)}',
            'confidence': 'N/A'
        }

def get_all_users():
    """
    Get all registered users with their fingerprint sample count.
    
    Returns:
        list: List of all users with metadata
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT u.id, u.name, u.blood_group, u.created_at, COUNT(fs.id) as sample_count
        FROM users u
        LEFT JOIN fingerprint_samples fs ON u.id = fs.user_id
        GROUP BY u.id
        ORDER BY u.name
    ''')
    
    users = cursor.fetchall()
    conn.close()
    
    return users

def delete_user_by_id(user_id):
    """
    Delete a user and ALL their fingerprint samples (cascade delete).
    
    Args:
        user_id (int): User's database ID
    
    Returns:
        dict: Status and message with deletion details
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # First, get user info and sample count before deletion
        cursor.execute('SELECT name FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        
        if not user:
            conn.close()
            return {
                'status': 'error',
                'message': 'User not found!'
            }
        
        user_name = user[0]
        
        # Get number of samples to delete
        cursor.execute('SELECT COUNT(*) FROM fingerprint_samples WHERE user_id = ?', (user_id,))
        sample_count = cursor.fetchone()[0]
        
        # Delete all fingerprint samples for this user
        cursor.execute('DELETE FROM fingerprint_samples WHERE user_id = ?', (user_id,))
        samples_deleted = cursor.rowcount
        
        # Delete the user (redundant but explicit)
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        user_deleted = cursor.rowcount
        
        if user_deleted > 0:
            conn.commit()
            conn.close()
            print(f"[DELETE] User '{user_name}' (ID: {user_id}) deleted with {samples_deleted} fingerprint samples")
            return {
                'status': 'success',
                'message': f'User "{user_name}" and {samples_deleted} fingerprint sample(s) deleted successfully!',
                'user_deleted': True,
                'samples_deleted': samples_deleted
            }
        else:
            conn.close()
            return {
                'status': 'error',
                'message': 'Failed to delete user!'
            }
    
    except Exception as e:
        conn.close()
        print(f"[ERROR] Failed to delete user {user_id}: {str(e)}")
        return {
            'status': 'error',
            'message': f'Database error: {str(e)}'
        }

def get_user_samples(user_id):
    """
    Get all fingerprint samples for a specific user.
    
    Args:
        user_id (int): User's database ID
    
    Returns:
        list: List of fingerprint samples
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT id, quality_score, captured_at FROM fingerprint_samples
            WHERE user_id = ?
            ORDER BY captured_at DESC
        ''', (user_id,))
        
        samples = cursor.fetchall()
        conn.close()
        return samples
    
    except Exception as e:
        conn.close()
        print(f"Error retrieving user samples: {str(e)}")
        return []

def delete_fingerprint_sample(sample_id):
    """
    Delete a specific fingerprint sample.
    
    Args:
        sample_id (int): Fingerprint sample ID
    
    Returns:
        dict: Status message
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('DELETE FROM fingerprint_samples WHERE id = ?', (sample_id,))
        
        if cursor.rowcount > 0:
            conn.commit()
            conn.close()
            return {
                'status': 'success',
                'message': 'Fingerprint sample deleted successfully!'
            }
        else:
            conn.close()
            return {
                'status': 'error',
                'message': 'Sample not found!'
            }
    
    except Exception as e:
        conn.close()
        return {
            'status': 'error',
            'message': f'Error: {str(e)}'
        }

if __name__ == '__main__':
    init_database()
