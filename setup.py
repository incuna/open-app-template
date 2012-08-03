from setuptools import setup, find_packages

import app_build


setup(
    name='django-app-build',
    packages=find_packages(),
    include_package_data=True,
    version=app_build.__version__,
    description='',
    long_description=open('README.rst').read(),
    author=app_build.__author__,
    author_email='admin@incuna.com',
    url='http://incuna.com/',
    install_requires=[],
    zip_safe=False,
)

