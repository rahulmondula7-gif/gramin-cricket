-- Optional sample data for testing. Delete these rows before a real tournament.
insert into public.teams (team_name, village, captain_name, mobile, status)
values
('Demo Warriors', 'Demo Village', 'Sample Captain', '9000000001', 'confirmed'),
('Demo Strikers', 'Demo Nagar', 'Example Captain', '9000000002', 'waiting')
on conflict do nothing;
