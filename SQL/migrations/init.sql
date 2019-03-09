create user c##local identified by localpass;

grant dba to c##local;

grant create session to c##local with admin option;
