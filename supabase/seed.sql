-- NaviSense seed data
-- Run this in the Supabase SQL editor for the CURRENT project.

-- Test user: admin / admin  (SHA-256 of "admin")
insert into users (email, first_name, last_name, organization, password_hash, package)
values ('admin', 'Admin', 'User', 'ARL', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', 'premium')
on conflict (email) do nothing;

-- Sample ports
insert into ports (country, locode, port, latitude, longitude) values
('Malaysia', 'MYPKG', 'Port Klang', 3.0, 101.4),
('Malaysia', 'MYPEN', 'Penang', 5.414, 100.329),
('Malaysia', 'MYKEM', 'Kemaman', 4.267, 103.45),
('Singapore', 'SGSIN', 'Singapore', 1.264, 103.84),
('Thailand', 'THBKK', 'Bangkok', 13.69, 100.6),
('Indonesia', 'IDJKT', 'Jakarta', -6.1, 106.8),
('Viet Nam', 'VNSGN', 'Ho Chi Minh City', 10.762, 106.68),
('China', 'CNTXG', 'Tianjin', 38.96, 117.78)
on conflict do nothing;

-- Sample NMEA position reports (so the map has vessels to show)
insert into nmea_data (nmea, timestamp) values
('!AIVDM,1,1,,A,13P;8FP0001jKk`OAvL0w?wP06<0B,0*53', now() - interval '2 minutes'),
('!AIVDM,1,1,,A,15M67FC000G?ufbE`FepT@3n00Sa,0*5C', now() - interval '1 minutes'),
('!AIVDM,1,1,,B,177KQJ5000G?tO`K>RA1wUbN0TKH,0*5C', now()),
('!AIVDM,1,1,,A,16P?d@4000G?rJi@:n00pE9vP00S,0*21', now() - interval '3 minutes'),
('!AIVDM,1,1,,B,35NR0hP00DqHTuH@ENwV@qvV0000,0*23', now() - interval '30 seconds')
on conflict do nothing;
