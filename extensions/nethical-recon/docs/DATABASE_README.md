# Database Module - Stain Storage

> *"Permanent storage for marked threats across multiple backends"*

🗂️ **FALA 6: STAIN DATABASE**

Multi-backend database support for flexible deployment scenarios - from local development to enterprise-scale cloud deployments.

---

## Overview

The database module provides a unified interface for storing and retrieving stain (threat marker) data across 10 different database backends. This allows Nethical Recon to adapt to any deployment scenario, from a single developer's laptop to enterprise-scale cloud infrastructure.

### Key Features

- **Unified Interface**: Single API works across all database backends
- **Multiple Backends**: Support for SQL, NoSQL, cache, and search engines
- **Connection Pooling**: Built-in connection pool management
- **Factory Pattern**: Easy instantiation and configuration
- **Schema Management**: Automatic schema initialization
- **Migration Ready**: Structured for future migration scripts
- **Production Ready**: SQLite, PostgreSQL, and MySQL fully implemented

---

## Supported Backends

### 🏠 Local Development

#### SQLite ✅ **Fully Implemented**
- **Use Case**: Single-user local development, testing, small deployments
- **Pros**: Zero configuration, file-based, perfect for getting started
- **Requires**: Built-in (no extra packages)
- **Status**: ✅ Production ready

### 🏢 Team/Enterprise

#### PostgreSQL ✅ **Fully Implemented**
- **Use Case**: Primary relational database for team deployments
- **Pros**: Advanced features (JSONB, full-text search), open-source, highly reliable
- **Requires**: `pip install psycopg2-binary`
- **Status**: ✅ Production ready

#### MySQL ✅ **Fully Implemented**
- **Use Case**: Web-scale applications, wide hosting support
- **Pros**: Proven scalability, large ecosystem, excellent for web apps
- **Requires**: `pip install mysql-connector-python`
- **Status**: ✅ Production ready

#### Microsoft SQL Server ⚠️ **Stub Implementation**
- **Use Case**: Enterprise Windows environments, .NET integration
- **Requires**: `pip install pyodbc`
- **Status**: ⚠️ Interface defined, implementation needed

#### Oracle Database ⚠️ **Stub Implementation**
- **Use Case**: Large enterprise, mission-critical financial systems
- **Requires**: `pip install cx_Oracle`
- **Status**: ⚠️ Interface defined, implementation needed

#### IBM Db2 ⚠️ **Stub Implementation**
- **Use Case**: Mainframe integration, legacy enterprise systems
- **Requires**: `pip install ibm_db`
- **Status**: ⚠️ Interface defined, implementation needed

### ☁️ Cloud/Analytics

#### Snowflake ⚠️ **Stub Implementation**
- **Use Case**: Analytics warehouse, large-scale data analysis and reporting
- **Requires**: `pip install snowflake-connector-python`
- **Status**: ⚠️ Interface defined, implementation needed

### 📦 NoSQL/Cache

#### MongoDB ⚠️ **Stub Implementation**
- **Use Case**: Flexible document storage for unstructured/semi-structured IOC data
- **Requires**: `pip install pymongo`
- **Status**: ⚠️ Interface defined, implementation needed

#### Redis ⚠️ **Stub Implementation**
- **Use Case**: High-speed caching layer for frequently accessed data
- **Requires**: `pip install redis`
- **Status**: ⚠️ Interface defined, implementation needed

### 🔍 Search

#### Elasticsearch ⚠️ **Stub Implementation**
- **Use Case**: Fast full-text IOC searches, log aggregation, threat hunting
- **Requires**: `pip install elasticsearch`
- **Status**: ⚠️ Interface defined, implementation needed

---

## Quick Start

### 1. Basic Usage with SQLite (Default)

```python
from database import create_store

# Create SQLite store (no configuration needed)
store = create_store()

# Connect and initialize
store.connect()
store.initialize_schema()

# Save a stain
stain = {
    'tag_id': 'MAL-abc123-2025-12-15',
    'marker_type': 'MALWARE',
    'color': 'RED',
    'timestamp_first_seen': '2025-12-15T14:30:00Z',
    'timestamp_last_seen': '2025-12-15T14:30:00Z',
    'hit_count': 1,
    'weapon_used': 'CO2_SILENT',
    'target': {'ip': '192.168.1.105', 'file_hash': 'abc123...'},
    'stain': {
        'threat_score': 9.2,
        'confidence': 0.95,
        'evidence': [],
        'linked_tags': []
    },
    'hunter_notes': 'Detected during night patrol',
    'detected_by': 'owl',
    'status': 'ACTIVE_THREAT'
}

store.save_stain(stain)

# Retrieve stain
retrieved = store.get_stain('MAL-abc123-2025-12-15')
print(retrieved)

# Get statistics
stats = store.get_statistics()
print(f"Total stains: {stats['total_stains']}")

# Disconnect
store.disconnect()
```

### 2. PostgreSQL Usage

```python
from database import create_store

# Create PostgreSQL store
config = {
    'host': 'localhost',
    'port': 5432,
    'database': 'nethical_recon',
    'user': 'hunter',
    'password': 'secure_password'
}

store = create_store('postgresql', config)

# Connect and initialize
store.connect()
store.initialize_schema()

# Use the store...
stains = store.get_all_stains(limit=10)

store.disconnect()
```

### 3. MySQL Usage

```python
from database import create_store

# Create MySQL store
config = {
    'host': 'localhost',
    'port': 3306,
    'database': 'nethical_recon',
    'user': 'hunter',
    'password': 'secure_password'
}

store = create_store('mysql', config)

# Use context manager for automatic connection management
with store:
    store.initialize_schema()
    
    # Query high-threat stains
    high_threats = store.get_stains_by_threat_score(min_score=8.0)
    print(f"Found {len(high_threats)} high-threat stains")
```

### 4. Using Store Factory

```python
from database import StoreFactory

# List available backends
backends = StoreFactory.list_available_backends()
print(f"Available: {backends}")

# Get backend information
info = StoreFactory.get_backend_info('postgresql')
print(f"PostgreSQL: {info['description']}")

# Create store using factory
store = StoreFactory.create_store('sqlite', {'database': 'threats.db'})
store.connect()
```

### 5. Connection Pooling

```python
from database import ConnectionPool, PooledStore

# Create connection pool
pool = ConnectionPool(
    backend='postgresql',
    config={'host': 'localhost', 'database': 'stains', 'user': 'hunter', 'password': 'pass'},
    pool_size=5,
    max_overflow=10
)

# Use pooled connections
with PooledStore(pool) as store:
    stains = store.get_all_stains(limit=100)
    
# Check pool statistics
stats = pool.get_stats()
print(f"Connections in use: {stats['in_use']}")

# Clean up
pool.close_all()
```

---

## API Reference

### BaseStore Interface

All database implementations inherit from `BaseStore` and implement the following methods:

#### Connection Management

```python
connect() -> bool
    """Establish database connection"""

disconnect() -> bool
    """Close database connection"""

initialize_schema() -> bool
    """Create tables, indexes, and other schema objects"""

is_connected() -> bool
    """Check if database is connected"""
```

#### CRUD Operations

```python
save_stain(stain: Dict[str, Any]) -> bool
    """Save or update a stain"""

get_stain(tag_id: str) -> Optional[Dict[str, Any]]
    """Retrieve a stain by tag ID"""

update_stain(tag_id: str, updates: Dict[str, Any]) -> bool
    """Update an existing stain"""

delete_stain(tag_id: str) -> bool
    """Delete a stain"""
```

#### Query Operations

```python
get_all_stains(limit: Optional[int] = None, offset: int = 0) -> List[Dict[str, Any]]
    """Get all stains with optional pagination"""

get_stains_by_type(marker_type: str, limit: Optional[int] = None) -> List[Dict[str, Any]]
    """Get stains filtered by marker type (MALWARE, EVIL_AI, etc.)"""

get_stains_by_color(color: str, limit: Optional[int] = None) -> List[Dict[str, Any]]
    """Get stains filtered by tracer color (RED, PURPLE, etc.)"""

get_stains_by_ip(ip: str) -> List[Dict[str, Any]]
    """Get stains associated with an IP address"""

get_stains_by_threat_score(min_score: float, max_score: float = 10.0) -> List[Dict[str, Any]]
    """Get stains within a threat score range"""

search_stains(query: str, fields: Optional[List[str]] = None) -> List[Dict[str, Any]]
    """Search stains using full-text search"""

count_stains(filters: Optional[Dict[str, Any]] = None) -> int
    """Count stains with optional filters"""

get_statistics() -> Dict[str, Any]
    """Get database statistics (total stains, by type, etc.)"""
```

---

## Database Schema

### Stains Table Structure

```sql
stains (
    tag_id                  TEXT/VARCHAR PRIMARY KEY,
    marker_type             TEXT/VARCHAR NOT NULL,
    color                   TEXT/VARCHAR NOT NULL,
    timestamp_first_seen    TIMESTAMP NOT NULL,
    timestamp_last_seen     TIMESTAMP NOT NULL,
    hit_count               INTEGER DEFAULT 1,
    weapon_used             TEXT/VARCHAR NOT NULL,
    target_data             JSON/JSONB NOT NULL,
    forest_location         JSON/JSONB,
    threat_score            FLOAT NOT NULL,
    confidence              FLOAT NOT NULL,
    evidence                JSON/JSONB,
    linked_tags             JSON/JSONB,
    hunter_notes            TEXT,
    detected_by             TEXT/VARCHAR,
    status                  TEXT/VARCHAR DEFAULT 'ACTIVE_THREAT',
    created_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### Indexes

- `idx_marker_type` on `marker_type`
- `idx_color` on `color`
- `idx_threat_score` on `threat_score`
- `idx_status` on `status`
- `idx_timestamp` on `timestamp_first_seen`
- GIN indexes on JSON columns (PostgreSQL)
- Full-text search indexes (PostgreSQL)

---

## Integration with Weapons

### Integrating Database with MarkerGun

```python
from weapons import MarkerGun, CO2SilentMode, RedTracer
from database import create_store

# Setup weapon
gun = MarkerGun("Silent Marker")
gun.register_mode('CO2_SILENT', CO2SilentMode())
gun.load_ammo(RedTracer())
gun.arm()
gun.safety_off()

# Setup database
store = create_store('sqlite', {'database': 'stains.db'})
store.connect()
store.initialize_schema()

# Fire and save
target = {
    'ip': '192.168.1.105',
    'file_hash': 'abc123...',
    'threat_score': 9.0,
    'confidence': 0.92
}

result = gun.fire(target)

if result.get('hit'):
    # Save stain to database
    stain = result['stain']
    store.save_stain(stain)
    print(f"✅ Stain saved to database: {stain['tag_id']}")

# Query stains
all_stains = store.get_all_stains()
print(f"Total stains in database: {len(all_stains)}")

store.disconnect()
```

---

## Configuration Examples

### config.yaml

```yaml
database:
  # Primary data store
  primary:
    backend: postgresql
    host: localhost
    port: 5432
    database: nethical_recon
    user: hunter
    password: ${DB_PASSWORD}  # Use environment variable
  
  # Cache layer (optional)
  cache:
    backend: redis
    host: localhost
    port: 6379
    ttl: 3600
  
  # Search backend (optional)
  search:
    backend: elasticsearch
    hosts:
      - http://localhost:9200
    index_prefix: nethical_
```

### Loading Configuration

```python
import yaml
import os
from database import create_store

# Load configuration
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Substitute environment variables
db_config = config['database']['primary'].copy()
db_config['password'] = os.environ.get('DB_PASSWORD', db_config['password'])

# Create store
store = create_store(db_config['backend'], db_config)
```

---

## Best Practices

### 1. Use Context Managers

```python
with create_store('sqlite') as store:
    store.initialize_schema()
    stains = store.get_all_stains()
    # Connection automatically closed
```

### 2. Handle Errors Gracefully

```python
try:
    store = create_store('postgresql', config)
    if not store.connect():
        print("Failed to connect")
        return
    
    store.initialize_schema()
    # Use store...
    
except Exception as e:
    print(f"Database error: {e}")
finally:
    if store.is_connected():
        store.disconnect()
```

### 3. Use Connection Pooling for High Load

```python
from database import ConnectionPool, PooledStore

pool = ConnectionPool('postgresql', config, pool_size=10)

def process_threat(threat_data):
    with PooledStore(pool) as store:
        store.save_stain(threat_data)

# Process threats in parallel threads
import concurrent.futures
with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
    executor.map(process_threat, threat_list)
```

### 4. Implement Caching for Hot Data

```python
from database import create_store

# Primary storage
primary = create_store('postgresql', pg_config)
primary.connect()

# Cache layer
cache = create_store('redis', redis_config)
cache.connect()

def get_stain_cached(tag_id):
    # Try cache first
    stain = cache.get_stain(tag_id)
    if stain:
        return stain
    
    # Fall back to primary
    stain = primary.get_stain(tag_id)
    if stain:
        cache.save_stain(stain)  # Cache for next time
    
    return stain
```

---

## Performance Considerations

### SQLite
- ✅ Great for: Local dev, testing, single-user
- ⚠️ Limitations: Single writer, not suitable for high concurrency
- 💡 Tip: Use WAL mode for better concurrency

### PostgreSQL
- ✅ Great for: Team deployments, complex queries, JSON operations
- ⚠️ Limitations: Requires separate server process
- 💡 Tip: Use JSONB for efficient JSON queries, enable connection pooling

### MySQL
- ✅ Great for: Web-scale applications, proven scalability
- ⚠️ Limitations: Less advanced JSON support than PostgreSQL
- 💡 Tip: Use InnoDB engine, configure appropriate buffer pool size

---

## Security Considerations

1. **Never commit credentials**: Use environment variables or secret management
2. **Use parameterized queries**: All implementations use parameter binding
3. **Limit permissions**: Database users should have minimal required privileges
4. **Encrypt connections**: Use SSL/TLS for database connections
5. **Regular backups**: Implement automated backup strategy
6. **Audit logging**: Enable database audit logs for compliance

---

## Troubleshooting

### Connection Issues

```python
# Test connection
from database import create_store

store = create_store('postgresql', config)
if not store.connect():
    print("Connection failed!")
    print("Check: host, port, credentials, firewall rules")
```

### Schema Issues

```python
# Re-initialize schema
store.connect()
if not store.initialize_schema():
    print("Schema initialization failed!")
    # Check database permissions
```

### Performance Issues

```python
# Check statistics
stats = store.get_statistics()
print(f"Total stains: {stats['total_stains']}")

# Use pagination for large result sets
stains = store.get_all_stains(limit=100, offset=0)

# Use specific queries instead of get_all_stains()
high_threats = store.get_stains_by_threat_score(min_score=8.0)
```

---

## Migration Guide

### From In-Memory to Database

```python
from weapons import MarkerGun
from database import create_store

# Old way: stains stored in MarkerGun
gun = MarkerGun()
# ... fire weapon ...
in_memory_stains = gun.get_all_stains()

# New way: migrate to database
store = create_store('sqlite', {'database': 'stains.db'})
store.connect()
store.initialize_schema()

# Migrate existing stains
for stain in in_memory_stains:
    store.save_stain(stain)

print(f"Migrated {len(in_memory_stains)} stains to database")
store.disconnect()
```

---

## Future Enhancements

- [ ] Complete MSSQL, Oracle, Db2 implementations
- [ ] Complete Snowflake implementation
- [ ] Complete MongoDB, Redis, Elasticsearch implementations
- [ ] Add database migration scripts
- [ ] Add STIX/MISP format export
- [ ] Add bulk operations for better performance
- [ ] Add async/await support for asyncio
- [ ] Add database replication support
- [ ] Add query builder for complex searches
- [ ] Add metrics and monitoring integration

---

## Examples

See `examples/database_example.py` for complete working examples.

---

## License

Part of Nethical Recon project. See main LICENSE file.

---

**Date**: December 15, 2025  
**Version**: 1.0.0  
**Status**: ✅ Core Implementation Complete

*"Once marked, forever tracked - across any database"*
