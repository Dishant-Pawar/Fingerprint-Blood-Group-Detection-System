"""
Fingerprint Verification System Settings - IMPROVED VERSION
Optimized for reduced false positives and better accuracy
"""

# ==================== FINGERPRINT MATCHING SETTINGS ====================

# MATCH THRESHOLD: Minimum similarity score (0-1) required to accept a match
# NEW IMPROVED VALUES (based on advanced preprocessing & multi-sample verification):
#
# 0.70 = Moderate (tolerates image variations)
# 0.80 = High (RECOMMENDED - reduces false positives significantly)
# 0.90 = Very High (strict mode - nearly identical fingerprints only)
# 0.95 = Maximum (critical security applications)
MATCH_THRESHOLD = 0.80

# ==================== ORB FEATURE DETECTION ====================

# Number of features to extract from fingerprint
# IMPROVED: Higher feature count for better accuracy
# Range: 100-2000
ORB_NFEATURES = 1000

# ==================== MULTI-SAMPLE VERIFICATION ====================

# Minimum number of samples recommended during registration
RECOMMENDED_SAMPLES_PER_USER = 5

# Minimum consistency score between multiple samples (0-1)
MIN_CONSISTENCY_SCORE = 0.70

# ==================== ADVANCED IMAGE PROCESSING ====================

# Image size (256x256 is standard for fingerprint processing)
IMAGE_SIZE = 256

# CLAHE parameters for contrast enhancement
CLAHE_CLIP_LIMIT = 2.0
CLAHE_GRID_SIZE = 8

# Feature Matching Parameters
MIN_MATCHES = 10

# Lowe's ratio threshold for ambiguous match filtering
LOWE_RATIO_THRESHOLD = 0.7

# Distance threshold for feature matches (0-256)
MAX_FEATURE_DISTANCE = 256

# ==================== IMAGE QUALITY VALIDATION ====================

# Enable/disable image quality scoring
ENABLE_IMAGE_QUALITY_CHECK = True

# Minimum quality score (0-1) for acceptable fingerprint
MIN_IMAGE_QUALITY = 0.3

# Minimum image dimensions
MIN_IMAGE_WIDTH = 100
MIN_IMAGE_HEIGHT = 100

# ==================== ANTI-SPOOFING & VALIDATION ====================

# Strict mode: Apply stricter matching criteria
STRICT_MODE = True

# Reject verification if quality is inconsistent
REJECT_QUALITY_MISMATCH = True

# Require multi-sample consistency if available
REQUIRE_MULTI_SAMPLE_CONSISTENCY = True

# ==================== PERFORMANCE SETTINGS ====================

# Maximum processing time per fingerprint (seconds)
MAX_PROCESSING_TIME = 10.0

# Enable caching for repeated verifications
ENABLE_RESULT_CACHE = False
CACHE_TTL = 300

# ==================== LOGGING & DEBUGGING ====================

# Enable detailed logging
DEBUG_MODE = True

# Log match scores for analysis
LOG_MATCH_SCORES = True

# Log rejected fingerprints
LOG_REJECTED_FINGERPRINTS = True

# ==================== STARTUP MESSAGE ====================

print("""
╔════════════════════════════════════════════════════════════════╗
║  FINGERPRINT VERIFICATION SYSTEM - SETTINGS LOADED             ║
╠════════════════════════════════════════════════════════════════╣
║  Version: IMPROVED (Advanced Preprocessing + Multi-Sample)     ║
║  Match Threshold: {}                                      ║
║  ORB Features: {}                                         ║
║  Strict Mode: {}                                          ║
║  Multi-Sample Support: ENABLED                                 ║
║  Status: Ready for deployment                                  ║
╚════════════════════════════════════════════════════════════════╝
""".format(MATCH_THRESHOLD, ORB_NFEATURES, STRICT_MODE))
