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

/*Mail Table*/
CREATE TABLE mail (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v7() NOT NULL,
    to_email VARCHAR NOT NULL,
    title VARCHAR NOT NULL,
    contents VARCHAR,
    status VARCHAR NOT NULL DEFAULT 'PENDING',
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX id ON mail (id);
CREATE INDEX status ON mail (status);
