#!/bin/bash

# source ./setup.sh #run when needed

#Run flask app
pip install --only-binary :all: greenlet
pip install --only-binary :all: Flask-SQLAlchemy
flask --app flaskr run --debug