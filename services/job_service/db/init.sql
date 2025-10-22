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
    Table: jobs
*/
CREATE TABLE IF NOT EXISTS public.jobs (
    job_id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


/*
    Table: job_reviews
*/
CREATE TABLE IF NOT EXISTS public.job_reviews (
    review_id UUID DEFAULT uuid_generate_v7() PRIMARY KEY,
    job_id INTEGER NOT NULL REFERENCES public.jobs (job_id) ON DELETE CASCADE,
    worker_id UUID NOT NULL,
    salary INTEGER CHECK (salary >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


/*
    Table: history
*/
CREATE TABLE IF NOT EXISTS public.history (
    history_id UUID DEFAULT uuid_generate_v7() PRIMARY KEY,
    job_id INTEGER NOT NULL REFERENCES public.jobs (job_id) ON DELETE CASCADE,
    dreamer_id UUID NOT NULL,
    good BOOLEAN NOT NULL DEFAULT FALSE,
    bad BOOLEAN NOT NULL DEFAULT FALSE,
    save BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);