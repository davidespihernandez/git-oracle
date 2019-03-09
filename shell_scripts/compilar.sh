#!/usr/bin/env bash
docker exec -it oracle-local bash -c "source /home/oracle/.bashrc; chmod +x /var/shell_scripts/join_sql_files.sh"
docker exec -it oracle-local bash -c "source /home/oracle/.bashrc; /var/shell_scripts/join_sql_files.sh"
docker exec -it oracle-local bash -c "source /home/oracle/.bashrc; echo exit | sqlplus / as sysdba @/var/SQL/all_header.sql"
docker exec -it oracle-local bash -c "source /home/oracle/.bashrc; echo exit | sqlplus / as sysdba @/var/SQL/all_body.sql"
