# TESTING GUIDE

This guide helps you test the Fingerprint Blood Group Detection System thoroughly.

## Pre-Testing Checklist

- [ ] Python 3.7+ installed
- [ ] Backend virtual environment activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Database initialized (`python database.py`)
- [ ] Backend server running (`python app.py`)
- [ ] Frontend accessible (index.html opened)
- [ ] Browser console open (F12)
- [ ] Test fingerprint images ready

## Test Fingerprint Images

### Option 1: Use Any Image as Test Fingerprint
Since this is a hash-based system (not real fingerprint recognition), you can use:
- Screenshots
- PNG/JPG images from your computer
- Generated images
- Any grayscale or color image

### Option 2: Download Sample Fingerprints
- [NIST Special Database 4](https://www.nist.gov/itl/iad/image-group/special-database-4-fingerprint-database)
- [FVC Fingerprint Databases](http://bias.csr.unibo.it/fvc2000/)
- [OpenSource Fingerprint Datasets](https://github.com/topics/fingerprint-dataset)

### Option 3: Create Test Images
- Draw a pattern in Paint/Photoshop
- Convert to grayscale
- Save as PNG or JPG
- Use for testing

## Test Cases

### TEST 1: API Status Check

**Objective**: Verify backend API is running

**Steps**:
1. Open browser
2. Visit: `http://localhost:5000/`
3. Should see JSON response with status: "success"

**Expected Result**:
```json
{
    "status": "success",
    "message": "Fingerprint Blood Group Detection API is running!",
    "version": "1.0.0"
}
```

**Pass Criteria**: ✅ JSON response received

---

### TEST 2: Home Page Load

**Objective**: Verify frontend loads correctly

**Steps**:
1. Open `frontend/index.html` in browser
2. Check page loads without errors
3. Check API status section updates
4. Check navigation menu

**Expected Result**:
- Page displays without errors
- API status shows "✅ API is running!"
- All buttons visible and clickable
- Navigation links work

**Pass Criteria**: ✅ Home page loads and displays correctly

---

### TEST 3: Navigation Between Pages

**Objective**: Test page navigation

**Steps**:
1. From Home page, click "Register Fingerprint"
2. Verify Register page loads
3. Click "Verify Fingerprint"
4. Verify Verify page loads
5. Click "Home" link
6. Verify Home page loads

**Expected Result**:
- All pages load correctly
- Navigation works in both directions
- URL changes appropriately
- Page content matches current page

**Pass Criteria**: ✅ All navigation working

---

### TEST 4: Register User - Valid Input

**Objective**: Successfully register a fingerprint

**Steps**:
1. Go to Register page
2. Enter Name: "Test User"
3. Select Blood Group: "O+"
4. Upload fingerprint image (use any image)
5. Click "Register"
6. Wait for response

**Expected Result**:
- Image preview shows
- Green success message appears
- Message: "User Test User registered successfully!"
- Form clears
- No console errors

**Pass Criteria**: ✅ User registered, success message shown

---

### TEST 5: Register User - Missing Name

**Objective**: Validate form - missing name field

**Steps**:
1. Go to Register page
2. Leave Name empty
3. Select Blood Group: "B+"
4. Upload fingerprint image
5. Click "Register"

**Expected Result**:
- Validation error: "Please enter your full name"
- Form not submitted
- No API call made

**Pass Criteria**: ✅ Form validation working

---

### TEST 6: Register User - Missing Blood Group

**Objective**: Validate form - missing blood group

**Steps**:
1. Go to Register page
2. Enter Name: "Test User 2"
3. Leave Blood Group as default
4. Upload fingerprint image
5. Click "Register"

**Expected Result**:
- Validation error: "Please select your blood group"
- Form not submitted

**Pass Criteria**: ✅ Validation working

---

### TEST 7: Register User - Missing Fingerprint

**Objective**: Validate form - missing fingerprint image

**Steps**:
1. Go to Register page
2. Enter Name: "Test User 3"
3. Select Blood Group: "A+"
4. Don't upload image
5. Click "Register"

**Expected Result**:
- Validation error: "Please upload a fingerprint image"
- Form not submitted

**Pass Criteria**: ✅ Validation working

---

### TEST 8: Image Preview - Register

**Objective**: Test image preview functionality

**Steps**:
1. Go to Register page
2. Click file upload area
3. Select an image
4. Observe preview area

**Expected Result**:
- Selected image appears in preview box
- Image displays correctly
- Remove (×) button appears
- Image preview is below file upload

**Pass Criteria**: ✅ Preview works correctly

---

### TEST 9: Remove Image Preview

**Objective**: Test remove image functionality

**Steps**:
1. Upload an image on Register page
2. Image preview appears
3. Click × button on preview
4. Observe preview area

**Expected Result**:
- Preview disappears
- Image input field clears
- Can upload another image

**Pass Criteria**: ✅ Remove functionality works

---

### TEST 10: Verify Fingerprint - Same Image

**Objective**: Verify a registered fingerprint

**Steps**:
1. Register user "John Doe" with blood group "O+" and fingerprint image X
2. Go to Verify page
3. Upload the exact same image X
4. Wait for response

**Expected Result**:
- Result box appears with green background
- Shows: "Fingerprint Verified!"
- Shows Name: "John Doe"
- Shows Blood Group: "O+" (highlighted)
- No console errors

**Pass Criteria**: ✅ Fingerprint verified successfully

---

### TEST 11: Verify Fingerprint - Unknown Image

**Objective**: Verify with unknown fingerprint

**Steps**:
1. Go to Verify page
2. Upload a different image (not registered)
3. Click "Verify Fingerprint"

**Expected Result**:
- Result box appears with red background
- Shows: "Verification Failed"
- Error message: "Fingerprint not found in database!"

**Pass Criteria**: ✅ Unknown fingerprint handled correctly

---

### TEST 12: Duplicate Fingerprint Registration

**Objective**: Test duplicate fingerprint prevention

**Steps**:
1. Register user "Alice" with image X and blood group "AB+"
2. Try to register "Bob" with the same image X
3. Click Register

**Expected Result**:
- Red error message appears
- Message: "Fingerprint already registered!"
- Database not updated with duplicate

**Pass Criteria**: ✅ Duplicate prevention working

---

### TEST 13: Different Images Different Hashes

**Objective**: Verify different images create different hashes

**Steps**:
1. Register user "User1" with image A and blood group "A+"
2. Register user "User2" with image B and blood group "B+"
3. Go to Verify page
4. Upload image A, should find User1
5. Upload image B, should find User2

**Expected Result**:
- Image A finds User1 with blood group A+
- Image B finds User2 with blood group B+
- Different images produce different hashes

**Pass Criteria**: ✅ Different images handled correctly

---

### TEST 14: Blood Group Selection

**Objective**: Test all blood groups

**Steps**:
1. Register 8 different users with each blood group:
   - O+, O-, A+, A-, B+, B-, AB+, AB-
2. Verify each registration succeeds

**Expected Result**:
- All 8 blood groups register successfully
- Each stores correct blood group in database

**Pass Criteria**: ✅ All blood groups working

---

### TEST 15: API Endpoint - /api/register

**Objective**: Test API directly with cURL

**Steps**:
```bash
# Create a test request
curl -X POST http://localhost:5000/api/register \
  -F "name=Test User" \
  -F "blood_group=O+" \
  -F "fingerprint_image=@path/to/image.jpg"
```

**Expected Result**:
```json
{"status": "success", "message": "User Test User registered successfully!"}
```

**Pass Criteria**: ✅ API endpoint working

---

### TEST 16: API Endpoint - /api/verify

**Objective**: Test verify API directly with cURL

**Steps**:
```bash
# Test with registered fingerprint
curl -X POST http://localhost:5000/api/verify \
  -F "fingerprint_image=@path/to/same/image.jpg"
```

**Expected Result**:
```json
{"status": "success", "name": "Test User", "blood_group": "O+"}
```

**Pass Criteria**: ✅ Verify API working

---

### TEST 17: API Endpoint - /api/users

**Objective**: Get all registered users

**Steps**:
```bash
curl http://localhost:5000/api/users
```

**Expected Result**:
```json
{
    "status": "success",
    "total_users": X,
    "users": [...]
}
```

**Pass Criteria**: ✅ Users list retrieved

---

### TEST 18: Large File Upload

**Objective**: Test file size limits

**Steps**:
1. Go to Register page
2. Try to upload a file > 16MB
3. Attempt to register

**Expected Result**:
- Either upload fails
- Or API returns error: "File too large"
- System handles gracefully

**Pass Criteria**: ✅ File size limit enforced

---

### TEST 19: Invalid Image File

**Objective**: Test with invalid image file

**Steps**:
1. Go to Register page
2. Try uploading a .txt or .doc file
3. Attempt to register

**Expected Result**:
- Validation fails or API returns error
- Error message: "Invalid image file!"
- Database not updated

**Pass Criteria**: ✅ Invalid files rejected

---

### TEST 20: CORS Error Handling

**Objective**: Test CORS error scenarios

**Steps**:
1. Stop the backend server
2. Try to register on frontend
3. Observe error message

**Expected Result**:
- Error message appears
- Message: "Failed to register! Make sure the backend API is running."
- User-friendly error handling

**Pass Criteria**: ✅ CORS errors handled gracefully

---

## Performance Tests

### TEST 21: Registration Time

**Objective**: Measure registration response time

**Steps**:
1. Open browser DevTools (F12)
2. Go to Network tab
3. Register a user
4. Check POST /api/register response time

**Expected Result**:
- Response time: 300-700ms (including image processing)
- Depends on image size and CPU

**Pass Criteria**: ✅ Response time acceptable

---

### TEST 22: Verification Time

**Objective**: Measure verification response time

**Steps**:
1. Open browser DevTools (F12)
2. Go to Network tab
3. Verify a fingerprint
4. Check POST /api/verify response time

**Expected Result**:
- Response time: 300-600ms
- Consistent with registration time

**Pass Criteria**: ✅ Performance acceptable

---

## Database Tests

### TEST 23: Database Persistence

**Objective**: Verify data persists across server restarts

**Steps**:
1. Register user "Persistent"
2. Stop backend server
3. Restart backend server
4. Verify same fingerprint
5. Should find registered user

**Expected Result**:
- User still registered after restart
- Data persists to database.db file

**Pass Criteria**: ✅ Database persistence working

---

### TEST 24: Concurrent Requests

**Objective**: Test system with multiple simultaneous requests

**Steps**:
1. Open 3 browser tabs
2. Register different users simultaneously
3. Then verify fingerprints simultaneously

**Expected Result**:
- All requests succeed
- No data corruption
- Each user registered correctly

**Pass Criteria**: ✅ Handles concurrent requests

---

## UI/UX Tests

### TEST 25: Responsive Design

**Objective**: Test UI on different screen sizes

**Steps**:
1. Open Register page
2. Resize browser to 480px (mobile)
3. Check form layout
4. Resize to 768px (tablet)
5. Resize to 1920px (desktop)

**Expected Result**:
- Form adapts to screen size
- All elements accessible
- No overlapping content
- Buttons clickable on all sizes

**Pass Criteria**: ✅ Responsive design working

---

### TEST 26: Form Button States

**Objective**: Test button disable/enable states

**Steps**:
1. Go to Register page
2. Click Register button
3. Watch button change state
4. Wait for response
5. Button re-enables

**Expected Result**:
- Button shows "Registering..." during request
- Button disabled during request
- Button re-enables after response

**Pass Criteria**: ✅ Button state management working

---

### TEST 27: Message Display

**Objective**: Test message visibility and clearing

**Steps**:
1. Register successfully
2. Observe success message
3. Register again (different fingerprint)
4. Observe previous message clears
5. New message appears

**Expected Result**:
- Messages display clearly
- Old messages clear before new ones
- Correct color (green for success, red for error)

**Pass Criteria**: ✅ Message handling working

---

## Security Tests

### TEST 28: SQL Injection Prevention

**Objective**: Test SQL injection protection

**Steps**:
1. Go to Register page
2. Enter name: `" OR "1"="1`
3. Try to register

**Expected Result**:
- Name stored as plain text
- No SQL injection possible
- Parameterized queries prevent this

**Pass Criteria**: ✅ SQL injection prevented

---

### TEST 29: XSS Prevention

**Objective**: Test XSS vulnerability protection

**Steps**:
1. Register with name: `<script>alert('XSS')</script>`
2. Verify the fingerprint
3. Check if script executes

**Expected Result**:
- Script does not execute
- Name displayed as plain text
- HTML properly escaped

**Pass Criteria**: ✅ XSS prevented

---

## Test Results Summary

Create a spreadsheet or document:

| Test # | Test Name | Status | Notes | Pass/Fail |
|--------|-----------|--------|-------|-----------|
| 1 | API Status | ✅ | | PASS |
| 2 | Home Page | ✅ | | PASS |
| ... | ... | ... | ... | ... |

## Conclusion

Once all tests pass, your system is ready for use!

---

**Testing Guide Complete**
