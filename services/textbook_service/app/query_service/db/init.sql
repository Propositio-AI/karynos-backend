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

CREATE TYPE query_type AS ENUM ('TEXTBOOK', 'CHAT', 'PLAN');

/*Query Table*/
CREATE TABLE query (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v7() NOT NULL,
    user_id UUID NOT NULL,
    parent_id UUID REFERENCES query(id),
    query TEXT,
    query_type query_type NOT NULL DEFAULT 'CHAT',
    favorite BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX query_id ON query (id);
CREATE INDEX user_id ON query (user_id);
