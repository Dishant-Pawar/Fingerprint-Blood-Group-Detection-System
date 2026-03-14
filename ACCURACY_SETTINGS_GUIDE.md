# ⚙️ Accuracy Settings Guide

## Quick Start

To increase fingerprint matching accuracy, adjust these two main settings in `backend/settings.py`:

```python
# Setting 1: Match Threshold (0.0 to 1.0)
MATCH_THRESHOLD = 0.5  # Change this value

# Setting 2: Number of Feature Points (100 to 2000)
ORB_NFEATURES = 500  # Change this value
```

Then restart the backend server.

---

## Setting 1: MATCH_THRESHOLD

**What it does:** Minimum score required to accept a fingerprint match

**Valid range:** 0.0 to 1.0

**Examples:**
| Value | Behavior | Use Case |
|-------|----------|----------|
| 0.30 | Very lenient - accepts partial matches | Testing, accessibility |
| 0.50 | Balanced (default) | General applications |
| 0.70 | Strict - only very similar fingerprints | Medical records |
| 0.85 | Very strict - nearly perfect match | Forensics, legal |

**How it works:**
- Fingerprints are compared feature-by-feature
- A score of 0.0-1.0 is calculated (1.0 = perfect match)
- If score ≥ threshold → Fingerprint is accepted ✓
- If score < threshold → Fingerprint is rejected ✗

**Example:**
```
Verification fingerprint vs stored fingerprint:
- Calculated match score: 0.62
- Match threshold: 0.50
- Result: ACCEPTED ✓ (0.62 > 0.50)

If threshold was 0.70:
- Result: REJECTED ✗ (0.62 < 0.70)
```

---

## Setting 2: ORB_NFEATURES

**What it does:** Number of distinctive feature points to extract

**Valid range:** 100 to 2000

**Examples:**
| Value | Speed | Accuracy | Best For |
|-------|-------|----------|----------|
| 300 | Very fast | Good | Quick testing |
| 500 | Fast | Good | Default, balanced |
| 800 | Medium | Better | Medical use |
| 1200 | Slow | Excellent | High precision needed |
| 1500+ | Very slow | Maximum | Forensic analysis |

**How it works:**
- Extracts unique ridge patterns from fingerprint
- More features = more detailed comparison
- Processing time increases with feature count

**Processing time estimates:**
```
300 features:  ~30-50ms to extract, ~5-10ms to match
500 features:  ~50-80ms to extract, ~10-15ms to match
800 features:  ~80-120ms to extract, ~15-25ms to match
1500 features: ~150-200ms to extract, ~30-50ms to match
```

---

## Recommended Configurations

### 1. **Quick Testing** ⚡
```python
MATCH_THRESHOLD = 0.35
ORB_NFEATURES = 300
```
- Very fast matching
- Loose acceptance criteria
- Good for rapid prototyping

### 2. **General Use** ⚖️ (Default)
```python
MATCH_THRESHOLD = 0.50
ORB_NFEATURES = 500
```
- Good balance of speed and accuracy
- Works for most applications
- Recommended for first-time users

### 3. **Medical Records** 🏥
```python
MATCH_THRESHOLD = 0.65
ORB_NFEATURES = 800
```
- Higher accuracy for patient identification
- Slightly slower but more reliable
- Prevents wrong blood group retrieval

### 4. **Forensic Analysis** 🔐
```python
MATCH_THRESHOLD = 0.85
ORB_NFEATURES = 1500
```
- Maximum accuracy for legal evidence
- Slower processing acceptable
- Nearly perfect matches required

### 5. **Lenient Matching** 🔓
```python
MATCH_THRESHOLD = 0.30
ORB_NFEATURES = 400
```
- Accepts partial/rotated fingerprints
- Fast processing
- Higher false positive rate

---

## How to Change Settings

### Method 1: Edit settings.py (Recommended)

1. Open `backend/settings.py` in a text editor
2. Find the settings you want to change:
   ```python
   MATCH_THRESHOLD = 0.5
   ORB_NFEATURES = 500
   ```
3. Change the values
4. Save the file
5. Restart the backend server:
   ```bash
   cd D:\RFingerPrint\backend
   python app.py
   ```

### Method 2: Use Settings Dashboard

1. Go to `http://localhost:8000/settings.html`
2. Use sliders to adjust values
3. Click "Save Settings"
4. Follow instructions to edit backend/settings.py

---

## Troubleshooting

### Problem: Too many false positives (matching non-matching fingerprints)

**Solution:** Increase match threshold
```python
MATCH_THRESHOLD = 0.60  # or higher
ORB_NFEATURES = 600     # increase features
```

### Problem: Too many false negatives (rejecting valid fingerprints)

**Solution:** Decrease match threshold or increase features
```python
MATCH_THRESHOLD = 0.45  # or lower
ORB_NFEATURES = 700     # increase features
```

### Problem: System too slow

**Solution:** Reduce feature count (small sacrifice in accuracy)
```python
MATCH_THRESHOLD = 0.50
ORB_NFEATURES = 400  # faster extraction
```

### Problem: Low accuracy with rotated/compressed images

**Solution:** Increase feature count (ORB is rotation-invariant)
```python
ORB_NFEATURES = 1000  # more features = more robust
```

---

## Performance Tuning Guide

### For Speed (Fast Matching)
```python
MATCH_THRESHOLD = 0.4      # Fast to evaluate
ORB_NFEATURES = 300        # Quick extraction
```
**Time per verification:** ~100-150ms for 100 users

### For Accuracy (Reliable Matching)
```python
MATCH_THRESHOLD = 0.70     # Stricter evaluation
ORB_NFEATURES = 1000       # Detailed features
```
**Time per verification:** ~1-2 seconds for 100 users

### For Balance (Recommended Default)
```python
MATCH_THRESHOLD = 0.50     # Good balance
ORB_NFEATURES = 500        # Standard features
```
**Time per verification:** ~300-500ms for 100 users

---

## Technical Details

### What is MATCH_THRESHOLD?

The threshold is calculated from two metrics:

1. **Match Score** = (Matching Features) / (Total Features)
   - How many keypoints match between fingerprints
   
2. **Distance Score** = 1 - (Average Distance / 256)
   - Quality of the matches (lower distance = better)

**Final Score** = (Match Score + Distance Score) / 2

Example:
```
Fingerprint A: 500 features
Fingerprint B: 500 features
Matched: 350 features
Average distance: 20

Match Score = 350/500 = 0.70
Distance Score = 1 - (20/256) = 0.92
Final Score = (0.70 + 0.92) / 2 = 0.81

If MATCH_THRESHOLD = 0.50:
0.81 > 0.50 → ACCEPTED ✓
```

### What is ORB_NFEATURES?

ORB = Oriented FAST and Rotated BRIEF
- **FAST:** Quickly detects corners/edges (keypoints)
- **BRIEF:** Creates descriptors for each keypoint
- **Rotation-invariant:** Handles rotated fingerprints

The `nfeatures` parameter limits max keypoints extracted:
- Higher value = more keypoints = more detailed features
- Lower value = fewer keypoints = faster processing

---

## Testing Your Settings

### Test 1: Same Image
```
Register: fingerprint.jpg
Verify: fingerprint.jpg
Expected: Match (score ≈ 1.0)
```

### Test 2: Rotated Image
```
Register: fingerprint.jpg
Verify: fingerprint.jpg (rotated 20°)
Expected: Match (score ≈ 0.7-0.9)
```

### Test 3: Compressed Image
```
Register: fingerprint.png (original)
Verify: fingerprint.jpg (JPEG compressed)
Expected: Match (score ≈ 0.6-0.8)
```

### Test 4: Different Person
```
Register: person1_finger.jpg
Verify: person2_finger.jpg
Expected: NO match (score < 0.5)
```

---

## Advanced Settings (Optional)

In `settings.py`, you can also adjust:

```python
IMAGE_SIZE = 256  # Resize fingerprints to this size
MIN_MATCHES = 5   # Minimum matching features required
```

These rarely need adjustment but can help in specific cases:
- **Smaller IMAGE_SIZE:** Faster but less detail
- **Larger IMAGE_SIZE:** More detail but slower
- **Higher MIN_MATCHES:** Stricter matching

---

## Monitoring and Logging

Enable logging to see match scores:

```python
DEBUG_MODE = True
LOG_MATCH_SCORES = True
```

Then check the console output when verifying fingerprints to see:
- Number of matching features
- Match scores
- Which fingerprints were considered

---

## Summary

**To increase accuracy:**
1. Increase `MATCH_THRESHOLD` (stricter matching)
2. Increase `ORB_NFEATURES` (more detailed features)
3. Both changes slow down the system

**Trade-off:**
- Higher accuracy = slower speed
- Lower threshold = faster but less reliable

**Best practice:**
- Start with defaults (0.5 threshold, 500 features)
- Test and adjust based on results
- Use presets for common scenarios

---

## Questions?

Refer to [FINGERPRINT_VERIFICATION_GUIDE.md](FINGERPRINT_VERIFICATION_GUIDE.md) for more technical details about how the system works.
