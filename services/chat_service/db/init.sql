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

CREATE SCHEMA IF NOT EXISTS public;

/*
    Table: conversations  
*/
CREATE TABLE conversations (
    conversation_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    owner_id UUID NOT NULL,
    title VARCHAR NOT NULL,
    share_type share_type NOT NULL DEFAULT 'PRIVATE',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


/*
    Table: messages  
*/
CREATE TABLE messages (
    message_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    conversation_id UUID NOT NULL,
    sender_id UUID NOT NULL,
    role VARCHAR NOT NULL,
    text_content TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_messages_conversation
        FOREIGN KEY (conversation_id) REFERENCES conversations (conversation_id)
);


/*
    Table: conversation_participants   
*/
CREATE TABLE conversation_participants (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    conversation_id UUID NOT NULL,
    user_id UUID NOT NULL,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_participants_conversation
        FOREIGN KEY (conversation_id) REFERENCES conversations (conversation_id)
);

CREATE TRIGGER update_conversation_timestamp
BEFORE UPDATE ON conversations
FOR EACH ROW
EXECUTE PROCEDURE update_timestamp();

CREATE TRIGGER update_message_timestamp
BEFORE UPDATE ON messages
FOR EACH ROW
EXECUTE PROCEDURE update_timestamp();