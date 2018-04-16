DROP KEYSPACE IF EXISTS minitwit;

CREATE KEYSPACE minitwit
           WITH replication = {'class' : 'SimpleStrategy',
                               'replication_factor' : 2};

USE minitwit;

CREATE TABLE get_userid_by_username (
    user_name text PRIMARY KEY,
    userid uuid
);

CREATE TABLE get_user_record (
    user_id uuid PRIMARY KEY,
    user_name text,
    email text,
);

CREATE INDEX ON get_user_record (user_name);

CREATE TABLE timeline (
    user_id uuid PRIMARY KEY,
    message_id uuid,
    author_id uuid,
    text text,
    pub_date date,
    who_id uuid,
    whom_id uuid
);

CREATE TABLE messages (
    user_id uuid PRIMARY KEY,
    username text,
    email text,
    message_id uuid,
    author_id uuid,
    text text,
    pub_date date
);
