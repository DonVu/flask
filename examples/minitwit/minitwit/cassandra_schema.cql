DROP KEYSPACE IF EXISTS minitwit;

CREATE KEYSPACE minitwit
           WITH replication = {'class' : 'SimpleStrategy',
                               'replication_factor' : 2};

USE minitwit;

CREATE TABLE authenticate_user (
    user_name text PRIMARY KEY,
    pw_hash text
);

CREATE TABLE data (
    user_id uuid PRIMARY KEY,
    user_name text,
    email text,
    whom_id set<text>
);

CREATE INDEX ON data (user_name);

CREATE TABLE messages (
    author_id uuid PRIMARY KEY,
    text text,
    pub_date date,
);
