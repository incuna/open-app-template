from setuptools import setup, find_packages

import open_app


setup(
    name='django-app-build',
    packages=find_packages(),
    include_package_data=True,
    version=open_app.__version__,
    description='',
    long_description=open('README.rst').read(),
    author=open_app.__author__,
    author_email='admin@incuna.com',
    url='http://incuna.com/',
    install_requires=[],
    zip_safe=False,
)
