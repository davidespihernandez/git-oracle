CREATE OR REPLACE PROCEDURE export_data_to_python(p_table_name varchar2) IS
    l_sql VARCHAR2(4000);
    type t_fields is table of varchar2(255) index by binary_integer;
    pk_fields t_fields;
    all_fields t_fields;
  BEGIN
    select cc.column_name
    bulk collect into pk_fields
    from ALL_CONSTRAINTS c, ALL_CONS_COLUMNS cc
    where c.table_name=p_table_name and constraint_type='P' and cc.constraint_name=c.constraint_name
    order by cc.column_name;
    select c.column_name
    bulk collect into all_fields
    from ALL_TAB_COLUMNS c
    where c.table_name=p_table_name
    order by c.column_name;
    l_sql := 'DECLARE python varchar2(32000) := ''' || upper(p_table_name) || '={''; ' ||
             'k varchar2(32000); v varchar2(32000); ' ||
             'BEGIN FOR r IN (SELECT * FROM '||p_table_name|| ') LOOP ';

    l_sql := l_sql || ' k := ''''; ';
    l_sql := l_sql || ' v := ''''; ';
    -- construir la key del dict
    FOR i IN 1 .. pk_fields.COUNT loop
        l_sql := l_sql || ' k := k || r.' || pk_fields(i) || '; ';
    end loop;
    -- construir el value del dict
    FOR i IN 1 .. all_fields.COUNT loop
        l_sql := l_sql || ' v := v || ''"' || lower(all_fields(i)) || '": "'' || r.' || all_fields(i) || ' || ''", '';';
    end loop;
    --TODO
    l_sql := l_sql || 'python := python || ''"'' || k || ''": { '' || v || ''},''; ';

    l_sql := l_sql || '   END LOOP; '
             || 'python := python || '' }'';'
             || ' dbms_output.put_line(python); ' ||
             ' END; ';
    EXECUTE IMMEDIATE l_sql;
END;

-- uso
--begin
--    export_data_to_python('THING_TYPE');
--end;
