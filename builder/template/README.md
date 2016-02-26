Django MoJ Template
===================

A Django app containing pre-built gov.uk template and elements
to be used when building Ministry of Justice Django-based services.

Usage
-----

* Install the package `pip install django_moj_template` or add `django_moj_template` to your requirements.txt
* Add `django_moj_template` to `INSTALLED_APPS` in settings
* Add `django_moj_template.context_processors.moj_context` to `context_processors` list in the template settings
* See `django_moj_template/base.html` and `sample_project` for template context usage
* Optionally, add result of `django_moj_template.get_assets_src_path()` to sass import paths to include GOV.UK Elements in your builds
