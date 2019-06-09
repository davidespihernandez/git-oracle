#!/usr/bin/env bash
echo "Export de la base de datos, sólo metadata"
expdp C##LOCAL/localpass schemas=C##LOCAL content=metadata_only dumpfile=export.dmp reuse_dumpfiles=YES
cp /u01/app/oracle/admin/ORCL/dpdump/export.dmp /var/SQL/export/
