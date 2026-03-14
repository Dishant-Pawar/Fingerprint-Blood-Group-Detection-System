# DATABASE SCHEMA AND DESIGN

## Overview
The system uses SQLite3 for storing user fingerprint hashes and blood group information. SQLite is chosen for its simplicity, no-setup requirement, and suitable for small to medium applications.

## Database File
- **Location**: `backend/database.db`
- **Type**: SQLite 3
- **Auto-initialization**: Database and tables are created automatically when `database.py` is executed

## Schema

### Table: users

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    blood_group TEXT NOT NULL,
    fingerprint_hash TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### Column Definitions

| Column | Type | Constraints | Description |
|--------|------|-----------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique identifier for each user |
| `name` | TEXT | NOT NULL | User's full name |
| `blood_group` | TEXT | NOT NULL | Blood group (A+, A-, B+, B-, AB+, AB-, O+, O-) |
| `fingerprint_hash` | TEXT | NOT NULL, UNIQUE | SHA256 hash of processed fingerprint image |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Registration timestamp |

## Data Constraints

### Unique Fingerprint
- Each fingerprint hash must be unique
- Prevents duplicate fingerprint registration
- If duplicate is attempted, database returns error

### Not Null Fields
- `name`: User must provide a name
- `blood_group`: User must select a blood group
- `fingerprint_hash`: Fingerprint must be processed and hashed

### Blood Group Values
Valid blood groups:
- `A+` (Positive)
- `A-` (Negative)
- `B+` (Positive)
- `B-` (Negative)
- `AB+` (Positive)
- `AB-` (Negative)
- `O+` (Positive)
- `O-` (Negative)

## Sample Data

```
id | name       | blood_group | fingerprint_hash                         | created_at
---|------------|-------------|----------------------------------------|---------------------
1  | John Doe   | O+          | a3f5b8c9d2e1f4g7h0i3j6k9l2m5n8o... | 2026-03-13 10:30:45
2  | Jane Smith | B-          | b4g6c9d3e2f5g8h1i4j7k0l3m6n9o1p... | 2026-03-13 11:45:30
```

## Sample Fingerprint Hash

SHA256 hash example:
```
a3f5b8c9d2e1f4g7h0i3j6k9l2m5n8opqrstuvwxyzabcdefghijklmnopqrst
```

- Length: 64 characters (hexadecimal)
- Generated from processed fingerprint image
- One-way function (cannot reverse to get original image)
- Deterministic (same image always produces same hash)

## Database Operations

### 1. Initialize Database
```python
from database import init_database
init_database()  # Creates database.db and tables
```

### 2. Register User
```python
from database import register_user
result = register_user('John Doe', 'O+', 'fingerprint_hash_here')
# Returns: {'status': 'success', 'message': '...'}
```

### 3. Verify Fingerprint
```python
from database import verify_fingerprint
result = verify_fingerprint('fingerprint_hash_here')
# Returns: {'status': 'success', 'name': '...', 'blood_group': '...'}
```

### 4. Get All Users
```python
from database import get_all_users
users = get_all_users()
# Returns: List of all user records
```

## Query Examples

### Get user by fingerprint hash
```sql
SELECT name, blood_group FROM users WHERE fingerprint_hash = ?
```

### Get all users with specific blood group
```sql
SELECT * FROM users WHERE blood_group = 'O+'
```

### Count total registered users
```sql
SELECT COUNT(*) as total FROM users
```

### Delete user by ID
```sql
DELETE FROM users WHERE id = ?
```

### Update blood group
```sql
UPDATE users SET blood_group = 'A+' WHERE id = ?
```

## Performance Considerations

### Indexing
For better performance with large datasets, consider adding indexes:

```sql
-- Index on fingerprint_hash for faster lookups
CREATE INDEX idx_fingerprint_hash ON users(fingerprint_hash)

-- Index on blood_group for filtering
CREATE INDEX idx_blood_group ON users(blood_group)
```

### Query Performance
- **Lookup by fingerprint**: ~O(1) with index
- **Insert new user**: ~O(1)
- **Select all users**: ~O(n) where n is number of users

## Backup & Recovery

### Backup Database
```bash
# Windows
copy backend\database.db backup_database.db

# macOS/Linux
cp backend/database.db backup_database.db
```

### Restore Database
```bash
# Windows
copy backup_database.db backend\database.db

# macOS/Linux
cp backup_database.db backend/database.db
```

## Data Privacy

### What's Stored
- ✅ User name (plain text)
- ✅ Blood group (plain text)
- ✅ Fingerprint hash (SHA256, one-way)
- ✅ Registration timestamp

### What's NOT Stored
- ❌ Original fingerprint image
- ❌ Raw biometric data
- ❌ Password (optional - not implemented)
- ❌ Personal identifiable info beyond name

## SQLite Advantages

1. **No Server Required**: Self-contained database file
2. **Easy Setup**: No installation or configuration
3. **Beginner Friendly**: Simple SQL queries
4. **Portable**: Copy database.db to move data
5. **Lightweight**: Minimal disk space usage
6. **Reliable**: ACID transactions supported

## SQLite Limitations

1. **Single User Access**: Not ideal for concurrent writes
2. **File Based**: Slower than client-server databases
3. **Scalability**: Best for <100GB of data
4. **No User Management**: No built-in security

## Migration to Other Databases

To migrate to MySQL, PostgreSQL, or MongoDB:

1. Modify database.py to use appropriate driver
2. Update connection strings
3. Run migration script
4. Update create table syntax

Example (PostgreSQL):
```python
import psycopg2

conn = psycopg2.connect(
    host='localhost',
    database='fingerprint_db',
    user='postgres',
    password='password'
)
```

## Database File Size

Approximate sizes:
- Empty database: ~20KB
- 100 users: ~50KB
- 1,000 users: ~100KB
- 10,000 users: ~500KB

## Maintenance

### Vacuum Database (optimize storage)
```sql
VACUUM;
```

### Check Database Integrity
```sql
PRAGMA integrity_check;
```

### Get Database Info
```sql
PRAGMA table_info(users);
PRAGMA database_list;
```

---

**Database Documentation Complete**
