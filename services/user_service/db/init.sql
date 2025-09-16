CREATE OR REPLACE FUNCTION uuid_generate_v7() RETURNS UUID AS
$$
BEGIN
    return encode(set_bit(set_bit(overlay(
        uuid_send(gen_random_uuid())
        placing substring(int8send(floor(extract(epoch from clock_timestamp()) * 1000)::bigint) from 3)
        from 1 for 6
    ), 52, 1), 53, 1), 'hex')::uuid;
END
$$ LANGUAGE plpgsql;

CREATE TYPE user_type AS ENUM ('GENERAL', 'STUDENT', 'TEACHER', 'ADMIN');

/*Users Table*/
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v7() NOT NULL,
    last_name VARCHAR,
    first_name VARCHAR NOT NULL,
    email VARCHAR NOT NULL UNIQUE,
    user_type user_type NOT NULL DEFAULT 'GENERAL',
    grade INTEGER,
    class_no INTEGER,
    student_no INTEGER,
    school UUID,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP WITHOUT TIME ZONE
);


/*Initialize*/
INSERT INTO user (first_name, email) VALUES ('Toya', 'toya@propositio.com'), ('Ren', 'ren@propositio.com'), ('Kage', 'kage@propositio.com'),