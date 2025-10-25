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

CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ language 'plpgsql';


CREATE SCHEMA IF NOT EXISTS public;

/*
    Table: mentors
*/
CREATE TABLE mentors (
    mentor_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    chief_mentor_id UUID NOT NULL,
    orgnaztion_id INTEGER NOT NULL,
    login_id TEXT NOT NULL,
    name_family TEXT NOT NULL,
    name_given TEXT NOT NULL,
    access_group UUID NOT NULL,
    last_login_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);


/*
    Table: mentor_groups
*/
CREATE TABLE mentor_groups (
    group_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    chief_mentor_id UUID NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_mentor_groups_chief
        FOREIGN KEY (chief_mentor_id) REFERENCES mentors (mentor_id)
);


/*
    Table: mentor_group_members 
*/
CREATE TABLE mentor_group_members (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    group_id UUID NOT NULL,
    mentor_id UUID NOT NULL,
    role TEXT NOT NULL,
    joined_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_mgm_group FOREIGN KEY (group_id) REFERENCES mentor_groups (group_id),
    CONSTRAINT fk_mgm_mentor FOREIGN KEY (mentor_id) REFERENCES mentors (mentor_id)
);

CREATE TRIGGER update_mentor_timestamp
BEFORE UPDATE ON mentors
FOR EACH ROW
EXECUTE PROCEDURE update_timestamp();

CREATE TRIGGER update_mentor_group_timestamp
BEFORE UPDATE ON mentor_groups
FOR EACH ROW
EXECUTE PROCEDURE update_timestamp();