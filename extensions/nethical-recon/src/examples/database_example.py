#!/usr/bin/env python3
"""
Database Module Example
Demonstrates stain database storage across different backends

🗂️ FALA 6: STAIN DATABASE
"""

import os
import sys

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import ConnectionPool, PooledStore, StoreFactory, create_store

# Try to import weapons module, but make it optional
try:
    from weapons import CO2SilentMode, MarkerGun, OrangeTracer, RedTracer, WeaponMode

    WEAPONS_AVAILABLE = True
except ImportError:
    WEAPONS_AVAILABLE = False
    print("⚠️  Weapons module not available, skipping weapon integration example")


def print_section(title):
    """Print a section header"""
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}\n")


def example_1_basic_sqlite():
    """Example 1: Basic SQLite usage"""
    print_section("Example 1: Basic SQLite Usage")

    # Create SQLite store (default, no config needed)
    store = create_store()

    print("✅ Created SQLite store")
    print(f"   Backend: {store.get_backend_type().value}")

    # Connect and initialize
    if not store.connect():
        print("❌ Failed to connect")
        return

    print("✅ Connected to database")

    if not store.initialize_schema():
        print("❌ Failed to initialize schema")
        return

    print("✅ Schema initialized")

    # Create sample stain
    stain = {
        "tag_id": "MAL-example1-2025-12-15",
        "marker_type": "MALWARE",
        "color": "RED",
        "timestamp_first_seen": "2025-12-15T14:30:00Z",
        "timestamp_last_seen": "2025-12-15T14:30:00Z",
        "hit_count": 1,
        "weapon_used": "CO2_SILENT",
        "target": {"ip": "192.168.1.105", "hostname": "malicious-server.local", "file_hash": "a1b2c3d4e5f6..."},
        "forest_location": {"tree": "web-server-01", "branch": "nginx-worker", "leaf": "session-4521"},
        "stain": {
            "threat_score": 9.2,
            "confidence": 0.95,
            "evidence": ["Suspicious network activity", "Known malware signature"],
            "linked_tags": [],
        },
        "hunter_notes": "Detected during night patrol by owl",
        "detected_by": "owl",
        "status": "ACTIVE_THREAT",
    }

    # Save stain
    if store.save_stain(stain):
        print(f"✅ Saved stain: {stain['tag_id']}")
    else:
        print("❌ Failed to save stain")

    # Retrieve stain
    retrieved = store.get_stain("MAL-example1-2025-12-15")
    if retrieved:
        print(f"✅ Retrieved stain: {retrieved['tag_id']}")
        print(f"   Threat Score: {retrieved['stain']['threat_score']}")
        print(f"   Confidence: {retrieved['stain']['confidence']}")

    # Get statistics
    stats = store.get_statistics()
    print("\n📊 Database Statistics:")
    print(f"   Total stains: {stats.get('total_stains', 0)}")

    store.disconnect()
    print("\n✅ Disconnected from database")


def example_2_weapon_integration():
    """Example 2: Integration with MarkerGun"""
    print_section("Example 2: MarkerGun + Database Integration")

    if not WEAPONS_AVAILABLE:
        print("⚠️  Skipping - weapons module not available\n")
        return

    # Setup weapon
    gun = MarkerGun("Silent Marker")
    gun.register_mode(WeaponMode.CO2_SILENT, CO2SilentMode())
    gun.load_ammo(RedTracer())
    gun.load_ammo(OrangeTracer())
    gun.arm()
    gun.safety_off()

    print("✅ MarkerGun configured and armed")

    # Setup database
    store = create_store("sqlite", {"database": "weapon_stains.db"})
    store.connect()
    store.initialize_schema()

    print("✅ Database ready")

    # Fire at multiple targets and save to database
    targets = [
        {
            "ip": "192.168.1.101",
            "file_hash": "abc123...",
            "threat_score": 9.0,
            "confidence": 0.92,
            "threat_type": "MALWARE",
        },
        {"ip": "192.168.1.102", "threat_score": 7.5, "confidence": 0.85, "threat_type": "SUSPICIOUS_IP"},
        {
            "ip": "192.168.1.103",
            "file_hash": "def456...",
            "threat_score": 8.8,
            "confidence": 0.91,
            "threat_type": "MALWARE",
        },
    ]

    print(f"\n🎯 Firing at {len(targets)} targets...")

    saved_count = 0
    for target in targets:
        # Select appropriate ammo
        if target.get("threat_type") == "MALWARE":
            gun.select_ammo("RED")
        else:
            gun.select_ammo("ORANGE")

        # Fire!
        result = gun.fire(target)

        if result.get("hit"):
            print(f"   💥 Hit: {target.get('ip')} with {result['ammo_used']} tracer")

            # Save to database
            stain = result["stain"]
            if store.save_stain(stain):
                saved_count += 1
        else:
            print(f"   ❌ Miss: {target.get('ip')}")

    print(f"\n✅ Saved {saved_count}/{len(targets)} stains to database")

    # Query high-threat stains
    high_threats = store.get_stains_by_threat_score(min_score=8.0)
    print(f"\n🔴 High-threat stains (score >= 8.0): {len(high_threats)}")
    for stain in high_threats:
        print(f"   - {stain['tag_id']}: Score {stain['stain']['threat_score']}")

    # Get stains by type
    malware_stains = store.get_stains_by_type("MALWARE")
    print(f"\n🦠 Malware stains: {len(malware_stains)}")

    # Get statistics
    stats = store.get_statistics()
    print("\n📊 Database Statistics:")
    print(f"   Total stains: {stats.get('total_stains', 0)}")
    print(f"   By type: {stats.get('stains_by_type', {})}")
    print(f"   By color: {stats.get('stains_by_color', {})}")
    print(f"   High threats: {stats.get('high_threat_count', 0)}")
    print(f"   Avg threat score: {stats.get('avg_threat_score', 0.0)}")

    store.disconnect()
    print("\n✅ Example complete")


def example_3_query_operations():
    """Example 3: Advanced query operations"""
    print_section("Example 3: Advanced Query Operations")

    store = create_store()
    store.connect()
    store.initialize_schema()

    # Add sample data
    sample_stains = [
        {
            "tag_id": "MAL-query1-2025-12-15",
            "marker_type": "MALWARE",
            "color": "RED",
            "timestamp_first_seen": "2025-12-15T10:00:00Z",
            "timestamp_last_seen": "2025-12-15T10:00:00Z",
            "hit_count": 1,
            "weapon_used": "CO2_SILENT",
            "target": {"ip": "10.0.0.1"},
            "stain": {"threat_score": 9.5, "confidence": 0.98, "evidence": [], "linked_tags": []},
            "hunter_notes": "Critical malware detected",
            "detected_by": "falcon",
            "status": "ACTIVE_THREAT",
        },
        {
            "tag_id": "SIP-query2-2025-12-15",
            "marker_type": "SUSPICIOUS_IP",
            "color": "ORANGE",
            "timestamp_first_seen": "2025-12-15T11:00:00Z",
            "timestamp_last_seen": "2025-12-15T11:00:00Z",
            "hit_count": 1,
            "weapon_used": "PNEUMATIC",
            "target": {"ip": "10.0.0.2"},
            "stain": {"threat_score": 6.5, "confidence": 0.75, "evidence": [], "linked_tags": []},
            "hunter_notes": "Port scan activity",
            "detected_by": "owl",
            "status": "MONITORING",
        },
    ]

    print("📝 Adding sample stains...")
    for stain in sample_stains:
        store.save_stain(stain)

    print(f"✅ Added {len(sample_stains)} stains\n")

    # Query 1: Get all stains
    all_stains = store.get_all_stains()
    print(f"1️⃣ All stains: {len(all_stains)}")

    # Query 2: Get by type
    malware = store.get_stains_by_type("MALWARE")
    print(f"2️⃣ Malware stains: {len(malware)}")

    # Query 3: Get by color
    red_stains = store.get_stains_by_color("RED")
    print(f"3️⃣ Red (malware) markers: {len(red_stains)}")

    # Query 4: Get by IP
    ip_stains = store.get_stains_by_ip("10.0.0.1")
    print(f"4️⃣ Stains for IP 10.0.0.1: {len(ip_stains)}")

    # Query 5: Get by threat score
    critical = store.get_stains_by_threat_score(min_score=9.0)
    print(f"5️⃣ Critical threats (>= 9.0): {len(critical)}")

    # Query 6: Search
    results = store.search_stains("malware")
    print(f"6️⃣ Search for 'malware': {len(results)} results")

    # Query 7: Count with filters
    active_count = store.count_stains({"status": "ACTIVE_THREAT"})
    print(f"7️⃣ Active threats: {active_count}")

    # Query 8: Pagination
    page1 = store.get_all_stains(limit=10, offset=0)
    print(f"8️⃣ Page 1 (10 per page): {len(page1)} stains")

    store.disconnect()
    print("\n✅ Query examples complete")


def example_4_connection_pooling():
    """Example 4: Connection pooling"""
    print_section("Example 4: Connection Pooling")

    # Create connection pool
    pool = ConnectionPool(backend="sqlite", config={"database": "pooled_stains.db"}, pool_size=3, max_overflow=2)

    print("✅ Created connection pool")
    print(f"   Pool size: {pool.pool_size}")
    print(f"   Max overflow: {pool.max_overflow}")

    # Use pooled connections
    print("\n🔄 Using pooled connections...")

    for i in range(5):
        with PooledStore(pool) as store:
            store.initialize_schema()

            stain = {
                "tag_id": f"POOL-test{i}-2025-12-15",
                "marker_type": "MALWARE",
                "color": "RED",
                "timestamp_first_seen": "2025-12-15T12:00:00Z",
                "timestamp_last_seen": "2025-12-15T12:00:00Z",
                "hit_count": 1,
                "weapon_used": "CO2_SILENT",
                "target": {"ip": f"10.0.1.{i}"},
                "stain": {"threat_score": 8.0, "confidence": 0.9, "evidence": [], "linked_tags": []},
                "hunter_notes": f"Pool test {i}",
                "detected_by": "automated",
                "status": "ACTIVE_THREAT",
            }

            store.save_stain(stain)
            print(f"   ✓ Saved stain {i+1}/5")

    # Check pool statistics
    stats = pool.get_stats()
    print("\n📊 Pool Statistics:")
    print(f"   Backend: {stats['backend']}")
    print(f"   Current size: {stats['current_size']}")
    print(f"   Available: {stats['available']}")
    print(f"   In use: {stats['in_use']}")

    # Clean up
    pool.close_all()
    print("\n✅ Pool closed")


def example_5_store_factory():
    """Example 5: Using StoreFactory"""
    print_section("Example 5: Store Factory")

    # List available backends
    backends = StoreFactory.list_available_backends()
    print(f"📋 Available backends: {', '.join(backends)}\n")

    # Get backend information
    for backend in ["sqlite", "postgresql", "mysql"]:
        info = StoreFactory.get_backend_info(backend)
        print(f"🔹 {info['name']}")
        print(f"   Use case: {info['use_case']}")
        print(f"   Requires: {info['requires']}")
        print()

    # Create default store
    store = StoreFactory.create_default_store()
    print(f"✅ Created default store: {store.get_backend_type().value}")

    store.connect()
    store.initialize_schema()

    # Add a test stain
    stain = {
        "tag_id": "FACTORY-test-2025-12-15",
        "marker_type": "MALWARE",
        "color": "RED",
        "timestamp_first_seen": "2025-12-15T13:00:00Z",
        "timestamp_last_seen": "2025-12-15T13:00:00Z",
        "hit_count": 1,
        "weapon_used": "ELECTRIC",
        "target": {"ip": "10.0.2.1"},
        "stain": {"threat_score": 9.0, "confidence": 0.95, "evidence": [], "linked_tags": []},
        "hunter_notes": "Factory test stain",
        "detected_by": "eagle",
        "status": "ACTIVE_THREAT",
    }

    store.save_stain(stain)
    print("✅ Saved test stain")

    # Verify
    retrieved = store.get_stain("FACTORY-test-2025-12-15")
    if retrieved:
        print(f"✅ Verified: Retrieved {retrieved['tag_id']}")

    store.disconnect()
    print("\n✅ Factory example complete")


def example_6_context_manager():
    """Example 6: Using context managers"""
    print_section("Example 6: Context Manager Usage")

    print("💡 Using context manager for automatic cleanup...\n")

    # Use context manager
    with create_store("sqlite", {"database": "context_test.db"}) as store:
        store.initialize_schema()

        stain = {
            "tag_id": "CTX-test-2025-12-15",
            "marker_type": "EVIL_AI",
            "color": "PURPLE",
            "timestamp_first_seen": "2025-12-15T14:00:00Z",
            "timestamp_last_seen": "2025-12-15T14:00:00Z",
            "hit_count": 1,
            "weapon_used": "CO2_SILENT",
            "target": {"user_agent": "MaliciousBot/1.0"},
            "stain": {"threat_score": 7.5, "confidence": 0.88, "evidence": [], "linked_tags": []},
            "hunter_notes": "Context manager test",
            "detected_by": "falcon",
            "status": "ACTIVE_THREAT",
        }

        store.save_stain(stain)
        print(f"✅ Saved stain: {stain['tag_id']}")

        stats = store.get_statistics()
        print(f"✅ Database has {stats.get('total_stains', 0)} stains")

    # Connection automatically closed
    print("\n✅ Context manager automatically closed connection")


def main():
    """Run all examples"""
    print("\n" + "=" * 70)
    print("  🗂️ DATABASE MODULE EXAMPLES")
    print("  FALA 6: STAIN DATABASE")
    print("=" * 70)

    try:
        example_1_basic_sqlite()
        example_2_weapon_integration()
        example_3_query_operations()
        example_4_connection_pooling()
        example_5_store_factory()
        example_6_context_manager()

        print("\n" + "=" * 70)
        print("  ✅ ALL EXAMPLES COMPLETED SUCCESSFULLY")
        print("=" * 70 + "\n")

    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
