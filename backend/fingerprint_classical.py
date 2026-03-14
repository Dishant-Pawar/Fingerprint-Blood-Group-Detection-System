"""
Classical Fingerprint Verification System
Combines three matching methods:
1. Minutiae-Based Matching
2. Correlation-Based Matching
3. Pattern-Based Matching
"""

import cv2
import numpy as np
import hashlib
from PIL import Image
import io
import base64
from scipy import signal, ndimage
from scipy.ndimage import label, find_objects
from settings import IMAGE_SIZE, MAX_FEATURE_DISTANCE, MIN_MATCHES

# ==================== IMAGE VALIDATION ====================

def validate_fingerprint_image(image_data):
    """
    Validate that the uploaded file is a valid fingerprint image.
    Supports BMP, PNG, JPG formats.
    """
    try:
        # Get file extension
        if hasattr(image_data, 'filename'):
            filename = image_data.filename.lower()
            allowed_extensions = {'.bmp', '.png', '.jpg', '.jpeg', '.gif'}
            
            if not any(filename.endswith(ext) for ext in allowed_extensions):
                return False
        
        # Try to open and read the image
        image_bytes = image_data.read() if hasattr(image_data, 'read') else image_data
        image = Image.open(io.BytesIO(image_bytes))
        image_data.seek(0)  # Reset file pointer
        
        # Convert to numpy array
        img_array = np.array(image)
        
        # Check minimum size
        if img_array.shape[0] < 50 or img_array.shape[1] < 50:
            return False
        
        return True
    except:
        return False

# ==================== FINGERPRINT PREPROCESSING ====================

def preprocess_fingerprint(img_gray, target_size=IMAGE_SIZE):
    """
    Advanced preprocessing for fingerprint images.
    Optimized for handling variations: rotation, distortion, noise, different pressures.
    
    Steps:
    1. Resize to standard size
    2. Normalize intensity
    3. Apply CLAHE for contrast enhancement (more aggressive)
    4. Apply bilateral filtering (stronger noise reduction)
    5. Apply morphological operations
    6. Histogram equalization for robustness
    """
    # Resize to standard size
    img_resized = cv2.resize(img_gray, (target_size, target_size))
    
    # Normalize intensity
    img_normalized = cv2.normalize(img_resized, None, 0, 255, cv2.NORM_MINMAX)
    
    # CLAHE for contrast enhancement (more aggressive for better ridge visibility)
    clahe = cv2.createCLAHE(clipLimit=3.5, tileGridSize=(12, 12))
    img_enhanced = clahe.apply(img_normalized)
    
    # Histogram equalization for additional robustness
    img_equalized = cv2.equalizeHist(img_enhanced)
    
    # Bilateral filter to reduce noise while preserving edges
    img_filtered = cv2.bilateralFilter(img_equalized, 7, 85, 85)
    
    # Gaussian blur for additional smoothing
    img_blurred = cv2.GaussianBlur(img_filtered, (5, 5), 0)
    
    # Morphological operations (stronger noise removal)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    img_morph = cv2.morphologyEx(img_blurred, cv2.MORPH_CLOSE, kernel, iterations=2)
    
    # Additional opening to remove small noise
    img_morph = cv2.morphologyEx(img_morph, cv2.MORPH_OPEN, kernel, iterations=1)
    
    return img_morph


def binarize_fingerprint(img_gray, threshold=None):
    """
    Convert grayscale fingerprint to binary image.
    Uses automatic threshold calculation if not provided.
    """
    if threshold is None:
        # Use Otsu's method for automatic threshold
        _, binary = cv2.threshold(img_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    else:
        _, binary = cv2.threshold(img_gray, threshold, 255, cv2.THRESH_BINARY)
    
    return binary


def skeletonize_fingerprint(binary_img):
    """
    Convert binary fingerprint to skeleton (ridge map).
    Uses morphological thinning to extract ridge structure.
    Fallback method: Morphological erosion if ximgproc unavailable.
    """
    try:
        # Try using OpenCV's morphological skeleton (preferred)
        skeleton = cv2.ximgproc.thinning(binary_img, cv2.ximgproc.THINNING_GUOHALL)
        return skeleton
    except:
        pass  # Fall through to morphological method
    
    # Fallback: Use morphological operations
    # This is more robust if ximgproc module is not available
    skeleton = binary_img.copy()
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    
    # Simple morphological thinning: erosion with reconstruction
    for iteration in range(10):
        prev_skeleton = skeleton.copy()
        
        # Erosion step
        eroded = cv2.erode(skeleton, kernel, iterations=1)
        
        # Dilation step to reconstruct
        dilated = cv2.dilate(eroded, kernel, iterations=1)
        
        # Subtract to get the outline
        outline = cv2.subtract(skeleton, dilated)
        
        # Update skeleton
        skeleton = eroded
        
        # Check for convergence
        if np.array_equal(prev_skeleton, skeleton):
            break
    
    # Clean up small noise with morphological opening
    skeleton = cv2.morphologyEx(skeleton, cv2.MORPH_OPEN, kernel)
    
    return skeleton


# ==================== MINUTIAE EXTRACTION ====================

def extract_minutiae_points(skeleton_img):
    """
    Extract minutiae points (ridge endings and bifurcations) from skeleton.
    
    Minutiae types:
    - Ridge ending: pixel with 1 neighbor
    - Bifurcation: pixel with 3 neighbors
    - Branch/complex: pixel with more than 3 neighbors
    
    Returns:
        list: [(x, y, type), ...] where type is 'ending' or 'bifurcation'
    """
    minutiae = []
    
    h, w = skeleton_img.shape
    
    # Pad skeleton to avoid boundary issues
    padded = cv2.copyMakeBorder(skeleton_img, 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=0)
    
    for i in range(1, h + 1):
        for j in range(1, w + 1):
            if padded[i, j] > 0:  # Pixel is part of ridge
                # Count neighbors in 3x3 neighborhood
                neighborhood = padded[i-1:i+2, j-1:j+2]
                
                # Count non-zero neighbors (excluding center)
                neighbors = np.sum(neighborhood > 0) - 1
                
                if neighbors == 1:
                    # Ridge ending
                    minutiae.append((j-1, i-1, 'ending'))
                elif neighbors == 3:
                    # Bifurcation
                    minutiae.append((j-1, i-1, 'bifurcation'))
                elif neighbors > 3:
                    # Complex branch - treat as bifurcation
                    minutiae.append((j-1, i-1, 'bifurcation'))
    
    return minutiae


def compute_minutiae_features(minutiae_points):
    """
    Compute spatial and topological features of minutiae.
    
    Returns:
        dict: Dictionary with minutiae statistics
    """
    if not minutiae_points:
        return {
            'count': 0,
            'endings': 0,
            'bifurcations': 0,
            'density': 0,
            'distribution': None,
            'points': []
        }
    
    endings = sum(1 for _, _, t in minutiae_points if t == 'ending')
    bifurcations = sum(1 for _, _, t in minutiae_points if t == 'bifurcation')
    
    # Compute density (minutiae per unit area)
    points_array = np.array([(x, y) for x, y, _ in minutiae_points])
    
    if len(points_array) > 0:
        # Compute spatial distribution
        distribution = {
            'mean_x': np.mean(points_array[:, 0]),
            'mean_y': np.mean(points_array[:, 1]),
            'std_x': np.std(points_array[:, 0]),
            'std_y': np.std(points_array[:, 1]),
            'spread': np.linalg.norm(points_array.max(axis=0) - points_array.min(axis=0))
        }
    else:
        distribution = None
    
    return {
        'count': len(minutiae_points),
        'endings': endings,
        'bifurcations': bifurcations,
        'density': len(minutiae_points) / (IMAGE_SIZE * IMAGE_SIZE / 10000),  # per 100x100
        'distribution': distribution,
        'points': minutiae_points
    }


def minutiae_matching_score(minutiae1, minutiae2, tolerance=20):
    """
    Compute minutiae-based matching score.
    
    Algorithm:
    1. Match minutiae points within tolerance distance
    2. Verify type consistency (ending vs bifurcation)
    3. Compute match ratio
    
    Args:
        minutiae1: List of minutiae from input fingerprint
        minutiae2: List of minutiae from stored fingerprint
        tolerance: Distance tolerance in pixels (increased to 20 for handling rotation/distortion/noise)
    
    Returns:
        float: Matching score (0-1)
    """
    if not minutiae1 or not minutiae2:
        return 0.0
    
    points1 = np.array([(x, y) for x, y, _ in minutiae1])
    points2 = np.array([(x, y) for x, y, _ in minutiae2])
    
    # Find closest points
    matched = 0
    type_matches = 0
    
    for i, (p1, (x1, y1, t1)) in enumerate(zip(points1, minutiae1)):
        # Find nearest point in minutiae2
        distances = np.linalg.norm(points2 - p1, axis=1)
        
        if len(distances) > 0:
            min_dist = np.min(distances)
            nearest_idx = np.argmin(distances)
            
            if min_dist < tolerance:
                matched += 1
                
                # Check if types match
                x2, y2, t2 = minutiae2[nearest_idx]
                if t1 == t2:
                    type_matches += 1
    
    # Compute score: combination of match count and type consistency
    match_ratio = matched / max(len(minutiae1), len(minutiae2))
    type_ratio = type_matches / max(matched, 1)
    
    # Weight both factors (more lenient for distorted/rotated prints)
    # Prioritize spatial matching over type consistency for noisy images
    score = 0.7 * match_ratio + 0.3 * type_ratio
    
    return min(score, 1.0)


# ==================== PATTERN CLASSIFICATION ====================

def classify_fingerprint_pattern(img_gray):
    """
    Classify fingerprint pattern type: loop, whorl, or arch.
    
    Methods:
    1. Compute directional field (ridge orientation)
    2. Analyze topology and singularities
    3. Classify based on core and delta location
    
    Returns:
        dict: Pattern classification and confidence
    """
    h, w = img_gray.shape
    
    # Compute local ridge orientation using Sobel
    sobel_x = cv2.Sobel(img_gray, cv2.CV_32F, 1, 0, ksize=3)
    sobel_y = cv2.Sobel(img_gray, cv2.CV_32F, 0, 1, ksize=3)
    
    # Orientation field
    orientation = np.arctan2(sobel_y, sobel_x)
    
    # Compute coherence (ridge strength)
    coherence = np.sqrt(sobel_x**2 + sobel_y**2)
    coherence = cv2.normalize(coherence, None, 0, 255, cv2.NORM_MINMAX)
    
    # Apply Gaussian blur to smooth orientation field
    orientation_smooth = cv2.GaussianBlur(orientation, (31, 31), 0)
    
    # Analyze orientation variation to detect pattern type
    # Arch: low variation, ridges parallel
    # Loop: one singularity (core)
    # Whorl: multiple singularities (core and delta)
    
    # Compute orientation gradient (Laplacian)
    orientation_laplacian = cv2.Laplacian(orientation_smooth, cv2.CV_32F)
    
    # Sum of positive and negative curvatures
    positive_curvature = np.sum(orientation_laplacian > 0.1)
    negative_curvature = np.sum(orientation_laplacian < -0.1)
    
    total_pixels = h * w
    
    # Classification logic
    if positive_curvature < total_pixels * 0.05 and negative_curvature < total_pixels * 0.05:
        pattern_type = 'arch'
        confidence = 0.8
    elif abs(positive_curvature - negative_curvature) < total_pixels * 0.1:
        pattern_type = 'whorl'
        confidence = 0.75
    else:
        pattern_type = 'loop'
        confidence = 0.85
    
    return {
        'type': pattern_type,
        'confidence': confidence,
        'orientation': orientation,
        'coherence': coherence,
        'singularities': {
            'positive': int(positive_curvature),
            'negative': int(negative_curvature)
        }
    }


def pattern_matching_score(pattern1, pattern2, allow_arch_mismatch=False):
    """
    Compute pattern-based matching score.
    
    Args:
        pattern1: Pattern dict from input fingerprint
        pattern2: Pattern dict from stored fingerprint
        allow_arch_mismatch: Whether to allow arch to match with other patterns
    
    Returns:
        float: Matching score (0-1)
    """
    if pattern1 is None or pattern2 is None:
        return 0.5
    
    type1 = pattern1.get('type', 'unknown')
    type2 = pattern2.get('type', 'unknown')
    
    # Exact match
    if type1 == type2:
        return 0.95
    
    # Partial credit for similar patterns
    similar_pairs = [('loop', 'whorl'), ('whorl', 'loop')]
    if (type1, type2) in similar_pairs or (type2, type1) in similar_pairs:
        return 0.6
    
    # Arch is least likely to match
    if 'arch' in (type1, type2):
        return 0.2
    
    return 0.1


# ==================== CORRELATION-BASED MATCHING ====================

def align_fingerprints(img1, img2, max_shift=50):
    """
    Align two fingerprint images using phase correlation.
    
    Args:
        img1: Input fingerprint image
        img2: Stored fingerprint image
        max_shift: Maximum allowed shift in pixels
    
    Returns:
        tuple: (aligned_img2, shift_x, shift_y, correlation_peak)
    """
    # Resize img2 to match img1 if different
    if img1.shape != img2.shape:
        img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
    
    # Compute FFT
    f1 = np.fft.fft2(img1.astype(np.float32))
    f2 = np.fft.fft2(img2.astype(np.float32))
    
    # Cross-power spectrum
    cross_power = (f1 * np.conj(f2)) / (np.abs(f1 * np.conj(f2)) + 1e-10)
    
    # Inverse FFT to get phase correlation
    correlation = np.fft.ifft2(cross_power)
    correlation = np.abs(correlation)
    
    # Find peak
    peak_y, peak_x = np.unravel_index(np.argmax(correlation), correlation.shape)
    
    # Convert to shift
    h, w = img1.shape
    shift_y = peak_y if peak_y < h // 2 else peak_y - h
    shift_x = peak_x if peak_x < w // 2 else peak_x - w
    
    # Limit shift
    shift_x = np.clip(shift_x, -max_shift, max_shift)
    shift_y = np.clip(shift_y, -max_shift, max_shift)
    
    # Align img2
    M = np.float32([[1, 0, shift_x], [0, 1, shift_y]])
    aligned_img2 = cv2.warpAffine(img2, M, (w, h))
    
    # Compute correlation peak value
    correlation_peak = np.max(correlation) / np.max(correlation.shape)
    
    return aligned_img2, shift_x, shift_y, correlation_peak


def correlation_matching_score(img1, img2):
    """
    Compute correlation-based matching score using normalized cross-correlation.
    
    Algorithm:
    1. Preprocess both images
    2. Align using phase correlation
    3. Compute normalized cross-correlation
    4. Return similarity score
    
    Args:
        img1: Input fingerprint image
        img2: Stored fingerprint image
    
    Returns:
        float: Correlation matching score (0-1)
    """
    # Resize to same size
    if img1.shape != img2.shape:
        img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
    
    # Normalize images
    img1_norm = cv2.normalize(img1.astype(np.float32), None, 0, 1, cv2.NORM_MINMAX)
    img2_norm = cv2.normalize(img2.astype(np.float32), None, 0, 1, cv2.NORM_MINMAX)
    
    # Try alignment
    try:
        aligned_img2, _, _, _ = align_fingerprints(img1_norm * 255, img2_norm * 255)
        aligned_img2 = cv2.normalize(aligned_img2.astype(np.float32), None, 0, 1, cv2.NORM_MINMAX)
    except:
        aligned_img2 = img2_norm
    
    # Compute normalized cross-correlation
    # Using template matching for better results
    numerator = np.sum((img1_norm - np.mean(img1_norm)) * (aligned_img2 - np.mean(aligned_img2)))
    denominator = np.sqrt(
        np.sum((img1_norm - np.mean(img1_norm))**2) * 
        np.sum((aligned_img2 - np.mean(aligned_img2))**2)
    )
    
    if denominator == 0:
        ncc = 0
    else:
        ncc = numerator / denominator
    
    # Convert to 0-1 range
    correlation_score = max(0, ncc)
    
    return correlation_score


# ==================== COMBINED MATCHING ====================

def compute_combined_matching_score(
    minutiae_score, correlation_score, pattern_score,
    weights=None
):
    """
    Combine three matching scores with weighted average.
    
    Default weights:
    - Minutiae: 0.5 (most reliable)
    - Correlation: 0.3 (complementary)
    - Pattern: 0.2 (filtering)
    """
    if weights is None:
        weights = [0.5, 0.3, 0.2]
    
    combined_score = (
        weights[0] * minutiae_score +
        weights[1] * correlation_score +
        weights[2] * pattern_score
    )
    
    return min(combined_score, 1.0)


# ==================== FEATURE EXTRACTION ====================

def extract_classical_features(img_data):
    """
    Extract all classical fingerprint features.
    
    Returns:
        dict: Contains minutiae, pattern, and raw image data
    """
    try:
        # Read image
        image_bytes = img_data.read() if hasattr(img_data, 'read') else img_data
        image = Image.open(io.BytesIO(image_bytes))
        img_array = np.array(image)
        
        if img_array is None or img_array.size == 0:
            print("[FEATURE EXTRACT] Error: Empty image array")
            return None
        
        # Convert to grayscale
        try:
            if len(img_array.shape) == 3:
                img_gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                img_gray = img_array
        except Exception as e:
            print(f"[FEATURE EXTRACT] Grayscale conversion failed: {str(e)}")
            return None
        
        # Preprocess
        try:
            img_preprocessed = preprocess_fingerprint(img_gray, IMAGE_SIZE)
            if img_preprocessed is None or img_preprocessed.size == 0:
                print("[FEATURE EXTRACT] Preprocessing returned empty image")
                return None
        except Exception as e:
            print(f"[FEATURE EXTRACT] Preprocessing failed: {str(e)}")
            return None
        
        # Binarize
        try:
            binary = binarize_fingerprint(img_preprocessed)
            if binary is None or binary.size == 0:
                print("[FEATURE EXTRACT] Binarization returned empty image")
                return None
        except Exception as e:
            print(f"[FEATURE EXTRACT] Binarization failed: {str(e)}")
            return None
        
        # Skeletonize
        try:
            skeleton = skeletonize_fingerprint(binary)
            if skeleton is None or skeleton.size == 0:
                print("[FEATURE EXTRACT] Skeletonization returned empty image")
                return None
        except Exception as e:
            print(f"[FEATURE EXTRACT] Skeletonization failed: {str(e)}")
            return None
        
        # Extract minutiae
        try:
            minutiae = extract_minutiae_points(skeleton)
            minutiae_features = compute_minutiae_features(minutiae)
            if minutiae_features['count'] == 0:
                print("[FEATURE EXTRACT] Warning: No minutiae points found")
        except Exception as e:
            print(f"[FEATURE EXTRACT] Minutiae extraction failed: {str(e)}")
            return None
        
        # Classify pattern
        try:
            pattern = classify_fingerprint_pattern(img_preprocessed)
        except Exception as e:
            print(f"[FEATURE EXTRACT] Pattern classification failed: {str(e)}")
            return None
        
        # Compute image hash
        try:
            img_hash = hashlib.sha256(cv2.imencode('.png', img_preprocessed)[1]).hexdigest()
        except Exception as e:
            print(f"[FEATURE EXTRACT] Hash computation failed: {str(e)}")
            return None
        
        # Compute quality score
        try:
            quality = np.sum(skeleton > 0) / (IMAGE_SIZE * IMAGE_SIZE)
        except Exception as e:
            print(f"[FEATURE EXTRACT] Quality computation failed: {str(e)}")
            quality = 0.5
        
        print(f"[FEATURE EXTRACT] Success - Minutiae: {minutiae_features['count']}, Quality: {quality:.2%}")
        
        return {
            'minutiae': minutiae_features,
            'pattern': pattern,
            'image_hash': img_hash,
            'quality_score': float(quality),
            'preprocessed_image': img_preprocessed,
            'binary_image': binary,
            'skeleton_image': skeleton,
            'raw_image': img_gray
        }
    
    except Exception as e:
        print(f"[FEATURE EXTRACT] Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def match_fingerprints_classical(features1, features2, threshold=0.65):
    """
    Match two fingerprints using three classical methods.
    
    Args:
        features1: Input fingerprint features
        features2: Stored fingerprint features
        threshold: Minimum score for acceptance (0.65 = more lenient for variations like rotation/distortion)
    
    Returns:
        dict: Matching result with individual and combined scores
    """
    if features1 is None or features2 is None:
        return {
            'match': False,
            'score': 0.0,
            'minutiae_score': 0.0,
            'correlation_score': 0.0,
            'pattern_score': 0.0,
            'reason': 'Invalid features'
        }
    
    # Method 1: Minutiae-based matching
    minutiae_score = minutiae_matching_score(
        features1['minutiae']['points'],
        features2['minutiae']['points'],
        tolerance=15
    )
    
    # Method 2: Pattern-based matching
    pattern_score = pattern_matching_score(
        features1['pattern'],
        features2['pattern']
    )
    
    # Method 3: Correlation-based matching
    correlation_score = correlation_matching_score(
        features1['preprocessed_image'],
        features2['preprocessed_image']
    )
    
    # Combine scores
    final_score = compute_combined_matching_score(
        minutiae_score, correlation_score, pattern_score
    )
    
    # Decision
    match = final_score >= threshold
    
    return {
        'match': match,
        'score': float(final_score),
        'minutiae_score': float(minutiae_score),
        'correlation_score': float(correlation_score),
        'pattern_score': float(pattern_score),
        'threshold': threshold,
        'confidence': 'High' if final_score >= 0.85 else 'Medium' if final_score >= threshold else 'Low'
    }


# ==================== SERIALIZATION ====================

def serialize_classical_features(features):
    """Make features serializable for database storage."""
    if features is None:
        return None
    
    serializable = {
        'minutiae': {
            'count': features['minutiae']['count'],
            'endings': features['minutiae']['endings'],
            'bifurcations': features['minutiae']['bifurcations'],
            'density': features['minutiae']['density'],
            'distribution': features['minutiae']['distribution'],
            'points': features['minutiae']['points']  # List of tuples
        },
        'pattern': {
            'type': features['pattern']['type'],
            'confidence': float(features['pattern']['confidence']),
            'singularities': {
                'positive': int(features['pattern']['singularities']['positive']),
                'negative': int(features['pattern']['singularities']['negative'])
            }
        },
        'image_hash': features['image_hash'],
        'quality_score': float(features['quality_score'])
    }
    
    return serializable


def deserialize_classical_features(features_blob):
    """Restore features from database blob."""
    if features_blob is None:
        return None
    
    try:
        import pickle
        features = pickle.loads(features_blob)
        return features
    except Exception as e:
        print(f"Error deserializing features: {str(e)}")
        return None
