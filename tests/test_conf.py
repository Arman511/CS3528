"""Tests configuration and routes."""

import uuid
from passlib.hash import pbkdf2_sha256
from ..core import database
from ..app import app


def test_create_app():
    client = app.test_client()
    url = "/"

    response = client.get(url)
    expected = b'<!doctype html>\n<html lang=en>\n<title>Redirecting...</title>\n<h1>Redirecting...</h1>\n<p>You should be redirected automatically to the target URL: <a href="/students/login">/students/login</a>. If not, click the link.\n'
    assert response.status_code == 302
    assert response.get_data() == expected


def test_get_login_page():
    client = app.test_client()

    url = "/user/login"

    response = client.get(url)
    assert response.status_code == 200


def test_login():
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


def test_get_add_Student():

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


def test_get_Search_Student():

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


def test_Log_out():

    # Think i actully to inact log out the test if sign in page there

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
