import os

from setuptools import setup

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

with open('README.md') as readme:
    README = readme.read()

setup(
    name='django-moj-template',
    version='0.1',
    author='Ministry of Justice Digital Services',
    url='https://github.com/ministryofjustice/django-moj-template',
    packages=['django_moj_template'],
    include_package_data=True,
    license='MIT',
    description='A Django app containing pre-built gov.uk template and elements',
    long_description=README,
    install_requires=['Django>=1.9'],
    classifiers=[
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: MoJ Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
    ],
)
