update rendless_execution
set is_active= false
where is_active = true
  and user_tid = ?
returning screen_session;