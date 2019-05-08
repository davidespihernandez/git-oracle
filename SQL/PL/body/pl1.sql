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
        thing_id  number;
        person_id number;
    begin
        begin
            select PERSON_ID into person_id from PERSON where NAME = person_name_p and ROWNUM = 1;
        exception
            when no_data_found then
                select nvl(min(PERSON_ID), 0) - 1 into person_id from PERSON;
                insert into PERSON(person_id, name) values (person_id, person_name_p);
        end;
        select nvl(min(THING_ID), 0) - 1 into thing_id from THING;
        insert into THING(thing_id, person_id, date_created, thing_type_code)
        values (thing_id, person_id, sysdate, 'HOU');

        insert into HOUSE(thing_id, detail) values (thing_id, detail);

        return thing_id;
    end create_example_house;
    function different_types_args(varchar2_p varchar2, number_p number, boolean_p boolean, date_p date) return varchar2 is
        result varchar2(255);
        boolean_string varchar2(20);
    begin
        boolean_string := 'TRUE';
        if not boolean_p then
            boolean_string := 'FALSE';
        end if;
        result := varchar2_p || '-' ||
                  to_char(number_p) || '-' ||
                  boolean_string || '-' ||
                  to_char(date_p, 'dd/mm/yyyy');
        return result;
    end different_types_args;
    function count_person_things(person_id_p number) return number is
        things number := 0;
    begin
        select count(*) into things
        from THING
        where PERSON_ID=person_id_p;
        return things;
    end count_person_things;
end pl1;
