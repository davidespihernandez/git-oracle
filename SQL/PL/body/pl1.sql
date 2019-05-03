create or replace package body pl1 is
    function funcion1(param1 varchar2) return varchar2 is
    begin
        return 'pl1.function1';
    end funcion1;
    procedure procedure1(param1 varchar2) is
    begin
        dbms_output.put_line('Cambio');
        dbms_output.put_line('Cambio 2');
        dbms_output.put_line('Otro Cambio');
    end procedure1;
    function create_example_house(person_name_p varchar2, detail varchar2) return number is
        thing_id number;
        person_id number;
    begin
        begin
            select PERSON_ID into person_id from PERSON where NAME=person_name_p and ROWNUM=1;
        exception
            when no_data_found then
                select nvl(min(PERSON_ID), 0)-1 into person_id from PERSON;
                insert into PERSON(person_id, name) values(person_id, person_name_p);
        end;
        select nvl(min(THING_ID), 0)-1 into thing_id from THING;
        insert into THING(thing_id, person_id, date_created, thing_type_code)
            values(thing_id, person_id, sysdate, 'HOU');

        insert into HOUSE(thing_id, detail) values (thing_id, detail);

        return thing_id;
    end create_example_house;
end pl1;
