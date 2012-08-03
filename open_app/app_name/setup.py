from setuptools import setup, find_packages

import {{ import_name }}


setup(
    name='{{ app_name }}',
    packages=find_packages(),
    include_package_data=True,
    version={{ import_name }}.__version__,
    description='',
    long_description=open('README.rst').read(),
    author={{ import_name }}.__author__,
    author_email='admin@incuna.com',
    url='http://incuna.com/',
    install_requires=[],
    zip_safe=False,
)

