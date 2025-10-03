def test_basic_import():
    """Test that we can import app modules"""
    try:
        from app.models.user import User
        from app.models.client import Client
        assert True
    except ImportError as e:
        assert False, f"Import failed: {e}"

def test_basic():
    """Basic test to verify pytest is working"""
    assert 1 + 1 == 2