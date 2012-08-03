Installation Notes
==================

Installing the Package
----------------------

From PyPI
~~~~~~~~~

.. code-block:: bash

    pip install {{ app_name }}


From source
~~~~~~~~~~~

.. code-block:: bash

    git clone git://github.com/incuna/{{ app_name }}.git
    cd {{ app_name }}
    python setup.py install

Setting up your Django
----------------------

Add ``{{ import_name }}`` to your ``INSTALLED_APPS``:

.. code-block:: python

    INSTALLED_APPS = (
        # ...
        '{{ import_name }}',
        # ...
    )
