#!/usr/bin/env bash
for f in /var/SQL/PL/header/*.sql; do
    echo 'alter session set current_schema = C##LOCAL; ' > /var/SQL/tmp.sql
    cat ${f} >> /var/SQL/tmp.sql
    echo / >> /var/SQL/tmp.sql
    echo exit | sqlplus / as sysdba @/var/SQL/tmp.sql
done
for f in /var/SQL/PL/body/*.sql; do
    echo 'alter session set current_schema = C##LOCAL; ' > /var/SQL/tmp.sql
    cat ${f} >> /var/SQL/tmp.sql
    echo / >> /var/SQL/tmp.sql
    echo exit | sqlplus / as sysdba @/var/SQL/tmp.sql
done
echo "EXEC UTL_RECOMP.recomp_serial('C##LOCAL');" > /var/SQL/tmp.sql
echo exit | sqlplus / as sysdba @/var/SQL/tmp.sql
echo exit | sqlplus / as sysdba @/var/SQL/tmp.sql
