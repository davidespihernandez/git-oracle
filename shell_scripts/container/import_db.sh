#!/usr/bin/env bash
echo "Import de la base de datos, el fichero debe estar en SQL/export/export.dmp"
cp /var/SQL/export/export.dmp /u01/app/oracle/admin/ORCL/dpdump/ 
impdp C##LOCAL/localpass schemas=C##LOCAL dumpfile=export.dmp   