contributing
------------

in order for a pull request to be merged, please make sure it meets the following criteria:

1. all unit tests pass for all supported versions of python and django.
2. every newly added line of code is exercised by at least one unit test.
3. all code is compliant with PEP8 style conventions.


development setup
-----------------
to setup a development environment, run the following commands::

  $ pip install -r dev_requirements.txt


unit testing
------------

to run the unit tests, run the following commands::

  $ cd test_app
  $ python manage.py test


demo testing
------------

to ensure the app behaves as expected, run the following::

  $ cd test_app
  $ python manage.py runserver

then, visit ``http://localhost:8000/`` in your browser and confirm it produces a valid CSV.


  
