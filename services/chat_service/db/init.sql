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

CREATE TYPE share_type AS ENUM ('PRIVATE', 'PUBLIC');
CREATE TYPE role_type AS ENUM ('HUMAN', 'AI', 'SYSTEM');

CREATE SCHEMA IF NOT EXISTS public;

/*
    Table: conversations  
*/
CREATE TABLE IF NOT EXISTS conversations (
    conversation_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    owner_id UUID NOT NULL,
    title TEXT NOT NULL,
    share_type share_type NOT NULL DEFAULT 'PRIVATE',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

/*
    Table: messages  
*/
CREATE TABLE IF NOT EXISTS messages (
    message_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    conversation_id UUID NOT NULL REFERENCES conversations(conversation_id) ON DELETE RESTRICT,
    sender_id UUID NOT NULL,
    role role_type NOT NULL,
    text_content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TRIGGER update_message_timestamp
BEFORE UPDATE ON messages
FOR EACH ROW
EXECUTE PROCEDURE update_timestamp();

/*
    Table: conversation_participants   
*/
CREATE TABLE IF NOT EXISTS conversation_participants (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    conversation_id UUID NOT NULL REFERENCES conversations(conversation_id) ON DELETE RESTRICT,
    user_id UUID NOT NULL,
    joined_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER update_conversation_timestamp
BEFORE UPDATE ON conversations
FOR EACH ROW
EXECUTE PROCEDURE update_timestamp();
