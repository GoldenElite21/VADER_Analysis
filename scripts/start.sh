#!/bin/bash
python3 -m venv env;
. ./env/bin/activate;
pip install django;
django-admin startproject amazonreviews;

cd amazonreviews;
ls;

sudo apt install libmysqlclient-dev default-libmysqlclient-dev;
pip install wheel;
pip install mysqlclient;

#vi amazonreviews/settings.py
read -r -p "Have you made the appropriate changes to your settings.py? [y/N] " response
response=${response,,}    # tolower
if ! [[ "$response" =~ ^(yes|y)$ ]]
	exit 0;
fi

python manage.py createsuperuser;
python manage.py startapp amazonvader
python manage.py startapp main;
python manage.py runserver 0:8000;
