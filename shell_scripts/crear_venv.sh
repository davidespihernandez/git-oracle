#!/usr/bin/env bash
mkdir -p ~/.virtualenvs
cd ~/.virtualenvs
python3 -m venv oracleutils
. ~/.virtualenvs/oracleutils/bin/activate
cd "$(dirname "$0")"
pip install -r ../django/oracleutils/requirements.in