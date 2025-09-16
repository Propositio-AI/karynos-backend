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

CREATE OR REPLACE FUNCTION default_expires_at() RETURNS TIMESTAMP AS
$$
BEGIN
    RETURN CURRENT_TIMESTAMP + INTERVAL '3 months';
END
$$ LANGUAGE plpgsql;

/*Auth Table*/
CREATE TABLE auth (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v7() NOT NULL,
    email VARCHAR NOT NULL,
    token VARCHAR UNIQUE NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT default_expires_at(),
    used_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NULL,
    CONSTRAINT expires_after_created CHECK (expires_at > created_at),
    CONSTRAINT used_before_expires CHECK (used_at < expires_at)
);
CREATE INDEX auth_token ON auth (token);
CREATE INDEX idx_email_expires_at ON auth (email, expires_at);

/*Refresh Table*/
CREATE TABLE refresh (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v7() NOT NULL,
    token VARCHAR UNIQUE NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT default_expires_at(),
    used_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NULL,
    CONSTRAINT expires_after_created CHECK (expires_at > created_at),
    CONSTRAINT used_before_expires CHECK (used_at > expires_at)
);
CREATE INDEX refresh_token ON refresh (token);
