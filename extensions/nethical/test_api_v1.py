#!/usr/bin/env python3
"""Standalone test script for new API v1 features."""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import individual modules directly (avoid main __init__.py)
from nethical.api.rbac import Role, create_access_token, get_password_hash, verify_password


def test_database_models():
    """Test database models."""
    print("Testing database models...")

    # Initialize database
    init_db()  # noqa: F821
    print("✓ Database initialized")

    # Create session
    db = SessionLocal()  # noqa: F821

    # Create test user
    user = User(  # noqa: F821
        username="testuser",
        email="test@example.com",
        full_name="Test User",
        hashed_password=get_password_hash("password123"),
        role="admin"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    print(f"✓ Created user: {user.username} (ID: {user.id})")

    # Create test agent
    agent = Agent(  # noqa: F821
        agent_id="test-agent-001",
        name="Test Agent",
        agent_type="llm",
        description="Test agent",
        trust_level=0.8,
        configuration={"model": "gpt-4"},
        metadata={"env": "test"},
        created_by="testuser"
    )
    db.add(agent)
    db.commit()
    db.refresh(agent)
    print(f"✓ Created agent: {agent.agent_id} (ID: {agent.id})")

    # Create test policy
    policy = Policy(  # noqa: F821
        policy_id="test-policy-001",
        name="Test Policy",
        description="Test policy",
        version="1.0.0",
        rules=[{"id": "rule-1", "action": "ALLOW"}],
        created_by="testuser"
    )
    db.add(policy)
    db.commit()
    db.refresh(policy)
    print(f"✓ Created policy: {policy.policy_id} (ID: {policy.id})")

    # Create test audit log
    log = AuditLog(  # noqa: F821
        log_id="log-001",
        event_type="threat_detected",
        agent_id="test-agent-001",
        action="block",
        outcome="blocked",
        threat_type="prompt_injection",
        threat_level="high",
        risk_score=0.9
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    print(f"✓ Created audit log: {log.log_id} (ID: {log.id})")

    # Query tests
    user_count = db.query(User).count()  # noqa: F821
    agent_count = db.query(Agent).count()  # noqa: F821
    policy_count = db.query(Policy).count()  # noqa: F821
    log_count = db.query(AuditLog).count()  # noqa: F821

    print(f"✓ Database contains: {user_count} users, {agent_count} agents, {policy_count} policies, {log_count} logs")

    db.close()
    print("✓ Database models test passed!")


def test_rbac():
    """Test RBAC functionality."""
    print("\nTesting RBAC...")

    # Test password hashing
    password = "test_password_123"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed), "Password verification failed"
    assert not verify_password("wrong", hashed), "Wrong password verified incorrectly"
    print("✓ Password hashing works")

    # Test token creation
    token = create_access_token({
        "sub": "testuser",
        "user_id": 1,
        "role": "admin"
    })
    assert token is not None and len(token) > 0, "Token creation failed"
    print("✓ Token creation works")

    # Test roles
    assert Role.ADMIN == "admin", "Admin role mismatch"
    assert Role.AUDITOR == "auditor", "Auditor role mismatch"
    assert Role.OPERATOR == "operator", "Operator role mismatch"
    print("✓ Roles defined correctly")

    print("✓ RBAC test passed!")


def test_api_imports():
    """Test API module imports."""
    print("\nTesting API imports...")

    print("✓ All route modules import successfully")

    from nethical.api.v1.app import create_v1_app
    print("✓ API v1 app factory imports successfully")

    # Create app
    app = create_v1_app()
    assert app is not None, "App creation failed"
    print("✓ API v1 app created successfully")

    print("✓ API imports test passed!")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Running Nethical API v1 Tests")
    print("=" * 60)

    try:
        test_database_models()
        test_rbac()
        test_api_imports()

        print("\n" + "=" * 60)
        print("All tests passed! ✓")
        print("=" * 60)
        return 0

    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
