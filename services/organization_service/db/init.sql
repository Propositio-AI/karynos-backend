CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ language 'plpgsql';

CREATE SCHEMA IF NOT EXISTS public;

CREATE TYPE organization_type AS ENUM ('SCHOOL_ELEMENTARY', 'SCHOOL_JUNIOR', 'SCHOOL_HIGH', 'COMPANY', 'OTHER');

/*
    Table: organization
*/
CREATE TABLE organization (
    organization_id SERIAL PRIMARY KEY,
    organization_name TEXT NOT NULL,
    display_name TEXT NOT NULL,
    organization_type organization_type NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);


CREATE TRIGGER update_organization_timestamp
BEFORE UPDATE ON organization
FOR EACH ROW
EXECUTE PROCEDURE update_timestamp();
