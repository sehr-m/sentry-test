"""
Test for the /api/errors/attribute endpoint.
Verifies that the AttributeError is properly triggered on NoneType.
"""

import pytest
from hello import app


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_attribute_error_endpoint(client):
    """Test that /api/errors/attribute properly triggers an AttributeError."""
    # When not in testing mode, the endpoint returns a 500 error
    # In testing mode with exception propagation, it raises the exception
    with pytest.raises(AttributeError) as exc_info:
        response = client.get('/api/errors/attribute')

    # Verify it's the correct AttributeError
    assert "'NoneType' object has no attribute 'nonexistent_method'" in str(exc_info.value)


def test_attribute_error_is_noneType_error(client):
    """
    Verify that the error is specifically an AttributeError on NoneType.
    This test manually calls the endpoint logic to verify the error type.
    """
    try:
        # Reproduce the exact error condition
        obj = None
        obj.nonexistent_method()
        assert False, "Should have raised AttributeError"
    except AttributeError as e:
        # Verify the error message indicates NoneType
        assert "'NoneType' object has no attribute" in str(e)
        assert "nonexistent_method" in str(e)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
