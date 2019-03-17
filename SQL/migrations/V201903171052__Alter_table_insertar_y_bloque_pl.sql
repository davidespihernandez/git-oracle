alter table tabla_ejemplo add fecha date;

begin
  insert into TABLA_EJEMPLO(CAMPO, FECHA) values ('EJEMPLO', sysdate);
exception
  when others then null;
end; /
