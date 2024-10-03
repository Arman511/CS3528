from flask import Flask, render_template
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import pymongo
from core.database import client
from _pytest.monkeypatch import MonkeyPatch

@pytest.fixture
def monkeypatch():
    mpatch = MonkeyPatch()
    yield mpatch
    mpatch.undo()



def test_ping_success():
    try:
        client.admin.command('ping')
        assert True, "Pinged your deployment. You successfully connected to MongoDB!"
    except Exception as e:
        pytest.fail(f"Unexpected error: {e}")