create or replace package pl1 is
    function funcion1(param1 varchar2) return varchar2;
    procedure procedure1(param1 varchar2);
    function create_example_house(person_name_p varchar2, detail varchar2) return number;
    function different_types_args(varchar2_p varchar2, number_p number, boolean_p boolean, date_p date) return varchar2;
    function count_person_things(person_id_p number) return number;
end pl1;
