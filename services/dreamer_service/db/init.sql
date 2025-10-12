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

CREATE SCHEMA IF NOT EXISTS public;

/*
    Table: dreamers 
*/
CREATE TABLE dreamers (
    dreamer_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    orgnaztion_id INTEGER,
    login_id VARCHAR NOT NULL,
    name_family VARCHAR NOT NULL,
    name_given VARCHAR NOT NULL,
    last_login_at TIMESTAMP,
    updated_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);


/*
    Table: dreamer_groups 
*/
CREATE TABLE dreamer_groups (
    group_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name VARCHAR NOT NULL,
    description VARCHAR,
    updated_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);


/*
    Table: dreamer_group_members  
*/
CREATE TABLE dreamer_group_members (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    group_id UUID NOT NULL,
    dreamer_id UUID NOT NULL,
    joined_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT fk_dgm_group FOREIGN KEY (group_id) REFERENCES dreamer_groups (group_id),
    CONSTRAINT fk_dgm_dreamer FOREIGN KEY (dreamer_id) REFERENCES dreamers (dreamer_id)
);