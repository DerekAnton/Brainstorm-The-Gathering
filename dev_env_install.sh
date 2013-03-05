#!/bin/sh
pip install virtualenv
pip install virtualenvwrapper
mkvirtualenv test
pip install -r requirements.txt
python manage.py syncdb --noinput
python load_cards.py
python createadmin.py
python manage.py rebuild_index --noinput
