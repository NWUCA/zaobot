create table waken_list
(
    id             integer primary key,
    wake_timestamp integer,
    wake_time      text,
    nickname       text,
    waken_num      integer
);

create table wake_history
(
    id         integer,
    wake_time  text,
    sleep_time text
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
)