CREATE TABLE city (
  ci_cityKey decimal(3,0) NOT NULL,
  ci_name char(25) NOT NULL,
);

CREATE TABLE campus (
  ca_campuskey decimal(8, 0) NOT NULL,
  ca_cityKey decimal(3,0) NOT NULL,
  ca_name char(25) NOT NULL,
);

CREATE TABLE product (
  p_productKey decimal(10,0) NOT NULL,
  p_name varchar(55) NOT NULL,
  p_category char(10) NOT NULL,
  p_size decimal(2,0) NOT NULL,
  p_price decimal(6,2) NOT NULL,
);

CREATE TABLE store (
  s_storeKey decimal(8,0) NOT NULL,
  s_name char(25) NOT NULL,
  s_campusKey decimal(3,0) NOT NULL,
);

CREATE TABLE stock (
  ps_productKey decimal(10,0) NOT NULL,
  ps_storeKey decimal(8,0) NOT NULL,
  ps_quantity decimal(5,0) NOT NULL,
);

CREATE TABLE customer (
  c_custKey decimal(9,0) NOT NULL,
  c_name char(25) NOT NULL,
  c_address varchar(40) NOT NULL,
  c_cityKey decimal(3,0) NOT NULL,
  c_phone char(15) NOT NULL,
  c_balance decimal(7,2) NOT NULL,
);

CREATE TABLE transactions (
  t_transcationKey decimal(12,0) NOT NULL,
  t_custKey decimal(9,0) NOT NULL,
  t_storeKey decimal (8,0) NOT NULL,
  t_transcationstatus char(1) NOT NULL,
  t_totalpayment decimal(8,2) NOT NULL,
  t_transcationdate date NOT NULL,
);

CREATE TABLE transprod (
  tp_transcationKey decimal(12,0) NOT NULL,
  tp_productKey decimal(10,0) NOT NULL,
  tp_quantity decimal(2,0) NOT NULL,
);