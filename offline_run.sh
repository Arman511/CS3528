#!/bin/bash
sudo systemctl start mongod
FLASK_APP=app.py FLASK_ENV="development" FLASK_DEBUG=1 IS_TEST="False" OFFLINE="True" flask run