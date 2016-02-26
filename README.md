Django MoJ Template App Builder
===============================

Using the latest gov.uk template and elements, builds a python package
containing a Django app with required static assets and templates.

NB: *Do not* include this repository in your services directly, it is only
designed to create the python package that you then install.

Requirements
------------

* Ruby 2.2+, bundler 1.10+ and sass 3.4 (probably installed via rbenv)
* Python 3.4+
* npm 3.7+

Usage
-----

`./main.py build` – will download and build the Django app, see build folder

`./main.py publish` – will publish the Django app to PyPi

The published package is what you use in your services: `pip install django_moj_template` or 
add `django_moj_template` to your requirements.txt
