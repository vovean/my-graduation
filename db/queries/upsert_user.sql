insert into users(tid, name, is_logged_in)
values (?, ?, ?)
on conflict DO NOTHING;