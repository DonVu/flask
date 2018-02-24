INSERT INTO user (username, email, pw_hash)
VALUES ('Mickey_Mouse', 'mmouse@aol.com', 'password1');

INSERT INTO user (username, email, pw_hash)
VALUES ('Minnie_Mouse', 'minmouse@aol.com', 'password2');

INSERT INTO user (username, email, pw_hash)
VALUES ('Donald_Duck', 'dduck@aol.com', 'password3');

INSERT INTO user (username, email, pw_hash)
VALUES ('Goofy', 'goofy@aol.com', 'password4');

INSERT INTO user (username, email, pw_hash)
VALUES ('Daisy', 'daisy@aol.com', 'password5');

INSERT INTO user (username, email, pw_hash)
VALUES ('Pluto', 'pluto@aol.com', 'password6');

INSERT INTO follower
VALUES (1, 2);

INSERT INTO follower
VALUES (1, 3);

INSERT INTO follower
VALUES (2, 3);

INSERT INTO follower
VALUES (4, 3);

INSERT INTO follower
VALUES (5, 1);

INSERT INTO follower
VALUES (3, 2);

INSERT INTO message (author_id, text, pub_date)
VALUES (1, 'Hey everyone!', 100); 

INSERT INTO message (author_id, text, pub_date)
VALUES (2, 'Hey! Goodmorning!', 100);

INSERT INTO message (author_id, text, pub_date)
VALUES (5, 'Have a great day guys!', 100); 

