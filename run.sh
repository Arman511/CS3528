#!/bin/bash
FLASK_APP=app.py FLASK_ENV="development" FLASK_DEBUG=1 IS_TEST="False" OFFLINE="False" USE_RELOADER=1  flask run
