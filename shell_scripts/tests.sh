#!/usr/bin/env bash
. ~/.virtualenvs/oracleutils/bin/activate
cd ../django/oracleutils
python3 manage.py test module1 --testrunner=oracleutils.NoDbTestRunner
python3 manage.py test module2 --testrunner=oracleutils.NoDbTestRunner
