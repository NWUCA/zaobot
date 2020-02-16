create table rest_record
(
    id              integer,
    wake_timestamp  integer,
    wake_time       text,
    nickname        text,
    waken_num       integer,
    sleep_timestamp integer,
    sleep_time      text
);

create table log
(
    message         text,
    sender_nickname text,
    sender_id       integer,
    timestamp       integer,
    time            text
);

create table treehole
(
    message         text,
    timestamp       integer,
    time            text,
    sender_nickname text,
    sender_id       integer
);

create table xiuxian_emulator
(
    id  integer primary key,
    nickname text,
    exp integer,
    level integer,
    last_speaking_timestamp integer,
    last_speaking_time text
)