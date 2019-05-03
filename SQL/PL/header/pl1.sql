create or replace package pl1 is
  function funcion1(param1 varchar2) return varchar2;
  procedure procedure1(param1 varchar2);
  function create_example_house(person_name_p varchar2, detail varchar2) return number;
end pl1;
