from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
from settings import MATCH_THRESHOLD, STRICT_MODE

# Import custom modules
from database import (
    init_database, register_user, verify_fingerprint, get_all_users,
    delete_user_by_id, get_user_samples, delete_fingerprint_sample
)
from fingerprint_classical import (
    extract_classical_features, validate_fingerprint_image
)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize database on startup
init_database()

# ==================== API ENDPOINTS ====================

@app.route('/', methods=['GET'])
def home():
    """Home endpoint - API status check with version info."""
    return jsonify({
        'status': 'success',
        'message': 'Fingerprint Blood Group Detection API is running!',
        'version': '2.0.0',
        'features': [
            'Advanced preprocessing',
            'Multi-sample fingerprints',
            'High-accuracy matching',
            'Quality validation'
        ],
        'match_threshold': MATCH_THRESHOLD,
        'strict_mode': STRICT_MODE
    })

@app.route('/api/register', methods=['POST'])
def register():
    """
    Register a new user with fingerprint and blood group.
    Uses classical fingerprint matching methods.
    Supports adding multiple samples for the same user.
    """
    try:
        name = request.form.get('name')
        blood_group = request.form.get('blood_group')
        
        # Debug logging
        print(f"[REGISTER] Received - Name: {name}, Blood Group: {blood_group}")
        print(f"[REGISTER] Files in request: {request.files.keys()}")
        
        if not name or not blood_group:
            return jsonify({
                'status': 'error',
                'message': 'Name and blood group are required!'
            }), 400
        
        if 'fingerprint_image' not in request.files:
            return jsonify({
                'status': 'error',
                'message': 'Fingerprint image is required!'
            }), 400
        
        fingerprint_file = request.files['fingerprint_image']
        
        if fingerprint_file.filename == '':
            return jsonify({
                'status': 'error',
                'message': 'No fingerprint image selected!'
            }), 400
        
        if not validate_fingerprint_image(fingerprint_file):
            return jsonify({
                'status': 'error',
                'message': 'Invalid image file! Please upload a valid BMP, PNG, or JPG image.'
            }), 400
        
        # Process fingerprint using classical methods
        features = extract_classical_features(fingerprint_file)
        
        if features is None:
            return jsonify({
                'status': 'error',
                'message': 'Failed to process fingerprint! Image may be of poor quality.'
            }), 500
        
        # Check quality score
        quality_score = features.get('quality_score', 0)
        if quality_score < 0.1:
            return jsonify({
                'status': 'warning',
                'message': f'Fingerprint quality is very low ({quality_score:.2%}). Try a clearer image.',
                'quality_score': quality_score
            }), 400
        
        fingerprint_hash = features.get('image_hash')
        
        # Register user with features
        result = register_user(name, blood_group, fingerprint_hash, features)
        
        if result['status'] == 'success':
            return jsonify({
                **result,
                'quality_score': quality_score,
                'user_id': result.get('user_id'),
                'minutiae_count': features['minutiae']['count'],
                'pattern_type': features['pattern']['type'],
                'next_step': 'You can add more fingerprint samples for better accuracy'
            }), 201
        else:
            return jsonify(result), 400
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Server error: {str(e)}'
        }), 500

@app.route('/api/verify', methods=['POST'])
def verify():
    """
    Verify a fingerprint and retrieve blood group.
    Uses classical fingerprint matching with three methods:
    1. Minutiae-Based Matching
    2. Correlation-Based Matching
    3. Pattern-Based Matching
    """
    try:
        if 'fingerprint_image' not in request.files:
            return jsonify({
                'status': 'error',
                'message': 'Fingerprint image is required!'
            }), 400
        
        fingerprint_file = request.files['fingerprint_image']
        
        if fingerprint_file.filename == '':
            return jsonify({
                'status': 'error',
                'message': 'No fingerprint image selected!'
            }), 400
        
        if not validate_fingerprint_image(fingerprint_file):
            return jsonify({
                'status': 'error',
                'message': 'Invalid image file! Please upload a valid BMP, PNG, or JPG image.'
            }), 400
        
        # Process fingerprint using classical methods
        features = extract_classical_features(fingerprint_file)
        
        if features is None:
            return jsonify({
                'status': 'error',
                'message': 'Failed to process fingerprint! Image may be of poor quality.'
            }), 500
        
        # Check quality score
        quality_score = features.get('quality_score', 0)
        if quality_score < 0.05:
            return jsonify({
                'status': 'error',
                'message': f'Fingerprint quality is too low ({quality_score:.2%}). Please try again with a clearer image.',
                'quality_score': quality_score
            }), 400
        
        fingerprint_hash = features.get('image_hash')
        
        # Verify fingerprint using classical matching
        result = verify_fingerprint(fingerprint_hash, features, MATCH_THRESHOLD, STRICT_MODE)
        
        status_code = 200 if result['status'] == 'success' else 404
        
        # Add quality and feature info to response
        if features:
            result['verification_quality'] = quality_score
            result['minutiae_count'] = features['minutiae']['count']
            result['pattern_type'] = features['pattern']['type']
        
        return jsonify(result), status_code
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Server error: {str(e)}'
        }), 500

@app.route('/api/users', methods=['GET'])
def get_users():
    """Get all registered users with sample count."""
    try:
        users = get_all_users()
        users_list = []
        
        for user in users:
            users_list.append({
                'id': user['id'],
                'name': user['name'],
                'blood_group': user['blood_group'],
                'fingerprint_samples': user['sample_count'],
                'registered_at': user['created_at']
            })
        
        return jsonify({
            'status': 'success',
            'total_users': len(users_list),
            'users': users_list
        }), 200
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Server error: {str(e)}'
        }), 500

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user_details(user_id):
    """Get details of a specific user including fingerprint samples."""
    try:
        users = get_all_users()
        user = None
        for u in users:
            if u['id'] == user_id:
                user = u
                break
        
        if not user:
            return jsonify({
                'status': 'error',
                'message': 'User not found!'
            }), 404
        
        # Get samples for this user
        samples = get_user_samples(user_id)
        
        return jsonify({
            'status': 'success',
            'user': {
                'id': user['id'],
                'name': user['name'],
                'blood_group': user['blood_group'],
                'registered_at': user['created_at']
            },
            'fingerprint_samples': [
                {
                    'id': s['id'],
                    'quality_score': s['quality_score'],
                    'captured_at': s['captured_at']
                }
                for s in samples
            ],
            'total_samples': len(samples)
        }), 200
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Server error: {str(e)}'
        }), 500

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete a registered user and all their fingerprint samples."""
    try:
        result = delete_user_by_id(user_id)
        status_code = 200 if result['status'] == 'success' else 404
        return jsonify(result), status_code
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Server error: {str(e)}'
        }), 500

@app.route('/api/users/<int:user_id>/samples/<int:sample_id>', methods=['DELETE'])
def delete_sample(user_id, sample_id):
    """Delete a specific fingerprint sample from a user."""
    try:
        result = delete_fingerprint_sample(sample_id)
        status_code = 200 if result['status'] == 'success' else 404
        return jsonify(result), status_code
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Server error: {str(e)}'
        }), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        'status': 'error',
        'message': 'Endpoint not found!'
    }), 404

@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors."""
    return jsonify({
        'status': 'error',
        'message': 'Internal server error!'
    }), 500

# ==================== MAIN ====================

if __name__ == '__main__':
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=True
    )
