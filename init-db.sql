-- HTX Trading Platform - Database Initialization Script
-- PostgreSQL initialization script (optional)

-- Create database extensions
CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";
CREATE EXTENSION IF NOT EXISTS \"pg_trgm\";
CREATE EXTENSION IF NOT EXISTS \"btree_gin\";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS trading;
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE SCHEMA IF NOT EXISTS ml;

-- Set default search path
ALTER DATABASE htx SET search_path = trading, analytics, ml, public;

-- Create user for application
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'htx_app') THEN
        CREATE ROLE htx_app WITH LOGIN PASSWORD 'htx_app_password';
    END IF;
END
$$;

-- Grant permissions
GRANT USAGE ON SCHEMA trading TO htx_app;
GRANT USAGE ON SCHEMA analytics TO htx_app;
GRANT USAGE ON SCHEMA ml TO htx_app;
GRANT CREATE ON SCHEMA trading TO htx_app;
GRANT CREATE ON SCHEMA analytics TO htx_app;
GRANT CREATE ON SCHEMA ml TO htx_app;

-- Grant permissions on all tables in schemas
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA trading TO htx_app;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA analytics TO htx_app;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA ml TO htx_app;

-- Grant permissions on all sequences in schemas
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA trading TO htx_app;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA analytics TO htx_app;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA ml TO htx_app;

-- Set default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA trading GRANT ALL ON TABLES TO htx_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA analytics GRANT ALL ON TABLES TO htx_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA ml GRANT ALL ON TABLES TO htx_app;

ALTER DEFAULT PRIVILEGES IN SCHEMA trading GRANT ALL ON SEQUENCES TO htx_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA analytics GRANT ALL ON SEQUENCES TO htx_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA ml GRANT ALL ON SEQUENCES TO htx_app;

-- Create indexes for performance
-- These will be created by Alembic migrations, but we can prepare the database

-- Log the initialization
INSERT INTO information_schema.sql_features (feature_id, feature_name, sub_feature_id, sub_feature_name, is_supported, comments)
VALUES ('HTX001', 'HTX Trading Platform', '001', 'Database Initialized', 'YES', 'Database initialized at ' || NOW());

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'HTX Trading Platform database initialized successfully!';
END
$$;