DROP TABLE IF EXISTS results CASCADE;
DROP TABLE IF EXISTS appliance_presets CASCADE;
DROP TABLE IF EXISTS locations CASCADE;
DROP TABLE IF EXISTS projects CASCADE;
DROP TABLE IF EXISTS appliances CASCADE;
DROP TABLE IF EXISTS solar_panels CASCADE;
DROP TABLE IF EXISTS batteries CASCADE;
DROP TABLE IF EXISTS settings CASCADE;
DROP TABLE IF EXISTS users CASCADE;

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    is_admin BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    property_type TEXT,
    state TEXT,
    city TEXT,
    solar_kw DOUBLE PRECISION,
    battery_kwh DOUBLE PRECISION,
    cost DOUBLE PRECISION,
    inputs TEXT NOT NULL,
    results TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE appliances (
    id SERIAL PRIMARY KEY,
    key TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    icon TEXT,
    watts DOUBLE PRECISION NOT NULL,
    qty INTEGER NOT NULL,
    hours DOUBLE PRECISION NOT NULL
);

CREATE TABLE solar_panels (
    id SERIAL PRIMARY KEY,
    model TEXT NOT NULL,
    watts INTEGER NOT NULL,
    area_m2 DOUBLE PRECISION NOT NULL,
    price DOUBLE PRECISION NOT NULL
);

CREATE TABLE batteries (
    id SERIAL PRIMARY KEY,
    model TEXT NOT NULL,
    kwh DOUBLE PRECISION NOT NULL,
    price DOUBLE PRECISION NOT NULL,
    chemistry TEXT
);

CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value DOUBLE PRECISION NOT NULL
);

-- Security: block Supabase's public API from reading these tables.
-- Flask connects directly as the database owner, so it is not affected.
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE appliances ENABLE ROW LEVEL SECURITY;
ALTER TABLE solar_panels ENABLE ROW LEVEL SECURITY;
ALTER TABLE batteries ENABLE ROW LEVEL SECURITY;
ALTER TABLE settings ENABLE ROW LEVEL SECURITY;