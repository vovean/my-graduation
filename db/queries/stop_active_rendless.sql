update rendless_execution
set is_active= false
where is_active = true
returning screen_session;