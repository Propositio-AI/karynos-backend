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

CREATE TYPE archive_type AS ENUM ('TEXTBOOK', 'CHAT', 'GRAPH', 'PLAN');
CREATE TYPE share_type AS ENUM ('PRIVATE', 'PUBLIC');
CREATE TYPE archive_status_type AS ENUM ('PENDING', 'RUNNING', 'SUCCEEDED', 'FAILED', 'CANCELLED');

/*Archive Table*/
CREATE TABLE archive (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v7() NOT NULL,
    query_id UUID NOT NULL,
    parent_id UUID REFERENCES archive(id),
    archive_type archive_type NOT NULL DEFAULT 'CHAT',
    share_type share_type NOT NULL DEFAULT 'PRIVATE',
    archive_status archive_status_type NOT NULL DEFAULT 'PENDING',
    contents JSON,
    contents_metadata JSON,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX archive_id ON archive (id);
