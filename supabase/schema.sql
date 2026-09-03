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
