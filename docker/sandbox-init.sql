-- Create sandbox_user: the restricted role used to execute user-submitted SQL queries.
-- This role gets SELECT-only access on the public schema and a strict statement timeout.

CREATE ROLE sandbox_user WITH
    LOGIN
    PASSWORD 'sandbox_user_pass'
    NOSUPERUSER
    NOCREATEDB
    NOCREATEROLE
    NOINHERIT
    NOREPLICATION;

-- Revoke schema creation from PUBLIC (default in PG16, but explicit for clarity)
REVOKE CREATE ON SCHEMA public FROM PUBLIC;

-- Allow sandbox_user to connect to this database
GRANT CONNECT ON DATABASE sandbox TO sandbox_user;

-- Allow sandbox_user to see objects in the public schema
GRANT USAGE ON SCHEMA public TO sandbox_user;

-- Grant SELECT on all tables that already exist (none at init time, but safe to include)
GRANT SELECT ON ALL TABLES IN SCHEMA public TO sandbox_user;

-- Grant SELECT automatically on all future tables created in public schema by postgres
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO sandbox_user;

-- Hard 5-second limit on every query sandbox_user runs
ALTER ROLE sandbox_user SET statement_timeout = '5s';
