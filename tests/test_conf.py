"""Tests configuration and routes."""

import uuid
from passlib.hash import pbkdf2_sha256
from ..core import database
from ..app import app


def test_create_app():
    """Test create_app."""
    client = app.test_client()
    url = "/"

    response = client.get(url)
    expected = (
        b"<!doctype html>\n<html lang=en>\n<title>Redirecting...</title>\n"
        b"<h1>Redirecting...</h1>\n<p>You should be redirected automatically "
        b'to the target URL: <a href="/students/login">/students/login</a>. '
        b"If not, click the link.\n"
    )
    assert response.status_code == 302
    assert response.get_data() == expected


def test_get_login_page():
    """Test get login page."""
    client = app.test_client()

    url = "/user/login"

    response = client.get(url)
    assert response.status_code == 200


def test_login():
    """Test login."""
    database.users_collection.delete_many({"email": "dummy@dummy.com"})

    user = {
        "_id": uuid.uuid4().hex,
        "name": "dummy",
        "email": "dummy@dummy.com",
        "password": pbkdf2_sha256.hash("dummy"),
    }
    database.users_collection.insert_one(user)

    client = app.test_client()
    response = client.post(
        "/user/login",
        data={
            "email": "dummy@dummy.com",
            "password": "dummy",
        },
    )

    assert response.status_code == 200

    database.users_collection.delete_one({"_id": user["_id"]})


def test_get_home_page():
    """Test get home page."""
    database.users_collection.delete_many({"email": "dummy@dummy.com"})
    user = {
        "_id": uuid.uuid4().hex,
        "name": "dummy",
        "email": "dummy@dummy.com",
        "password": pbkdf2_sha256.hash("dummy"),
    }
    database.users_collection.insert_one(user)

    client = app.test_client()
    response = client.post(
        "/user/login",
        data={
            "email": "dummy@dummy.com",
            "password": "dummy",
        },
    )

    url = "/"
    response = client.get(url)
    assert response.status_code == 200
    database.users_collection.delete_one({"_id": user["_id"]})


def test_get_add_student():
    """Test get add student."""
    database.users_collection.delete_many({"email": "dummy@dummy.com"})

    user = {
        "_id": uuid.uuid4().hex,
        "name": "dummy",
        "email": "dummy@dummy.com",
        "password": pbkdf2_sha256.hash("dummy"),
    }
    database.users_collection.insert_one(user)

    client = app.test_client()
    response = client.post(
        "/user/login",
        data={
            "email": "dummy@dummy.com",
            "password": "dummy",
        },
    )

    url = "/students/upload"
    response = client.get(url)
    assert response.status_code == 200
    database.users_collection.delete_one({"_id": user["_id"]})


def test_get_add_employer():
    """Test get add employer."""
    database.users_collection.delete_many({"email": "dummy@dummy.com"})

    user = {
        "_id": uuid.uuid4().hex,
        "name": "dummy",
        "email": "dummy@dummy.com",
        "password": pbkdf2_sha256.hash("dummy"),
    }
    database.users_collection.insert_one(user)

    client = app.test_client()
    response = client.post(
        "/user/login",
        data={
            "email": "dummy@dummy.com",
            "password": "dummy",
        },
    )

    url = "/employers/add_employer"
    response = client.get(url)
    assert response.status_code == 200
    database.users_collection.delete_one({"_id": user["_id"]})


def test_get_change_deadline():
    """Test get change deadline."""
    database.users_collection.delete_many({"email": "dummy@dummy.com"})

    user = {
        "_id": uuid.uuid4().hex,
        "name": "dummy",
        "email": "dummy@dummy.com",
        "password": pbkdf2_sha256.hash("dummy"),
    }
    database.users_collection.insert_one(user)

    client = app.test_client()
    response = client.post(
        "/user/login",
        data={
            "email": "dummy@dummy.com",
            "password": "dummy",
        },
    )

    url = "/user/deadline"
    response = client.get(url)
    assert response.status_code == 200
    database.users_collection.delete_one({"_id": user["_id"]})


def test_get_search_student():
    """Test get search student."""
    user = {
        "_id": uuid.uuid4().hex,
        "name": "dummy",
        "email": "dummy@dummy.com",
        "password": pbkdf2_sha256.hash("dummy"),
    }
    database.users_collection.insert_one(user)

    client = app.test_client()
    response = client.post(
        "/user/login",
        data={
            "email": "dummy@dummy.com",
            "password": "dummy",
        },
    )

    url = "/students/search"
    response = client.get(url)
    assert response.status_code == 200
    database.users_collection.delete_one({"_id": user["_id"]})


def test_get_adding_skills():
    """Test get adding skills."""
    database.users_collection.delete_many({"email": "dummy@dummy.com"})
    user = {
        "_id": uuid.uuid4().hex,
        "name": "dummy",
        "email": "dummy@dummy.com",
        "password": pbkdf2_sha256.hash("dummy"),
    }
    database.users_collection.insert_one(user)

    client = app.test_client()
    response = client.post(
        "/user/login",
        data={
            "email": "dummy@dummy.com",
            "password": "dummy",
        },
    )

    url = "/skills/add_skill"
    response = client.get(url)
    assert response.status_code == 200
    database.users_collection.delete_one({"_id": user["_id"]})


def test_get_courses():
    """Test get courses."""
    database.users_collection.delete_many({"email": "dummy@dummy.com"})
    user = {
        "_id": uuid.uuid4().hex,
        "name": "dummy",
        "email": "dummy@dummy.com",
        "password": pbkdf2_sha256.hash("dummy"),
    }
    database.users_collection.insert_one(user)

    client = app.test_client()
    response = client.post(
        "/user/login",
        data={
            "email": "dummy@dummy.com",
            "password": "dummy",
        },
    )

    url = "/course_modules/add_module"
    response = client.get(url)
    assert response.status_code == 200
    database.users_collection.delete_one({"_id": user["_id"]})


def test_get_modules():
    """Test get modules."""
    database.users_collection.delete_many({"email": "dummy@dummy.com"})
    user = {
        "_id": uuid.uuid4().hex,
        "name": "dummy",
        "email": "dummy@dummy.com",
        "password": pbkdf2_sha256.hash("dummy"),
    }
    database.users_collection.insert_one(user)

    client = app.test_client()
    response = client.post(
        "/user/login",
        data={
            "email": "dummy@dummy.com",
            "password": "dummy",
        },
    )

    url = "/course_modules/add_module"
    response = client.get(url)
    assert response.status_code == 200
    database.users_collection.delete_one({"_id": user["_id"]})


def test_log_out():
    """Test log out."""
    user = {
        "_id": uuid.uuid4().hex,
        "name": "dummy",
        "email": "dummy@dummy.com",
        "password": pbkdf2_sha256.hash("dummy"),
    }
    database.users_collection.insert_one(user)

    client = app.test_client()
    response = client.post(
        "/user/login",
        data={
            "email": "dummy@dummy.com",
            "password": "dummy",
        },
    )

    client.get("/user/signout")
    url = "/user/login"

    client = app.test_client()
    response = client.post(
        "/user/login",
        data={
            "email": "",
            "password": "",
        },
    )

    response = client.get(url)
    assert response.status_code == 200
    # Could you not redirect to home page >:(

    database.users_collection.delete_one({"_id": user["_id"]})
