"""Tests for the course modules model."""

import os
import sys
import uuid
import pytest
import pandas as pd
from dotenv import load_dotenv
from flask import send_file
from core.database_mongo_manager import DatabaseMongoManager

os.environ["IS_TEST"] = "True"

load_dotenv()

@pytest.fixture()
def app():
    """Fixture to create a test client."""
    from ...app import app
    return app

@pytest.fixture()
def database():
    """Fixture to create a test database."""
    DATABASE = DatabaseMongoManager(os.getenv("MONGO_URI"), os.getenv("MONGO_DB_TEST", "cs3528_testing"))
    modules = DATABASE.get_all("modules")
    DATABASE.delete_all("modules")
    yield DATABASE
    for module in modules:
        DATABASE.insert("modules", module)
    DATABASE.connection.close()

@pytest.fixture()
def module_model():
    """Fixture to create a Module model instance."""
    from course_modules.models import Module
    return Module()

@pytest.fixture()
def sample_module(database):
    """Fixture to create a sample module."""
    yield {
        "_id": uuid.uuid4().hex,
        "module_id": "CS101",
        "module_name": "Introduction to CS",
        "module_description": "A basic CS course",
    }
    database.delete_all_by_field("modules", "module_id", "CS101")

def test_add_module(database, module_model, app):
    """Test add_module method."""
    sample_module = {
        "_id": uuid.uuid4().hex,
        "module_id": "CS101",
        "module_name": "Introduction to CS",
        "module_description": "A basic CS course",
    }
    with app.app_context():
        with app.test_request_context():
            response = module_model.add_module(sample_module)[0]
            assert response.status_code == 200
            assert database.get_one_by_id("modules", sample_module["_id"]) is not None
    database.delete_all_by_field("modules", "module_id", "CS101")

def test_get_module_by_id(database, module_model, app, sample_module):
    """Test get_module_by_id method."""
    database.insert("modules", sample_module)
    with app.app_context():
        with app.test_request_context():
            module = module_model.get_module_by_id(sample_module["module_id"])
            assert module is not None
            assert module["module_name"] == "Introduction to CS"

def test_get_module_name_by_id(database, module_model, app, sample_module):
    """Test get_module_name_by_id method."""
    database.insert("modules", sample_module)
    with app.app_context():
        with app.test_request_context():
            module_name = module_model.get_module_name_by_id(sample_module["module_id"])
            assert module_name == "Introduction to CS"

def test_update_module_by_uuid(database, module_model, app, sample_module):
    """Test update_module_by_uuid method."""
    database.insert("modules", sample_module)
    with app.app_context():
        with app.test_request_context():
            response = module_model.update_module_by_uuid(sample_module["_id"], "CS102", "Advanced CS", "Next level CS")[0]
            assert response.status_code == 200
            updated_module = database.get_one_by_id("modules", sample_module["_id"])
            assert updated_module["module_name"] == "Advanced CS"

def test_delete_all_modules(database, module_model, app, sample_module):
    """Test delete_all_modules method."""
    with app.app_context():
        with app.test_request_context():
            response = module_model.delete_all_modules()[0]
            assert response.status_code == 200
            assert database.get_all("modules") == []

def test_download_all_modules(database, module_model, app):
    """Test download_all_modules method."""
    sample_module = {
        "_id": uuid.uuid4().hex,
        "module_id": "CS101",
        "module_name": "Introduction to CS",
        "module_description": "A basic CS course",
    }
    database.insert("modules", sample_module)
    with app.app_context():
        with app.test_request_context():
            response = module_model.download_all_modules()
            assert response.mimetype == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

def test_upload_course_modules(database, module_model, app):
    """Test upload_course_modules method."""
    file_path = "/data_model_upload_template/course_modules_template.xlsx"
    data = pd.DataFrame([
        {"Module_id": "CS102", "Module_name": "Advanced CS", "Module_description": "Next level CS"}
    ])
    data.to_excel(file_path, index=False)
    with open(file_path, "rb") as file:
        with app.app_context():
            with app.test_request_context():
                response = module_model.upload_course_modules(file)
                assert response[1] == 200

def test_delete_module_by_id(database, module_model, app, sample_module):
    """Test delete_module_by_id method."""
    database.insert("modules", sample_module)
    with app.app_context():
        with app.test_request_context():
            response = module_model.delete_module_by_id(sample_module["module_id"])[0]
            assert response.status_code == 200
            assert database.get_one_by_id("modules", sample_module["_id"]) is None

def test_delete_module_by_uuid(database, module_model, app, sample_module):
    """Test delete_module_by_uuid method."""
    database.insert("modules", sample_module)
    with app.app_context():
        with app.test_request_context():
            response = module_model.delete_module_by_uuid(sample_module["_id"])[0]
            assert response.status_code == 200
            assert database.get_one_by_id("modules", sample_module["_id"]) is None

def test_get_module_by_uuid(database, module_model, app, sample_module):
    """Test get_module_by_uuid method."""
    database.insert("modules", sample_module)
    with app.app_context():
        with app.test_request_context():
            module = module_model.get_module_by_uuid(sample_module["_id"])
            assert module is not None
            assert module["module_name"] == "Introduction to CS"

def test_get_modules_map(database, module_model, app, sample_module):
    """Test get_modules_map method."""
    database.insert("modules", sample_module)
    with app.app_context():
        with app.test_request_context():
            modules_map = module_model.get_modules_map()
            assert sample_module["module_id"] in modules_map
            assert modules_map[sample_module["module_id"]]["module_name"] == "Introduction to CS"

def test_update_module_by_uuid(database, module_model, app, sample_module):
    """Test update_module_by_uuid method."""
    database.insert("modules", sample_module)
    with app.app_context():
        with app.test_request_context():
            response = module_model.update_module_by_uuid(sample_module["_id"], "CS102", "Advanced CS", "Next level CS")[0]
            assert response.status_code == 200
            updated_module = database.get_one_by_id("modules", sample_module["_id"])
            assert updated_module["module_name"] == "Advanced CS"

def test_reset_cache(database, module_model, app):
    """Test reset_cache method."""
    from course_modules.models import modules_cache
    sample_module = {
        "_id": uuid.uuid4().hex,
        "module_id": "CS101",
        "module_name": "Introduction to CS",
        "module_description": "A basic CS course",
    }
    database.insert("modules", sample_module)

    # Ensure the cache is reset
    with app.app_context():
        with app.test_request_context():
            module_model.reset_cache()
            assert modules_cache["data"] is not None
            assert len(modules_cache["data"]) > 0
            assert modules_cache["last_updated"] is not None

    # Clean up the database
    database.delete_all_by_field("modules", "module_id", "CS101")