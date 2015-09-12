create table codes (
  code char(20) not null primary key
);

create table map (
  shorten char(255) not null primary key,
  url text not null
) default charset=utf8
