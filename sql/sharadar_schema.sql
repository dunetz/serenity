-- Database generated with pgModeler (PostgreSQL Database Modeler).
-- pgModeler  version: 0.9.3-beta
-- PostgreSQL version: 12.0
-- Project Site: pgmodeler.io
-- Model Author: ---

-- object: sharadar | type: ROLE --
-- DROP ROLE IF EXISTS sharadar;
CREATE ROLE sharadar WITH 
	LOGIN
	ENCRYPTED PASSWORD 'sharadardb';
-- ddl-end --


-- Database creation must be done outside a multicommand file.
-- These commands were put in this file only as a convenience.
-- -- object: sharadar | type: DATABASE --
-- -- DROP DATABASE IF EXISTS sharadar;
-- CREATE DATABASE sharadar;
-- -- ddl-end --
-- 

-- object: sharadar | type: SCHEMA --
-- DROP SCHEMA IF EXISTS sharadar CASCADE;
CREATE SCHEMA sharadar;
-- ddl-end --
ALTER SCHEMA sharadar OWNER TO postgres;
-- ddl-end --

SET search_path TO pg_catalog,public,sharadar;
-- ddl-end --

-- object: sharadar.indicator_seq | type: SEQUENCE --
-- DROP SEQUENCE IF EXISTS sharadar.indicator_seq CASCADE;
CREATE SEQUENCE sharadar.indicator_seq
	INCREMENT BY 1
	MINVALUE 0
	MAXVALUE 2147483647
	START WITH 1
	CACHE 1
	NO CYCLE
	OWNED BY NONE;
-- ddl-end --
ALTER SEQUENCE sharadar.indicator_seq OWNER TO postgres;
-- ddl-end --

-- object: sharadar.unit_type_seq | type: SEQUENCE --
-- DROP SEQUENCE IF EXISTS sharadar.unit_type_seq CASCADE;
CREATE SEQUENCE sharadar.unit_type_seq
	INCREMENT BY 1
	MINVALUE 0
	MAXVALUE 2147483647
	START WITH 1
	CACHE 1
	NO CYCLE
	OWNED BY NONE;
-- ddl-end --
ALTER SEQUENCE sharadar.unit_type_seq OWNER TO postgres;
-- ddl-end --

-- object: sharadar.corporate_action_seq | type: SEQUENCE --
-- DROP SEQUENCE IF EXISTS sharadar.corporate_action_seq CASCADE;
CREATE SEQUENCE sharadar.corporate_action_seq
	INCREMENT BY 1
	MINVALUE 0
	MAXVALUE 2147483647
	START WITH 1
	CACHE 1
	NO CYCLE
	OWNED BY NONE;
-- ddl-end --
ALTER SEQUENCE sharadar.corporate_action_seq OWNER TO postgres;
-- ddl-end --

-- object: sharadar.ticker_seq | type: SEQUENCE --
-- DROP SEQUENCE IF EXISTS sharadar.ticker_seq CASCADE;
CREATE SEQUENCE sharadar.ticker_seq
	INCREMENT BY 1
	MINVALUE 0
	MAXVALUE 2147483647
	START WITH 1
	CACHE 1
	NO CYCLE
	OWNED BY NONE;
-- ddl-end --
ALTER SEQUENCE sharadar.ticker_seq OWNER TO postgres;
-- ddl-end --

-- object: sharadar.fundamentals_seq | type: SEQUENCE --
-- DROP SEQUENCE IF EXISTS sharadar.fundamentals_seq CASCADE;
CREATE SEQUENCE sharadar.fundamentals_seq
	INCREMENT BY 1
	MINVALUE 0
	MAXVALUE 2147483647
	START WITH 1
	CACHE 1
	NO CYCLE
	OWNED BY NONE;
-- ddl-end --
ALTER SEQUENCE sharadar.fundamentals_seq OWNER TO postgres;
-- ddl-end --

-- object: sharadar.institutional_holdings_seq | type: SEQUENCE --
-- DROP SEQUENCE IF EXISTS sharadar.institutional_holdings_seq CASCADE;
CREATE SEQUENCE sharadar.institutional_holdings_seq
	INCREMENT BY 1
	MINVALUE 0
	MAXVALUE 2147483647
	START WITH 1
	CACHE 1
	NO CYCLE
	OWNED BY NONE;
-- ddl-end --
ALTER SEQUENCE sharadar.institutional_holdings_seq OWNER TO postgres;
-- ddl-end --

-- object: sharadar.event_seq | type: SEQUENCE --
-- DROP SEQUENCE IF EXISTS sharadar.event_seq CASCADE;
CREATE SEQUENCE sharadar.event_seq
	INCREMENT BY 1
	MINVALUE 0
	MAXVALUE 2147483647
	START WITH 1
	CACHE 1
	NO CYCLE
	OWNED BY NONE;
-- ddl-end --
ALTER SEQUENCE sharadar.event_seq OWNER TO postgres;
-- ddl-end --

-- object: sharadar.equity_price_seq | type: SEQUENCE --
-- DROP SEQUENCE IF EXISTS sharadar.equity_price_seq CASCADE;
CREATE SEQUENCE sharadar.equity_price_seq
	INCREMENT BY 1
	MINVALUE 0
	MAXVALUE 2147483647
	START WITH 1
	CACHE 1
	NO CYCLE
	OWNED BY NONE;
-- ddl-end --
ALTER SEQUENCE sharadar.equity_price_seq OWNER TO postgres;
-- ddl-end --

-- object: sharadar.indicators | type: TABLE --
-- DROP TABLE IF EXISTS sharadar.indicators CASCADE;
CREATE TABLE sharadar.indicators (
	indicator_id integer NOT NULL DEFAULT nextval('sharadar.indicator_seq'::regclass),
	table_name varchar(32) NOT NULL,
	indicator varchar(32) NOT NULL,
	is_filter bool NOT NULL,
	is_primary_key bool NOT NULL,
	title varchar(256) NOT NULL,
	description varchar(2048),
	unit_type_id integer NOT NULL,
	CONSTRAINT indicators_pk PRIMARY KEY (indicator_id)

);
-- ddl-end --
ALTER TABLE sharadar.indicators OWNER TO postgres;
-- ddl-end --

-- object: sharadar.unit_type | type: TABLE --
-- DROP TABLE IF EXISTS sharadar.unit_type CASCADE;
CREATE TABLE sharadar.unit_type (
	unit_type_id integer NOT NULL DEFAULT nextval('sharadar.unit_type_seq'::regclass),
	unit_type_code varchar(32) NOT NULL,
	CONSTRAINT unit_type_pk PRIMARY KEY (unit_type_id),
	CONSTRAINT unit_type_code_uq UNIQUE (unit_type_code)

);
-- ddl-end --
ALTER TABLE sharadar.unit_type OWNER TO postgres;
-- ddl-end --

-- object: sharadar.event_code_seq | type: SEQUENCE --
-- DROP SEQUENCE IF EXISTS sharadar.event_code_seq CASCADE;
CREATE SEQUENCE sharadar.event_code_seq
	INCREMENT BY 1
	MINVALUE 0
	MAXVALUE 2147483647
	START WITH 1
	CACHE 1
	NO CYCLE
	OWNED BY NONE;
-- ddl-end --
ALTER SEQUENCE sharadar.event_code_seq OWNER TO postgres;
-- ddl-end --

-- object: sharadar.event | type: TABLE --
-- DROP TABLE IF EXISTS sharadar.event CASCADE;
CREATE TABLE sharadar.event (
	event_id integer NOT NULL DEFAULT nextval('sharadar.event_seq'::regclass),
	ticker varchar(16) NOT NULL,
	ticker_id integer,
	event_date date NOT NULL,
	event_code_id integer NOT NULL,
	CONSTRAINT event_pk PRIMARY KEY (event_id)

);
-- ddl-end --
ALTER TABLE sharadar.event OWNER TO postgres;
-- ddl-end --

-- object: sharadar.insider_holdings_seq | type: SEQUENCE --
-- DROP SEQUENCE IF EXISTS sharadar.insider_holdings_seq CASCADE;
CREATE SEQUENCE sharadar.insider_holdings_seq
	INCREMENT BY 1
	MINVALUE 0
	MAXVALUE 2147483647
	START WITH 1
	CACHE 1
	NO CYCLE
	OWNED BY NONE;
-- ddl-end --
ALTER SEQUENCE sharadar.insider_holdings_seq OWNER TO postgres;
-- ddl-end --

-- object: sharadar.scale_seq | type: SEQUENCE --
-- DROP SEQUENCE IF EXISTS sharadar.scale_seq CASCADE;
CREATE SEQUENCE sharadar.scale_seq
	INCREMENT BY 1
	MINVALUE 0
	MAXVALUE 2147483647
	START WITH 1
	CACHE 1
	NO CYCLE
	OWNED BY NONE;
-- ddl-end --
ALTER SEQUENCE sharadar.scale_seq OWNER TO postgres;
-- ddl-end --

-- object: sharadar.sector_map_seq | type: SEQUENCE --
-- DROP SEQUENCE IF EXISTS sharadar.sector_map_seq CASCADE;
CREATE SEQUENCE sharadar.sector_map_seq
	INCREMENT BY 1
	MINVALUE 0
	MAXVALUE 2147483647
	START WITH 1
	CACHE 1
	NO CYCLE
	OWNED BY NONE;
-- ddl-end --
ALTER SEQUENCE sharadar.sector_map_seq OWNER TO postgres;
-- ddl-end --

-- object: sharadar.sector_code_type_seq | type: SEQUENCE --
-- DROP SEQUENCE IF EXISTS sharadar.sector_code_type_seq CASCADE;
CREATE SEQUENCE sharadar.sector_code_type_seq
	INCREMENT BY 1
	MINVALUE 0
	MAXVALUE 2147483647
	START WITH 1
	CACHE 1
	NO CYCLE
	OWNED BY NONE;
-- ddl-end --
ALTER SEQUENCE sharadar.sector_code_type_seq OWNER TO postgres;
-- ddl-end --

-- object: sharadar.sector_map | type: TABLE --
-- DROP TABLE IF EXISTS sharadar.sector_map CASCADE;
CREATE TABLE sharadar.sector_map (
	sector_map_id integer NOT NULL DEFAULT nextval('sharadar.sector_map_seq'::regclass),
	sector_code_type_id integer NOT NULL,
	sector_code integer,
	sector varchar(64),
	industry varchar(64),
	CONSTRAINT sector_map_pk PRIMARY KEY (sector_map_id)

);
-- ddl-end --
ALTER TABLE sharadar.sector_map OWNER TO postgres;
-- ddl-end --

-- object: sharadar.ticker_category_seq | type: SEQUENCE --
-- DROP SEQUENCE IF EXISTS sharadar.ticker_category_seq CASCADE;
CREATE SEQUENCE sharadar.ticker_category_seq
	INCREMENT BY 1
	MINVALUE 0
	MAXVALUE 2147483647
	START WITH 1
	CACHE 1
	NO CYCLE
	OWNED BY NONE;
-- ddl-end --
ALTER SEQUENCE sharadar.ticker_category_seq OWNER TO postgres;
-- ddl-end --

-- object: sharadar.ticker | type: TABLE --
-- DROP TABLE IF EXISTS sharadar.ticker CASCADE;
CREATE TABLE sharadar.ticker (
	ticker_id integer NOT NULL DEFAULT nextval('sharadar.ticker_seq'::regclass),
	table_name varchar(32) NOT NULL,
	perma_ticker_id integer NOT NULL,
	ticker varchar(16),
	name varchar(256) NOT NULL,
	exchange_id integer,
	is_delisted bool NOT NULL,
	ticker_category_id integer,
	cusips varchar(256),
	sic_sector_id integer,
	fama_sector_id integer,
	sector_id integer,
	market_cap_scale_id integer,
	revenue_scale_id integer,
	related_tickers varchar(256),
	currency_id integer NOT NULL,
	location varchar(64),
	last_updated date,
	first_added date,
	first_price_date date,
	last_price_date date,
	first_quarter date,
	last_quarter date,
	secfilings varchar(256),
	company_site varchar(256),
	CONSTRAINT tickers_pk PRIMARY KEY (ticker_id)

);
-- ddl-end --
ALTER TABLE sharadar.ticker OWNER TO postgres;
-- ddl-end --

-- object: sharadar.scale | type: TABLE --
-- DROP TABLE IF EXISTS sharadar.scale CASCADE;
CREATE TABLE sharadar.scale (
	scale_id integer NOT NULL DEFAULT nextval('sharadar.scale_seq'::regclass),
	scale_code varchar(32) NOT NULL,
	CONSTRAINT scale_pk PRIMARY KEY (scale_id),
	CONSTRAINT scale_code_uq UNIQUE (scale_code)

);
-- ddl-end --
ALTER TABLE sharadar.scale OWNER TO postgres;
-- ddl-end --

-- object: sharadar.cusip_seq | type: SEQUENCE --
-- DROP SEQUENCE IF EXISTS sharadar.cusip_seq CASCADE;
CREATE SEQUENCE sharadar.cusip_seq
	INCREMENT BY 1
	MINVALUE 0
	MAXVALUE 2147483647
	START WITH 1
	CACHE 1
	NO CYCLE
	OWNED BY NONE;
-- ddl-end --
ALTER SEQUENCE sharadar.cusip_seq OWNER TO postgres;
-- ddl-end --

-- object: sharadar.ticker_category | type: TABLE --
-- DROP TABLE IF EXISTS sharadar.ticker_category CASCADE;
CREATE TABLE sharadar.ticker_category (
	ticker_category_id integer NOT NULL DEFAULT nextval('sharadar.ticker_category_seq'::regclass),
	ticker_category_code varchar(64),
	CONSTRAINT ticker_category_pk PRIMARY KEY (ticker_category_id),
	CONSTRAINT ticker_category_code_uq UNIQUE (ticker_category_code)

);
-- ddl-end --
ALTER TABLE sharadar.ticker_category OWNER TO postgres;
-- ddl-end --

-- object: sharadar.exchange_seq | type: SEQUENCE --
-- DROP SEQUENCE IF EXISTS sharadar.exchange_seq CASCADE;
CREATE SEQUENCE sharadar.exchange_seq
	INCREMENT BY 1
	MINVALUE 0
	MAXVALUE 2147483647
	START WITH 1
	CACHE 1
	NO CYCLE
	OWNED BY NONE;
-- ddl-end --
ALTER SEQUENCE sharadar.exchange_seq OWNER TO postgres;
-- ddl-end --

-- object: sharadar.exchange | type: TABLE --
-- DROP TABLE IF EXISTS sharadar.exchange CASCADE;
CREATE TABLE sharadar.exchange (
	exchange_id integer NOT NULL DEFAULT nextval('sharadar.exchange_seq'::regclass),
	exchange_code varchar(32) NOT NULL,
	CONSTRAINT exchange_pk PRIMARY KEY (exchange_id),
	CONSTRAINT exchange_code_uq UNIQUE (exchange_code)

);
-- ddl-end --
ALTER TABLE sharadar.exchange OWNER TO postgres;
-- ddl-end --

-- object: sharadar.currency_seq | type: SEQUENCE --
-- DROP SEQUENCE IF EXISTS sharadar.currency_seq CASCADE;
CREATE SEQUENCE sharadar.currency_seq
	INCREMENT BY 1
	MINVALUE 0
	MAXVALUE 2147483647
	START WITH 1
	CACHE 1
	NO CYCLE
	OWNED BY NONE;
-- ddl-end --
ALTER SEQUENCE sharadar.currency_seq OWNER TO postgres;
-- ddl-end --

-- object: sharadar.currency | type: TABLE --
-- DROP TABLE IF EXISTS sharadar.currency CASCADE;
CREATE TABLE sharadar.currency (
	currency_id integer NOT NULL DEFAULT nextval('sharadar.currency_seq'::regclass),
	currency_code varchar(8) NOT NULL,
	CONSTRAINT currency_pk PRIMARY KEY (currency_id),
	CONSTRAINT currency_code_uq UNIQUE (currency_code)

);
-- ddl-end --
ALTER TABLE sharadar.currency OWNER TO postgres;
-- ddl-end --

-- object: sharadar.sector_code_type | type: TABLE --
-- DROP TABLE IF EXISTS sharadar.sector_code_type CASCADE;
CREATE TABLE sharadar.sector_code_type (
	sector_code_type_id integer NOT NULL DEFAULT nextval('sharadar.sector_code_type_seq'::regclass),
	sector_code_type_code varchar(32) NOT NULL,
	CONSTRAINT sector_code_type_pk PRIMARY KEY (sector_code_type_id)

);
-- ddl-end --
ALTER TABLE sharadar.sector_code_type OWNER TO postgres;
-- ddl-end --

-- object: sharadar.event_code | type: TABLE --
-- DROP TABLE IF EXISTS sharadar.event_code CASCADE;
CREATE TABLE sharadar.event_code (
	event_code_id integer NOT NULL DEFAULT nextval('sharadar.event_code_seq'::regclass),
	event_code integer NOT NULL,
	event_description varchar(256) NOT NULL,
	CONSTRAINT event_code_pk PRIMARY KEY (event_code_id),
	CONSTRAINT event_code_uq UNIQUE (event_code)

);
-- ddl-end --
ALTER TABLE sharadar.event_code OWNER TO postgres;
-- ddl-end --

-- object: sharadar.equity_price | type: TABLE --
-- DROP TABLE IF EXISTS sharadar.equity_price CASCADE;
CREATE TABLE sharadar.equity_price (
	equity_price_id integer NOT NULL DEFAULT nextval('sharadar.equity_price_seq'::regclass),
	ticker varchar(16) NOT NULL,
	ticker_id integer,
	price_date date NOT NULL,
	open money NOT NULL,
	high money NOT NULL,
	low money NOT NULL,
	close money NOT NULL,
	volume integer,
	dividends money NOT NULL,
	close_unadj money NOT NULL,
	last_updated date NOT NULL,
	CONSTRAINT equity_price_pk PRIMARY KEY (equity_price_id)

);
-- ddl-end --
ALTER TABLE sharadar.equity_price OWNER TO postgres;
-- ddl-end --

-- object: sharadar.institutional_holdings | type: TABLE --
-- DROP TABLE IF EXISTS sharadar.institutional_holdings CASCADE;
CREATE TABLE sharadar.institutional_holdings (
	institutional_holdings_id integer NOT NULL DEFAULT nextval('sharadar.institutional_holdings_seq'::regclass),
	ticker varchar(16),
	ticker_id integer,
	institutional_investor_id integer NOT NULL,
	security_type_id integer NOT NULL,
	calendar_date date NOT NULL,
	value money NOT NULL,
	units int8 NOT NULL,
	price money,
	CONSTRAINT institutional_holdings_pk PRIMARY KEY (institutional_holdings_id)

);
-- ddl-end --
ALTER TABLE sharadar.institutional_holdings OWNER TO postgres;
-- ddl-end --

-- object: sharadar.insider_holdings | type: TABLE --
-- DROP TABLE IF EXISTS sharadar.insider_holdings CASCADE;
CREATE TABLE sharadar.insider_holdings (
	insider_holdings_id integer NOT NULL DEFAULT nextval('sharadar.insider_holdings_seq'::regclass),
	ticker varchar(16),
	ticker_id integer,
	filing_date date NOT NULL,
	form_type_id integer NOT NULL,
	issuer_name varchar(128) NOT NULL,
	owner_name varchar(128) NOT NULL,
	officer_title varchar(128),
	is_director bool NOT NULL,
	is_officer bool NOT NULL,
	is_ten_percent_owner bool NOT NULL,
	transaction_date date,
	security_ad_type_id integer,
	transaction_type_id integer,
	shares_owned_before_transaction int8,
	transaction_shares int8,
	shares_owned_following_transaction int8,
	transaction_price_per_share money,
	transaction_value money,
	security_title_type_id integer,
	direct_or_indirect char(1),
	nature_of_ownership varchar(128),
	date_exercisable date,
	price_exercisable money,
	expiration_date date,
	row_num integer NOT NULL,
	CONSTRAINT insider_holdings_pk PRIMARY KEY (insider_holdings_id)

);
-- ddl-end --
ALTER TABLE sharadar.insider_holdings OWNER TO postgres;
-- ddl-end --

-- object: sharadar.institutional_investor_seq | type: SEQUENCE --
-- DROP SEQUENCE IF EXISTS sharadar.institutional_investor_seq CASCADE;
CREATE SEQUENCE sharadar.institutional_investor_seq
	INCREMENT BY 1
	MINVALUE 0
	MAXVALUE 2147483647
	START WITH 1
	CACHE 1
	NO CYCLE
	OWNED BY NONE;
-- ddl-end --
ALTER SEQUENCE sharadar.institutional_investor_seq OWNER TO postgres;
-- ddl-end --

-- object: sharadar.institutional_investor | type: TABLE --
-- DROP TABLE IF EXISTS sharadar.institutional_investor CASCADE;
CREATE TABLE sharadar.institutional_investor (
	institutional_investor_id integer NOT NULL DEFAULT nextval('sharadar.institutional_investor_seq'::regclass),
	institutional_investor_name varchar(128) NOT NULL,
	CONSTRAINT institutional_investor_pk PRIMARY KEY (institutional_investor_id),
	CONSTRAINT institutional_investor_uq UNIQUE (institutional_investor_name)

);
-- ddl-end --
ALTER TABLE sharadar.institutional_investor OWNER TO postgres;
-- ddl-end --

-- object: sharadar.security_type_seq | type: SEQUENCE --
-- DROP SEQUENCE IF EXISTS sharadar.security_type_seq CASCADE;
CREATE SEQUENCE sharadar.security_type_seq
	INCREMENT BY 1
	MINVALUE 0
	MAXVALUE 2147483647
	START WITH 1
	CACHE 1
	NO CYCLE
	OWNED BY NONE;
-- ddl-end --
ALTER SEQUENCE sharadar.security_type_seq OWNER TO postgres;
-- ddl-end --

-- object: sharadar.security_type | type: TABLE --
-- DROP TABLE IF EXISTS sharadar.security_type CASCADE;
CREATE TABLE sharadar.security_type (
	security_type_id integer NOT NULL DEFAULT nextval('sharadar.security_type_seq'::regclass),
	security_type_code varchar(8) NOT NULL,
	CONSTRAINT security_type_pk PRIMARY KEY (security_type_id),
	CONSTRAINT security_type_uq UNIQUE (security_type_code)

);
-- ddl-end --
ALTER TABLE sharadar.security_type OWNER TO postgres;
-- ddl-end --

-- object: sharadar.fundamentals | type: TABLE --
-- DROP TABLE IF EXISTS sharadar.fundamentals CASCADE;
CREATE TABLE sharadar.fundamentals (
	fundamentals_id integer NOT NULL DEFAULT nextval('sharadar.fundamentals_seq'::regclass),
	ticker varchar(16) NOT NULL,
	ticker_id integer,
	dimension_type_id integer NOT NULL,
	calendar_date date NOT NULL,
	date_key date NOT NULL,
	report_period date NOT NULL,
	last_updated date NOT NULL,
	accoci money,
	assets money,
	assets_avg money,
	assets_c money,
	assets_nc money,
	asset_turnover decimal(16,4),
	bvps money,
	capex money,
	cash_neq money,
	cash_neq_usd money,
	cor money,
	consol_inc money,
	current_ratio decimal(16,4),
	de decimal(16,4),
	debt money,
	debt_c money,
	debt_nc money,
	debt_usd money,
	deferred_rev money,
	dep_amor money,
	deposits money,
	div_yield decimal(16,4),
	dps money,
	ebit money,
	ebitda money,
	ebitda_margin decimal(16,4),
	ebitda_usd money,
	ebit_usd money,
	ebt money,
	eps money,
	eps_dil money,
	eps_usd money,
	equity money,
	equity_avg money,
	equity_usd money,
	ev money,
	ev_ebit decimal(16,4),
	ev_ebitda decimal(16,4),
	fcf money,
	fcf_ps money,
	fx_usd money,
	gp money,
	gross_margin decimal(16,4),
	intangibles money,
	int_exp money,
	inv_cap money,
	inv_cap_avg money,
	inventory money,
	investments money,
	investments_c money,
	investments_nc money,
	liabilities money,
	liabilities_c money,
	liabilities_nc money,
	market_cap money,
	ncf money,
	ncf_bus money,
	ncf_common money,
	ncf_debt money,
	ncf_div money,
	ncf_f money,
	ncf_i money,
	ncf_inv money,
	ncf_o money,
	ncf_x money,
	net_inc money,
	net_inc_cmn money,
	net_inc_cmn_usd money,
	net_inc_dis money,
	net_inc_nci money,
	net_margin decimal(16,4),
	op_ex money,
	op_inc money,
	payables money,
	payout_ratio decimal(16,4),
	pb decimal(16,4),
	pe decimal(16,4),
	pe1 decimal(16,4),
	ppne_net money,
	pref_div_is money,
	price money,
	ps decimal(16,4),
	ps1 decimal(16,4),
	receivables money,
	ret_earn money,
	revenue money,
	revenue_usd money,
	rnd money,
	roa decimal(16,4),
	roe decimal(16,4),
	roic decimal(16,4),
	ros decimal(16,4),
	sb_comp money,
	sgna money,
	share_factor decimal(16,4),
	shares_bas int8,
	shares_wa int8,
	shares_wa_dil int8,
	sps money,
	tangibles money,
	tax_assets money,
	tax_exp money,
	tax_liabilities money,
	tbvps money,
	working_capital money,
	CONSTRAINT fundamentals_pk PRIMARY KEY (fundamentals_id)

);
-- ddl-end --
ALTER TABLE sharadar.fundamentals OWNER TO postgres;
-- ddl-end --

-- object: sharadar.form_type_seq | type: SEQUENCE --
-- DROP SEQUENCE IF EXISTS sharadar.form_type_seq CASCADE;
CREATE SEQUENCE sharadar.form_type_seq
	INCREMENT BY 1
	MINVALUE 0
	MAXVALUE 2147483647
	START WITH 1
	CACHE 1
	NO CYCLE
	OWNED BY NONE;
-- ddl-end --
ALTER SEQUENCE sharadar.form_type_seq OWNER TO postgres;
-- ddl-end --

-- object: sharadar.form_type | type: TABLE --
-- DROP TABLE IF EXISTS sharadar.form_type CASCADE;
CREATE TABLE sharadar.form_type (
	form_type_id integer NOT NULL DEFAULT nextval('sharadar.form_type_seq'::regclass),
	form_type_code varchar(32) NOT NULL,
	CONSTRAINT form_type_pk PRIMARY KEY (form_type_id),
	CONSTRAINT form_type_uq UNIQUE (form_type_code)

);
-- ddl-end --
ALTER TABLE sharadar.form_type OWNER TO postgres;
-- ddl-end --

-- object: sharadar.security_ad_seq | type: SEQUENCE --
-- DROP SEQUENCE IF EXISTS sharadar.security_ad_seq CASCADE;
CREATE SEQUENCE sharadar.security_ad_seq
	INCREMENT BY 1
	MINVALUE 0
	MAXVALUE 2147483647
	START WITH 1
	CACHE 1
	NO CYCLE
	OWNED BY NONE;
-- ddl-end --
ALTER SEQUENCE sharadar.security_ad_seq OWNER TO postgres;
-- ddl-end --

-- object: sharadar.security_ad_type | type: TABLE --
-- DROP TABLE IF EXISTS sharadar.security_ad_type CASCADE;
CREATE TABLE sharadar.security_ad_type (
	security_ad_type_id integer NOT NULL DEFAULT nextval('sharadar.security_ad_seq'::regclass),
	security_ad_type_code varchar(8) NOT NULL,
	CONSTRAINT security_ad_type_pk PRIMARY KEY (security_ad_type_id),
	CONSTRAINT security_ad_type_uq UNIQUE (security_ad_type_code)

);
-- ddl-end --
ALTER TABLE sharadar.security_ad_type OWNER TO postgres;
-- ddl-end --

-- object: sharadar.tranaction_type_seq | type: SEQUENCE --
-- DROP SEQUENCE IF EXISTS sharadar.tranaction_type_seq CASCADE;
CREATE SEQUENCE sharadar.tranaction_type_seq
	INCREMENT BY 1
	MINVALUE 0
	MAXVALUE 2147483647
	START WITH 1
	CACHE 1
	NO CYCLE
	OWNED BY NONE;
-- ddl-end --
ALTER SEQUENCE sharadar.tranaction_type_seq OWNER TO postgres;
-- ddl-end --

-- object: sharadar.transaction_type | type: TABLE --
-- DROP TABLE IF EXISTS sharadar.transaction_type CASCADE;
CREATE TABLE sharadar.transaction_type (
	transaction_type_id integer NOT NULL DEFAULT nextval('sharadar.tranaction_type_seq'::regclass),
	transaction_type_code varchar(8) NOT NULL,
	CONSTRAINT transaction_type_pk PRIMARY KEY (transaction_type_id),
	CONSTRAINT transaction_type_uq UNIQUE (transaction_type_code)

);
-- ddl-end --
ALTER TABLE sharadar.transaction_type OWNER TO postgres;
-- ddl-end --

-- object: sharadar.security_title_type_seq | type: SEQUENCE --
-- DROP SEQUENCE IF EXISTS sharadar.security_title_type_seq CASCADE;
CREATE SEQUENCE sharadar.security_title_type_seq
	INCREMENT BY 1
	MINVALUE 0
	MAXVALUE 2147483647
	START WITH 1
	CACHE 1
	NO CYCLE
	OWNED BY NONE;
-- ddl-end --
ALTER SEQUENCE sharadar.security_title_type_seq OWNER TO postgres;
-- ddl-end --

-- object: sharadar.security_title_type | type: TABLE --
-- DROP TABLE IF EXISTS sharadar.security_title_type CASCADE;
CREATE TABLE sharadar.security_title_type (
	security_title_type_id integer NOT NULL DEFAULT nextval('sharadar.security_title_type_seq'::regclass),
	security_title_type_code varchar(64) NOT NULL,
	CONSTRAINT security_title_type_pk PRIMARY KEY (security_title_type_id),
	CONSTRAINT security_title_type_uq UNIQUE (security_title_type_code)

);
-- ddl-end --
ALTER TABLE sharadar.security_title_type OWNER TO postgres;
-- ddl-end --

-- object: sharadar.dimension_type_seq | type: SEQUENCE --
-- DROP SEQUENCE IF EXISTS sharadar.dimension_type_seq CASCADE;
CREATE SEQUENCE sharadar.dimension_type_seq
	INCREMENT BY 1
	MINVALUE 0
	MAXVALUE 2147483647
	START WITH 1
	CACHE 1
	NO CYCLE
	OWNED BY NONE;
-- ddl-end --
ALTER SEQUENCE sharadar.dimension_type_seq OWNER TO postgres;
-- ddl-end --

-- object: sharadar.dimension_type | type: TABLE --
-- DROP TABLE IF EXISTS sharadar.dimension_type CASCADE;
CREATE TABLE sharadar.dimension_type (
	dimension_type_id integer NOT NULL DEFAULT nextval('sharadar.dimension_type_seq'::regclass),
	dimension_type_code varchar(8) NOT NULL,
	CONSTRAINT dimension_type_pk PRIMARY KEY (dimension_type_id)

);
-- ddl-end --
ALTER TABLE sharadar.dimension_type OWNER TO postgres;
-- ddl-end --

-- object: sharadar.corp_action_type_seq | type: SEQUENCE --
-- DROP SEQUENCE IF EXISTS sharadar.corp_action_type_seq CASCADE;
CREATE SEQUENCE sharadar.corp_action_type_seq
	INCREMENT BY 1
	MINVALUE 0
	MAXVALUE 2147483647
	START WITH 1
	CACHE 1
	NO CYCLE
	OWNED BY NONE;
-- ddl-end --
ALTER SEQUENCE sharadar.corp_action_type_seq OWNER TO postgres;
-- ddl-end --

-- object: sharadar.corp_action_type | type: TABLE --
-- DROP TABLE IF EXISTS sharadar.corp_action_type CASCADE;
CREATE TABLE sharadar.corp_action_type (
	corp_action_type_id integer NOT NULL DEFAULT nextval('sharadar.corp_action_type_seq'::regclass),
	corp_action_type_code varchar(32) NOT NULL,
	CONSTRAINT corp_action_type_pk PRIMARY KEY (corp_action_type_id),
	CONSTRAINT corp_action_type_uq UNIQUE (corp_action_type_code)

);
-- ddl-end --
ALTER TABLE sharadar.corp_action_type OWNER TO postgres;
-- ddl-end --

-- object: sharadar.corp_action | type: TABLE --
-- DROP TABLE IF EXISTS sharadar.corp_action CASCADE;
CREATE TABLE sharadar.corp_action (
	corp_action_id integer NOT NULL DEFAULT nextval('sharadar.corporate_action_seq'::regclass),
	corp_action_date date NOT NULL,
	ticker varchar(16),
	ticker_id integer,
	corp_action_type_id integer NOT NULL,
	name varchar(256),
	value decimal(16,4),
	contra_ticker varchar(16),
	contra_name varchar(256),
	CONSTRAINT corp_action_pk PRIMARY KEY (corp_action_id)

);
-- ddl-end --
ALTER TABLE sharadar.corp_action OWNER TO postgres;
-- ddl-end --

-- object: perma_ticker_idx | type: INDEX --
-- DROP INDEX IF EXISTS sharadar.perma_ticker_idx CASCADE;
CREATE INDEX perma_ticker_idx ON sharadar.ticker
	USING btree
	(
	  perma_ticker_id
	);
-- ddl-end --

-- object: ticker_idx | type: INDEX --
-- DROP INDEX IF EXISTS sharadar.ticker_idx CASCADE;
CREATE INDEX ticker_idx ON sharadar.ticker
	USING btree
	(
	  ticker
	);
-- ddl-end --

-- object: institutional_holdings_uq_idx | type: INDEX --
-- DROP INDEX IF EXISTS sharadar.institutional_holdings_uq_idx CASCADE;
CREATE UNIQUE INDEX institutional_holdings_uq_idx ON sharadar.institutional_holdings
	USING btree
	(
	  ticker,
	  institutional_investor_id,
	  security_type_id,
	  calendar_date
	);
-- ddl-end --

-- object: insider_holdings_uq_idx | type: INDEX --
-- DROP INDEX IF EXISTS sharadar.insider_holdings_uq_idx CASCADE;
CREATE UNIQUE INDEX insider_holdings_uq_idx ON sharadar.insider_holdings
	USING btree
	(
	  ticker,
	  filing_date,
	  owner_name,
	  form_type_id,
	  row_num
	);
-- ddl-end --

-- object: event_uq_idx | type: INDEX --
-- DROP INDEX IF EXISTS sharadar.event_uq_idx CASCADE;
CREATE UNIQUE INDEX event_uq_idx ON sharadar.event
	USING btree
	(
	  ticker,
	  event_date,
	  event_code_id
	);
-- ddl-end --

-- object: corp_action_uq_idx | type: INDEX --
-- DROP INDEX IF EXISTS sharadar.corp_action_uq_idx CASCADE;
CREATE UNIQUE INDEX corp_action_uq_idx ON sharadar.corp_action
	USING btree
	(
	  ticker,
	  corp_action_date,
	  corp_action_type_id
	);
-- ddl-end --

-- object: equity_price_uq_idx | type: INDEX --
-- DROP INDEX IF EXISTS sharadar.equity_price_uq_idx CASCADE;
CREATE UNIQUE INDEX equity_price_uq_idx ON sharadar.equity_price
	USING btree
	(
	  ticker,
	  price_date
	);
-- ddl-end --

-- object: fundamentals_uq_idx | type: INDEX --
-- DROP INDEX IF EXISTS sharadar.fundamentals_uq_idx CASCADE;
CREATE UNIQUE INDEX fundamentals_uq_idx ON sharadar.fundamentals
	USING btree
	(
	  ticker,
	  dimension_type_id,
	  date_key,
	  report_period
	);
-- ddl-end --

-- object: sharadar.batch_status_seq | type: SEQUENCE --
-- DROP SEQUENCE IF EXISTS sharadar.batch_status_seq CASCADE;
CREATE SEQUENCE sharadar.batch_status_seq
	INCREMENT BY 1
	MINVALUE 0
	MAXVALUE 2147483647
	START WITH 1
	CACHE 1
	NO CYCLE
	OWNED BY NONE;
-- ddl-end --
ALTER SEQUENCE sharadar.batch_status_seq OWNER TO postgres;
-- ddl-end --

-- object: sharadar.batch_status | type: TABLE --
-- DROP TABLE IF EXISTS sharadar.batch_status CASCADE;
CREATE TABLE sharadar.batch_status (
	batch_status_id integer NOT NULL DEFAULT nextval('sharadar.batch_status_seq'::regclass),
	workflow_name varchar(64) NOT NULL,
	start_date date,
	end_date date,
	md5_checksum varchar(32) NOT NULL,
	is_pending bool NOT NULL,
	CONSTRAINT batch_status_pk PRIMARY KEY (batch_status_id)

);
-- ddl-end --
ALTER TABLE sharadar.batch_status OWNER TO postgres;
-- ddl-end --

-- object: batch_status_uq_idx | type: INDEX --
-- DROP INDEX IF EXISTS sharadar.batch_status_uq_idx CASCADE;
CREATE UNIQUE INDEX batch_status_uq_idx ON sharadar.batch_status
	USING btree
	(
	  workflow_name,
	  start_date,
	  end_date
	);
-- ddl-end --

-- object: unit_type_fk | type: CONSTRAINT --
-- ALTER TABLE sharadar.indicators DROP CONSTRAINT IF EXISTS unit_type_fk CASCADE;
ALTER TABLE sharadar.indicators ADD CONSTRAINT unit_type_fk FOREIGN KEY (unit_type_id)
REFERENCES sharadar.unit_type (unit_type_id) MATCH FULL
ON DELETE NO ACTION ON UPDATE NO ACTION;
-- ddl-end --

-- object: event_code_fk | type: CONSTRAINT --
-- ALTER TABLE sharadar.event DROP CONSTRAINT IF EXISTS event_code_fk CASCADE;
ALTER TABLE sharadar.event ADD CONSTRAINT event_code_fk FOREIGN KEY (event_code_id)
REFERENCES sharadar.event_code (event_code_id) MATCH FULL
ON DELETE NO ACTION ON UPDATE NO ACTION;
-- ddl-end --

-- object: ticker_fk | type: CONSTRAINT --
-- ALTER TABLE sharadar.event DROP CONSTRAINT IF EXISTS ticker_fk CASCADE;
ALTER TABLE sharadar.event ADD CONSTRAINT ticker_fk FOREIGN KEY (ticker_id)
REFERENCES sharadar.ticker (ticker_id) MATCH FULL
ON DELETE NO ACTION ON UPDATE NO ACTION;
-- ddl-end --

-- object: sector_code_type_fk | type: CONSTRAINT --
-- ALTER TABLE sharadar.sector_map DROP CONSTRAINT IF EXISTS sector_code_type_fk CASCADE;
ALTER TABLE sharadar.sector_map ADD CONSTRAINT sector_code_type_fk FOREIGN KEY (sector_code_type_id)
REFERENCES sharadar.sector_code_type (sector_code_type_id) MATCH FULL
ON DELETE NO ACTION ON UPDATE NO ACTION;
-- ddl-end --

-- object: exchange_fk | type: CONSTRAINT --
-- ALTER TABLE sharadar.ticker DROP CONSTRAINT IF EXISTS exchange_fk CASCADE;
ALTER TABLE sharadar.ticker ADD CONSTRAINT exchange_fk FOREIGN KEY (exchange_id)
REFERENCES sharadar.exchange (exchange_id) MATCH FULL
ON DELETE NO ACTION ON UPDATE NO ACTION;
-- ddl-end --

-- object: ticker_category_fk | type: CONSTRAINT --
-- ALTER TABLE sharadar.ticker DROP CONSTRAINT IF EXISTS ticker_category_fk CASCADE;
ALTER TABLE sharadar.ticker ADD CONSTRAINT ticker_category_fk FOREIGN KEY (ticker_category_id)
REFERENCES sharadar.ticker_category (ticker_category_id) MATCH FULL
ON DELETE NO ACTION ON UPDATE NO ACTION;
-- ddl-end --

-- object: sic_sector_fk | type: CONSTRAINT --
-- ALTER TABLE sharadar.ticker DROP CONSTRAINT IF EXISTS sic_sector_fk CASCADE;
ALTER TABLE sharadar.ticker ADD CONSTRAINT sic_sector_fk FOREIGN KEY (sic_sector_id)
REFERENCES sharadar.sector_map (sector_map_id) MATCH FULL
ON DELETE NO ACTION ON UPDATE NO ACTION;
-- ddl-end --

-- object: fama_sector_fk | type: CONSTRAINT --
-- ALTER TABLE sharadar.ticker DROP CONSTRAINT IF EXISTS fama_sector_fk CASCADE;
ALTER TABLE sharadar.ticker ADD CONSTRAINT fama_sector_fk FOREIGN KEY (fama_sector_id)
REFERENCES sharadar.sector_map (sector_map_id) MATCH FULL
ON DELETE NO ACTION ON UPDATE NO ACTION;
-- ddl-end --

-- object: sector_fk | type: CONSTRAINT --
-- ALTER TABLE sharadar.ticker DROP CONSTRAINT IF EXISTS sector_fk CASCADE;
ALTER TABLE sharadar.ticker ADD CONSTRAINT sector_fk FOREIGN KEY (sector_id)
REFERENCES sharadar.sector_map (sector_map_id) MATCH FULL
ON DELETE NO ACTION ON UPDATE NO ACTION;
-- ddl-end --

-- object: market_cap_scale_fk | type: CONSTRAINT --
-- ALTER TABLE sharadar.ticker DROP CONSTRAINT IF EXISTS market_cap_scale_fk CASCADE;
ALTER TABLE sharadar.ticker ADD CONSTRAINT market_cap_scale_fk FOREIGN KEY (market_cap_scale_id)
REFERENCES sharadar.scale (scale_id) MATCH FULL
ON DELETE NO ACTION ON UPDATE NO ACTION;
-- ddl-end --

-- object: revenue_scale_fk | type: CONSTRAINT --
-- ALTER TABLE sharadar.ticker DROP CONSTRAINT IF EXISTS revenue_scale_fk CASCADE;
ALTER TABLE sharadar.ticker ADD CONSTRAINT revenue_scale_fk FOREIGN KEY (revenue_scale_id)
REFERENCES sharadar.scale (scale_id) MATCH FULL
ON DELETE NO ACTION ON UPDATE NO ACTION;
-- ddl-end --

-- object: currency_fk | type: CONSTRAINT --
-- ALTER TABLE sharadar.ticker DROP CONSTRAINT IF EXISTS currency_fk CASCADE;
ALTER TABLE sharadar.ticker ADD CONSTRAINT currency_fk FOREIGN KEY (currency_id)
REFERENCES sharadar.currency (currency_id) MATCH FULL
ON DELETE NO ACTION ON UPDATE NO ACTION;
-- ddl-end --

-- object: ticker_fk | type: CONSTRAINT --
-- ALTER TABLE sharadar.equity_price DROP CONSTRAINT IF EXISTS ticker_fk CASCADE;
ALTER TABLE sharadar.equity_price ADD CONSTRAINT ticker_fk FOREIGN KEY (ticker_id)
REFERENCES sharadar.ticker (ticker_id) MATCH FULL
ON DELETE NO ACTION ON UPDATE NO ACTION;
-- ddl-end --

-- object: ticker_fk | type: CONSTRAINT --
-- ALTER TABLE sharadar.institutional_holdings DROP CONSTRAINT IF EXISTS ticker_fk CASCADE;
ALTER TABLE sharadar.institutional_holdings ADD CONSTRAINT ticker_fk FOREIGN KEY (ticker_id)
REFERENCES sharadar.ticker (ticker_id) MATCH FULL
ON DELETE NO ACTION ON UPDATE NO ACTION;
-- ddl-end --

-- object: institutional_investor_fk | type: CONSTRAINT --
-- ALTER TABLE sharadar.institutional_holdings DROP CONSTRAINT IF EXISTS institutional_investor_fk CASCADE;
ALTER TABLE sharadar.institutional_holdings ADD CONSTRAINT institutional_investor_fk FOREIGN KEY (institutional_investor_id)
REFERENCES sharadar.institutional_investor (institutional_investor_id) MATCH FULL
ON DELETE NO ACTION ON UPDATE NO ACTION;
-- ddl-end --

-- object: security_type_fk | type: CONSTRAINT --
-- ALTER TABLE sharadar.institutional_holdings DROP CONSTRAINT IF EXISTS security_type_fk CASCADE;
ALTER TABLE sharadar.institutional_holdings ADD CONSTRAINT security_type_fk FOREIGN KEY (security_type_id)
REFERENCES sharadar.security_type (security_type_id) MATCH FULL
ON DELETE NO ACTION ON UPDATE NO ACTION;
-- ddl-end --

-- object: ticker_fk | type: CONSTRAINT --
-- ALTER TABLE sharadar.insider_holdings DROP CONSTRAINT IF EXISTS ticker_fk CASCADE;
ALTER TABLE sharadar.insider_holdings ADD CONSTRAINT ticker_fk FOREIGN KEY (ticker_id)
REFERENCES sharadar.ticker (ticker_id) MATCH FULL
ON DELETE NO ACTION ON UPDATE NO ACTION;
-- ddl-end --

-- object: form_type_fk | type: CONSTRAINT --
-- ALTER TABLE sharadar.insider_holdings DROP CONSTRAINT IF EXISTS form_type_fk CASCADE;
ALTER TABLE sharadar.insider_holdings ADD CONSTRAINT form_type_fk FOREIGN KEY (form_type_id)
REFERENCES sharadar.form_type (form_type_id) MATCH FULL
ON DELETE NO ACTION ON UPDATE NO ACTION;
-- ddl-end --

-- object: security_ad_fk | type: CONSTRAINT --
-- ALTER TABLE sharadar.insider_holdings DROP CONSTRAINT IF EXISTS security_ad_fk CASCADE;
ALTER TABLE sharadar.insider_holdings ADD CONSTRAINT security_ad_fk FOREIGN KEY (security_ad_type_id)
REFERENCES sharadar.security_ad_type (security_ad_type_id) MATCH FULL
ON DELETE NO ACTION ON UPDATE NO ACTION;
-- ddl-end --

-- object: transaction_type_fk | type: CONSTRAINT --
-- ALTER TABLE sharadar.insider_holdings DROP CONSTRAINT IF EXISTS transaction_type_fk CASCADE;
ALTER TABLE sharadar.insider_holdings ADD CONSTRAINT transaction_type_fk FOREIGN KEY (transaction_type_id)
REFERENCES sharadar.transaction_type (transaction_type_id) MATCH FULL
ON DELETE NO ACTION ON UPDATE NO ACTION;
-- ddl-end --

-- object: security_title_type_fk | type: CONSTRAINT --
-- ALTER TABLE sharadar.insider_holdings DROP CONSTRAINT IF EXISTS security_title_type_fk CASCADE;
ALTER TABLE sharadar.insider_holdings ADD CONSTRAINT security_title_type_fk FOREIGN KEY (security_title_type_id)
REFERENCES sharadar.security_title_type (security_title_type_id) MATCH FULL
ON DELETE NO ACTION ON UPDATE NO ACTION;
-- ddl-end --

-- object: ticker_fk | type: CONSTRAINT --
-- ALTER TABLE sharadar.fundamentals DROP CONSTRAINT IF EXISTS ticker_fk CASCADE;
ALTER TABLE sharadar.fundamentals ADD CONSTRAINT ticker_fk FOREIGN KEY (ticker_id)
REFERENCES sharadar.ticker (ticker_id) MATCH FULL
ON DELETE NO ACTION ON UPDATE NO ACTION;
-- ddl-end --

-- object: dimension_type_fk | type: CONSTRAINT --
-- ALTER TABLE sharadar.fundamentals DROP CONSTRAINT IF EXISTS dimension_type_fk CASCADE;
ALTER TABLE sharadar.fundamentals ADD CONSTRAINT dimension_type_fk FOREIGN KEY (dimension_type_id)
REFERENCES sharadar.dimension_type (dimension_type_id) MATCH FULL
ON DELETE NO ACTION ON UPDATE NO ACTION;
-- ddl-end --

-- object: ticker_fk | type: CONSTRAINT --
-- ALTER TABLE sharadar.corp_action DROP CONSTRAINT IF EXISTS ticker_fk CASCADE;
ALTER TABLE sharadar.corp_action ADD CONSTRAINT ticker_fk FOREIGN KEY (ticker_id)
REFERENCES sharadar.ticker (ticker_id) MATCH FULL
ON DELETE NO ACTION ON UPDATE NO ACTION;
-- ddl-end --

-- object: corp_action_type_fk | type: CONSTRAINT --
-- ALTER TABLE sharadar.corp_action DROP CONSTRAINT IF EXISTS corp_action_type_fk CASCADE;
ALTER TABLE sharadar.corp_action ADD CONSTRAINT corp_action_type_fk FOREIGN KEY (corp_action_type_id)
REFERENCES sharadar.corp_action_type (corp_action_type_id) MATCH FULL
ON DELETE NO ACTION ON UPDATE NO ACTION;
-- ddl-end --


-- Appended SQL commands --
GRANT USAGE ON SCHEMA sharadar TO sharadar;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA sharadar TO sharadar;
GRANT SELECT, USAGE ON ALL SEQUENCES IN SCHEMA sharadar TO sharadar;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA sharadar TO sharadar;
-- ddl-end --