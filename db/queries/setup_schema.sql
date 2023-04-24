create table users
(
    tid          text primary key,
    name         text    default '',
    is_logged_in boolean default false
);

create table management
(
    key   text primary key,
    value text not null
);

create table simple_command_execution
(
    id                 text primary key,
    command            text,
    output_file        text,
    text_response_mid  text,
    image_response_mid text null
);

create table rendless_execution
(
    id             text primary key,
    user_tid       text,
    is_active      boolean,
    command        text,
    screen_session text,
    hardcopy       text
)