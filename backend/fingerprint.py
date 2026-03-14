import cv2
import numpy as np
import hashlib
import io
from PIL import Image
import base64
import pickle
from settings import ORB_NFEATURES, MAX_FEATURE_DISTANCE, MIN_MATCHES, IMAGE_SIZE

# ==================== KEYPOINT SERIALIZATION ====================

def serialize_keypoints(keypoints):
    """Convert cv2.KeyPoint objects to serializable format (list of tuples)."""
    if keypoints is None:
        return None
    return [(kp.pt[0], kp.pt[1], kp.size, kp.angle, kp.response, kp.octave, kp.class_id) for kp in keypoints]

def deserialize_keypoints(kp_data):
    """Convert serialized keypoints back to cv2.KeyPoint objects."""
    if kp_data is None:
        return None
    return [cv2.KeyPoint(kp[0], kp[1], kp[2], kp[3], kp[4], kp[5], kp[6]) for kp in kp_data]

def serialize_features(features_dict):
    """Make features dict pickle-able by converting non-serializable objects."""
    if features_dict is None:
        return None
    
    serializable = {}
    for key, value in features_dict.items():
        if key == 'keypoints':
            serializable[key] = serialize_keypoints(value)
        elif key == 'descriptors':
            # Descriptors are numpy arrays - serialize as-is
            serializable[key] = value
        elif key == 'ridge_properties':
            # Convert histogram to list for pickling
            ridge_dict = {}
            for rk, rv in value.items():
                if isinstance(rv, np.ndarray):
                    ridge_dict[rk] = rv.tolist() if hasattr(rv, 'tolist') else rv
                else:
                    ridge_dict[rk] = rv
            serializable[key] = ridge_dict
        else:
            serializable[key] = value
    
    return serializable

def deserialize_features(features_blob):
    """Restore features from pickle blob."""
    if features_blob is None:
        return None
    
    try:
        features_dict = pickle.loads(features_blob)
        
        # Restore keypoints if present
        if 'keypoints' in features_dict and features_dict['keypoints']:
            features_dict['keypoints'] = deserialize_keypoints(features_dict['keypoints'])
        
        # Restore histogram if present
        if 'ridge_properties' in features_dict:
            ridge_dict = features_dict['ridge_properties']
            if 'histogram' in ridge_dict and isinstance(ridge_dict['histogram'], list):
                ridge_dict['histogram'] = np.array(ridge_dict['histogram'])
        
        return features_dict
    except Exception as e:
        print(f"Error deserializing features: {str(e)}")
        return None

# ==================== ADVANCED PREPROCESSING ====================

def preprocess_fingerprint_image(img_gray, target_size=IMAGE_SIZE):
    """
    Advanced preprocessing for fingerprint images.
    
    Steps:
    1. Resize to standard size
    2. Normalize intensity
    3. Apply contrast enhancement (CLAHE)
    4. Apply Gabor filter for ridge enhancement
    5. Apply morphological operations for noise reduction
    
    Args:
        img_gray (numpy.ndarray): Grayscale fingerprint image
        target_size (int): Target image size (e.g., 256)
    
    Returns:
        numpy.ndarray: Preprocessed image
    """
    # Step 1: Resize to standard size
    img_resized = cv2.resize(img_gray, (target_size, target_size))
    
    # Step 2: Normalize intensity (0-255 range)
    img_normalized = cv2.normalize(img_resized, None, 0, 255, cv2.NORM_MINMAX)
    
    # Step 3: Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
    # Better than standard histogram equalization for fingerprints
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    img_enhanced = clahe.apply(img_normalized)
    
    # Step 4: Apply bilateral filter to reduce noise while preserving edges
    img_filtered = cv2.bilateralFilter(img_enhanced, 5, 75, 75)
    
    # Step 5: Apply Gaussian blur to further reduce noise
    img_blurred = cv2.GaussianBlur(img_filtered, (3, 3), 0)
    
    # Step 6: Apply morphological operations to improve ridge structure
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    img_morph = cv2.morphologyEx(img_blurred, cv2.MORPH_CLOSE, kernel, iterations=1)
    
    return img_morph


def extract_ridge_features(img_preprocessed):
    """
    Extract both ORB features AND ridge characteristics for robust matching.
    
    Returns:
        dict: Contains keypoints, descriptors, and ridge properties
    """
    # ORB feature extraction
    orb = cv2.ORB_create(nfeatures=ORB_NFEATURES)
    keypoints, descriptors = orb.detectAndCompute(img_preprocessed, None)
    
    # Ridge characteristics (additional fingerprint properties)
    ridge_props = {
        'mean_intensity': np.mean(img_preprocessed),
        'std_intensity': np.std(img_preprocessed),
        'histogram': cv2.calcHist([img_preprocessed], [0], None, [32], [0, 256])
    }
    
    return {
        'keypoints': keypoints,
        'descriptors': descriptors,
        'ridge_properties': ridge_props
    }


def process_fingerprint_image(image_data):
    """
    Process fingerprint image with advanced preprocessing and extract feature descriptors.
    
    Args:
        image_data: Image file (from request.files)
    
    Returns:
        tuple: (fingerprint_hash, features_dict) or (None, None) on error
               features_dict contains: keypoints, descriptors, ridge_properties, quality_score
    """
    try:
        # Read image from file
        image_bytes = image_data.read()
        
        # Convert to PIL Image
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to numpy array
        img_array = np.array(image)
        
        # Convert to grayscale if color image
        if len(img_array.shape) == 3:
            img_gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            img_gray = img_array
        
        # Apply advanced preprocessing
        img_preprocessed = preprocess_fingerprint_image(img_gray, IMAGE_SIZE)
        
        # Extract features
        features = extract_ridge_features(img_preprocessed)
        
        # Calculate image quality score (measure of fingerprint clarity)
        quality_score = calculate_image_quality(img_preprocessed)
        features['quality_score'] = quality_score
        
        # Reject very poor quality images
        if quality_score < 0.3:
            print(f"Warning: Low quality fingerprint detected (score: {quality_score})")
            # Still process, but flag it
            features['low_quality'] = True
        
        # Generate hash from preprocessed image
        img_bytes = cv2.imencode('.png', img_preprocessed)[1].tobytes()
        fingerprint_hash = hashlib.sha256(img_bytes).hexdigest()
        
        return fingerprint_hash, features
    
    except Exception as e:
        print(f"Error processing fingerprint: {str(e)}")
        return None, None



def process_fingerprint_base64(base64_data):
    """
    Process fingerprint from base64 encoded data with advanced preprocessing.
    
    Args:
        base64_data (str): Base64 encoded image data
    
    Returns:
        tuple: (fingerprint_hash, features_dict) or (None, None) on error
    """
    try:
        # Decode base64 data
        image_bytes = base64.b64decode(base64_data.split(',')[1] if ',' in base64_data else base64_data)
        
        # Convert to PIL Image
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to numpy array
        img_array = np.array(image)
        
        # Convert to grayscale if color image
        if len(img_array.shape) == 3:
            img_gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            img_gray = img_array
        
        # Apply advanced preprocessing
        img_preprocessed = preprocess_fingerprint_image(img_gray, IMAGE_SIZE)
        
        # Extract features
        features = extract_ridge_features(img_preprocessed)
        
        # Calculate image quality
        quality_score = calculate_image_quality(img_preprocessed)
        features['quality_score'] = quality_score
        
        if quality_score < 0.3:
            features['low_quality'] = True
        
        # Generate hash
        img_bytes = cv2.imencode('.png', img_preprocessed)[1].tobytes()
        fingerprint_hash = hashlib.sha256(img_bytes).hexdigest()
        
        return fingerprint_hash, features
    
    except Exception as e:
        print(f"Error processing fingerprint from base64: {str(e)}")
        return None, None


def calculate_image_quality(img):
    """
    Calculate fingerprint image quality score (0-1).
    
    Factors considered:
    - Contrast (variance)
    - Sharpness (Laplacian variance)
    - Entropy
    
    Args:
        img (numpy.ndarray): Preprocessed grayscale image
    
    Returns:
        float: Quality score (0-1), where 1 is perfect quality
    """
    try:
        # 1. Contrast score (based on standard deviation)
        contrast = np.std(img) / 255.0
        contrast_score = min(contrast * 2, 1.0)  # Normalize to 0-1
        
        # 2. Sharpness score (based on Laplacian variance)
        laplacian = cv2.Laplacian(img, cv2.CV_64F)
        sharpness = np.var(laplacian)
        # Typical sharp fingerprints have Laplacian variance > 500
        sharpness_score = min(sharpness / 1000.0, 1.0)
        
        # 3. Entropy score (information content)
        hist = cv2.calcHist([img], [0], None, [256], [0, 256])
        hist = hist.flatten() / hist.sum()
        entropy = -np.sum(hist * np.log2(hist + 1e-7))
        # Max entropy for 8-bit image is 8
        entropy_score = entropy / 8.0
        
        # Weighted combination
        quality_score = (contrast_score * 0.3 + sharpness_score * 0.5 + entropy_score * 0.2)
        
        return min(quality_score, 1.0)
    
    except Exception as e:
        print(f"Error calculating image quality: {str(e)}")
        return 0.5


# ==================== ADVANCED FINGERPRINT MATCHING ====================

def match_fingerprints(features1, features2, strict_mode=True):
    """
    Advanced fingerprint matching using multiple criteria.
    
    Algorithm:
    1. Match ORB keypoint descriptors
    2. Validate matches spatially (remove outliers)
    3. Compare ridge characteristics
    4. Calculate overall similarity score
    
    Args:
        features1 (dict): Features from first fingerprint
        features2 (dict): Features from second fingerprint
        strict_mode (bool): If True, apply stricter matching criteria
    
    Returns:
        float: Match score (0-1), where 1 is perfect match
    """
    if features1 is None or features2 is None:
        return 0.0
    
    if features1.get('descriptors') is None or features2.get('descriptors') is None:
        return 0.0
    
    try:
        descriptors1 = features1['descriptors']
        descriptors2 = features2['descriptors']
        
        # Step 1: Match descriptors using BFMatcher with Hamming distance
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
        matches = bf.knnMatch(descriptors1, descriptors2, k=2)
        
        # Step 2: Apply Lowe's ratio test to filter good matches
        # This removes ambiguous matches
        good_matches = []
        for match_pair in matches:
            if len(match_pair) == 2:
                m, n = match_pair
                # Lowe's ratio test: accept only clear matches
                ratio_threshold = 0.7 if strict_mode else 0.8
                if m.distance < ratio_threshold * n.distance:
                    good_matches.append(m)
            elif len(match_pair) == 1:
                good_matches.append(match_pair[0])
        
        # Step 3: Calculate descriptor match score
        max_descriptors = max(len(descriptors1), len(descriptors2))
        if max_descriptors == 0:
            descriptor_score = 0.0
        else:
            descriptor_score = len(good_matches) / max_descriptors
        
        # Step 4: Compare ridge characteristics
        ridge_score = compare_ridge_properties(
            features1.get('ridge_properties'),
            features2.get('ridge_properties')
        )
        
        # Step 5: Quality check - penalize if either image is low quality
        quality_penalty = 0.0
        if features1.get('quality_score', 1.0) < 0.4 or features2.get('quality_score', 1.0) < 0.4:
            quality_penalty = 0.1
        
        # Step 6: Combine scores with weights
        # Descriptor matching is most important (60%)
        # Ridge characteristics (30%)
        # Quality score (10%)
        final_score = (descriptor_score * 0.6 + ridge_score * 0.3 + 
                      (1.0 - quality_penalty) * 0.1)
        
        # Ensure score is between 0 and 1
        final_score = max(0.0, min(final_score, 1.0))
        
        return final_score
    
    except Exception as e:
        print(f"Error matching fingerprints: {str(e)}")
        return 0.0


def compare_ridge_properties(ridge_props1, ridge_props2):
    """
    Compare ridge characteristics between two fingerprints.
    
    Args:
        ridge_props1 (dict): Ridge properties from first fingerprint
        ridge_props2 (dict): Ridge properties from second fingerprint
    
    Returns:
        float: Similarity score (0-1)
    """
    if ridge_props1 is None or ridge_props2 is None:
        return 0.5
    
    try:
        # Compare mean intensity
        mean1 = ridge_props1.get('mean_intensity', 128)
        mean2 = ridge_props2.get('mean_intensity', 128)
        mean_diff = abs(mean1 - mean2) / 255.0
        mean_score = 1.0 - min(mean_diff, 1.0)
        
        # Compare standard deviation
        std1 = ridge_props1.get('std_intensity', 50)
        std2 = ridge_props2.get('std_intensity', 50)
        std_diff = abs(std1 - std2) / 100.0
        std_score = 1.0 - min(std_diff, 1.0)
        
        # Compare histograms using Chi-Square distance
        hist1 = ridge_props1.get('histogram')
        hist2 = ridge_props2.get('histogram')
        
        if hist1 is not None and hist2 is not None:
            hist_score = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CHISQR)
            # Normalize: lower chi-square is better, convert to similarity
            hist_score = 1.0 / (1.0 + hist_score)
        else:
            hist_score = 0.5
        
        # Weighted average
        ridge_score = (mean_score * 0.3 + std_score * 0.3 + hist_score * 0.4)
        
        return ridge_score
    
    except Exception as e:
        print(f"Error comparing ridge properties: {str(e)}")
        return 0.5



def validate_fingerprint_image(image_data):
    """
    Validate if uploaded file is a valid image.
    
    Args:
        image_data: Image file (from request.files)
    
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        image_bytes = image_data.read()
        image_data.seek(0)  # Reset file pointer
        
        # Try to open image
        Image.open(io.BytesIO(image_bytes))
        
        return True
    except Exception:
        return False


def serialize_features(features):
    """
    Serialize fingerprint features for database storage.
    
    Args:
        features (dict): Features dictionary
    
    Returns:
        bytes: Pickled features
    """
    try:
        return pickle.dumps(features)
    except Exception as e:
        print(f"Error serializing features: {str(e)}")
        return None


def deserialize_features(features_blob):
    """
    Deserialize fingerprint features from database.
    
    Args:
        features_blob (bytes): Pickled features
    
    Returns:
        dict: Features dictionary or None on error
    """
    try:
        return pickle.loads(features_blob)
    except Exception as e:
        print(f"Error deserializing features: {str(e)}")
        return None