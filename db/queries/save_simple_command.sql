insert into simple_command_execution(id, command, output_file, text_response_mid)
VALUES (?, ?, ?, ?)
returning id;