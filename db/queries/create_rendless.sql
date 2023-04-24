insert into rendless_execution(id, user_tid, is_active, command, screen_session, hardcopy)
VALUES (?, ?, ?, ?, ?, ?)
returning id;