create table if not exists users (
    email text primary key,
    first_name text,
    last_name text,
    organization text,
    password_hash text not null,
    auth_token text,
    time_created timestamptz,
    time_expiry timestamptz,
    package text
);

create table if not exists nmea_data (
    id bigserial primary key,
    nmea text not null,
    timestamp timestamptz default now()
);

create index if not exists idx_nmea_data_timestamp on nmea_data (timestamp desc);

create table if not exists ports (
    id bigserial primary key,
    country text,
    locode text,
    port text,
    latitude numeric,
    longitude numeric
);

create table if not exists sensor_data (
    id bigserial primary key,
    device_id text,
    voltage numeric,
    temperature numeric,
    nmea text,
    timestamp timestamptz default now()
);

create index if not exists idx_sensor_data_timestamp on sensor_data (timestamp desc);

create table if not exists ais_data_sat (
    id bigserial primary key,
    time_stamp timestamptz default now(),
    ch1 integer,
    ch2 integer,
    rssi integer,
    data_column text,
    mmsi text
);

create index if not exists idx_ais_data_sat_mmsi on ais_data_sat (mmsi);
