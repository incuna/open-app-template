SHELL := /bin/bash

release:
	python setup.py register sdist upload

test:
	django-admin.py test tests --settings={{ import_name }}.test_settings
