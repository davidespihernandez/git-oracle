CREATE TABLE THING_TYPE
(
    ID INTEGER GENERATED BY DEFAULT AS IDENTITY (START WITH 1) NOT NULL PRIMARY KEY,
    NAME VARCHAR2(255) NOT NULL CONSTRAINT THING_TYPE_UK UNIQUE
);

CREATE TABLE PERSON
(
    ID INTEGER GENERATED BY DEFAULT AS IDENTITY (START WITH 1) NOT NULL PRIMARY KEY,
    NAME VARCHAR2(255) NOT NULL CONSTRAINT PERSON_UK UNIQUE
);


CREATE TABLE THING
(
    ID INTEGER GENERATED BY DEFAULT AS IDENTITY (START WITH 1) NOT NULL PRIMARY KEY,
    PERSON_ID INTEGER REFERENCES PERSON(ID),
    DATE_CREATED DATE NOT NULL,
    THING_TYPE_ID INTEGER REFERENCES THING_TYPE(ID)
);

CREATE INDEX THING_PERSON_IDX ON THING(PERSON_ID);

CREATE TABLE CAR
(
    ID INTEGER GENERATED BY DEFAULT AS IDENTITY (START WITH 1) NOT NULL PRIMARY KEY,
    THING_ID INTEGER REFERENCES THING(ID),
    DETAIL VARCHAR2(4000) NOT NULL
);

CREATE INDEX CAR_THING_IDX ON CAR(THING_ID);

CREATE TABLE HOUSE
(
    ID INTEGER GENERATED BY DEFAULT AS IDENTITY (START WITH 1) NOT NULL PRIMARY KEY,
    THING_ID INTEGER REFERENCES THING(ID),
    DETAIL VARCHAR2(4000) NOT NULL
);

CREATE INDEX HOUSE_THING_IDX ON HOUSE(THING_ID);