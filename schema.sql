drop table if exists customers;
create table customers (
       id integer primary key autoincrement,
       name text not null,
       last_name text not null,
       date_of_birth date not null,
       points integer not null
);
