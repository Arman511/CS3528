import pytest
from ..core import database




def test_ping_success():
    try:
        database.client.admin.command('ping')
        assert True, "Pinged your deployment. You successfully connected to MongoDB!"
    except Exception as e:
        pytest.fail(f"Unexpected error: {e}")