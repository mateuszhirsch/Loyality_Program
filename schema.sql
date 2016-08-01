drop table if exists customers;
create table customers (
       id integer primary key autoincrement,
       name text not null,
       last_name text not null,
       date_of_birth date not null,
       points integer not null
);
drop table if exists new_customers;
create table new_customers (
       id integer not null,
       cycles integer not null
);
