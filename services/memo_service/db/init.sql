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

/*Memo Table*/
CREATE TABLE memo (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v7() NOT NULL,
    archive_id UUID NOT NULL,
    user_id UUID NOT NULL,
    drawing_data JSON NOT NULL,
    canvas_w FLOAT NOT NULL,
    canvas_h FLOAT NOT NULL,
     TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,created_at
    updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX id ON memo (id);
CREATE INDEX query_and_user ON memo (query_id, user_id);
