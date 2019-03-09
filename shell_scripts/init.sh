#!/usr/bin/env bash
docker exec -it oracle-local bash -c "source /home/oracle/.bashrc; echo exit | sqlplus / as sysdba @/var/SQL/migrations/init.sql"
