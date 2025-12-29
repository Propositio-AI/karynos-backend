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
CREATE TABLE IF NOT EXISTS mentors (
    mentor_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    chief_mentor_id UUID,
    organization_id INTEGER NOT NULL,
    login_id TEXT NOT NULL,
    name_family TEXT NOT NULL,
    name_given TEXT NOT NULL,
    access_group UUID,
    last_login_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TRIGGER update_mentor_timestamp
BEFORE UPDATE ON mentors
FOR EACH ROW
EXECUTE PROCEDURE update_timestamp();

/*
    Table: mentor_groups
*/
CREATE TABLE IF NOT EXISTS mentor_groups (
    group_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    chief_mentor_id UUID REFERENCES mentors(mentor_id) ON DELETE RESTRICT,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TRIGGER update_mentor_group_timestamp
BEFORE UPDATE ON mentor_groups
FOR EACH ROW
EXECUTE PROCEDURE update_timestamp();

/*
    Table: mentor_group_members 
*/
CREATE TABLE IF NOT EXISTS mentor_group_members (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    group_id UUID NOT NULL REFERENCES mentor_groups(group_id) ON DELETE RESTRICT,
    mentor_id UUID NOT NULL REFERENCES mentors(mentor_id) ON DELETE RESTRICT,
    role TEXT NOT NULL,
    joined_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

