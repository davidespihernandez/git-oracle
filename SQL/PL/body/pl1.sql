create or replace package body pl1 is
  function funcion1(param1 varchar2) return varchar2 is
  begin
    return 'pl1.function1';
  end funcion1;
  procedure procedure1(param1 varchar2) is
  begin
    null;
  end procedure1;
end pl1;
