#!/usr/bin/env bash
echo 'alter session set current_schema = C##LOCAL; ' > /var/SQL/all_header.sql
echo 'alter session set current_schema = C##LOCAL; ' > /var/SQL/all_body.sql
for f in /var/SQL/PL/header/*.sql; do (cat $f; echo '/') >> /var/SQL/all_header.sql; done
for f in /var/SQL/PL/body/*.sql; do (cat $f; echo '/') >> /var/SQL/all_body.sql; done
