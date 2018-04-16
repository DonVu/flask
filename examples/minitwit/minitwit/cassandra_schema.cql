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
    username text,
    email text,
    message_id uuid,
    author_id uuid,
    text text,
    pub_date date,
    who_id list<int>,
    whom_id list<int>
);

CREATE INDEX ON data (user_name);
CREATE INDEX ON data (who_id);
CREATE INDEX ON data (whom_id);
