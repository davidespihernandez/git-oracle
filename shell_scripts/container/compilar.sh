#!/usr/bin/env bash
echo "Compilando cabeceras"
for f in /var/SQL/PL/header/*.sql; do
    echo "  " `basename ${f}`
    echo 'alter session set current_schema = C##LOCAL; ' >> /var/SQL/tmp.sql
    cat ${f} >> /var/SQL/tmp.sql
    echo / >> /var/SQL/tmp.sql
    echo exit | sqlplus / as sysdba @/var/SQL/tmp.sql >/dev/null
done
echo "Compilando bodies"
for f in /var/SQL/PL/body/*.sql; do
    echo "  " `basename ${f}`
    echo 'alter session set current_schema = C##LOCAL; ' > /var/SQL/tmp.sql
    cat ${f} >> /var/SQL/tmp.sql
    echo / >> /var/SQL/tmp.sql
    echo exit | sqlplus / as sysdba @/var/SQL/tmp.sql >/dev/null
done
echo "Recompilando todo"
echo "EXEC UTL_RECOMP.recomp_serial('C##LOCAL');" > /var/SQL/tmp.sql
echo exit | sqlplus / as sysdba @/var/SQL/tmp.sql >/dev/null
echo exit | sqlplus / as sysdba @/var/SQL/tmp.sql >/dev/null

echo "SET WRAP OFF;" > /var/SQL/tmp.sql
echo "set linesize 80;" >> /var/SQL/tmp.sql
echo "col object_type format a15;" >> /var/SQL/tmp.sql
echo "col object_name format a65;" >> /var/SQL/tmp.sql
echo "spool /var/SQL/errores.txt;" >> /var/SQL/tmp.sql
echo "select object_type, object_name from dba_objects where status='INVALID';" >> /var/SQL/tmp.sql
echo "spool off;" >> /var/SQL/tmp.sql
echo exit | sqlplus -S / as sysdba @/var/SQL/tmp.sql >/dev/null
if [ `cat /var/SQL/errores.txt|wc -l` -lt 5 ]
    then echo "Todo compilado sin errores!"
else
    echo "Hay errores de compilación!"
    cat /var/SQL/errores.txt
fi
