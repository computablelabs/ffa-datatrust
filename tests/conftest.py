"""
Reusable client for API tests
"""

import pytest
import app

@pytest.fixture(scope="module")
def client():
    """
    Flask client for testing
    """
    app.app.config['TESTING'] = True
    app.initialize_app(app.app)
    client = app.app.test_client()
    yield client
