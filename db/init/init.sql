-- ==============================
--  TABLE: residents
-- ==============================
CREATE TABLE IF NOT EXISTS residents (
    id SMALLSERIAL PRIMARY KEY,
    last_name VARCHAR(128),
    first_name VARCHAR(128),
    middle_name VARCHAR(128),
    suffix VARCHAR(8),
    gender TEXT CHECK (gender IN ('male', 'female')),
    birthdate DATE,
    years_residency SMALLINT CHECK (years_residency >= 0),
    email VARCHAR(64) UNIQUE,
    phone_number CHAR(11),
    account_pin TEXT, -- store hashed PIN
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==============================
--  TABLE: puroks
-- ==============================
CREATE TABLE IF NOT EXISTS puroks (
    id SMALLSERIAL PRIMARY KEY,
    purok_name VARCHAR(8) NOT NULL
);

-- ==============================
--  TABLE: addresses
-- ==============================
CREATE TABLE IF NOT EXISTS addresses (
    id SMALLSERIAL PRIMARY KEY,
    resident_id SMALLINT REFERENCES residents(id) ON DELETE CASCADE ON UPDATE CASCADE,
    unit_blk_street VARCHAR(255),
    purok_id SMALLINT CHECK (purok_id BETWEEN 1 AND 255) REFERENCES puroks(id) ON DELETE SET NULL ON UPDATE CASCADE,
    barangay VARCHAR(64),
    municipality VARCHAR(16),
    province VARCHAR(16),
    region VARCHAR(64),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_current BOOLEAN DEFAULT TRUE
);

-- Ensure only one current address per resident
CREATE UNIQUE INDEX IF NOT EXISTS one_current_address_per_resident
ON addresses(resident_id)
WHERE is_current = TRUE;

-- ==============================
--  TABLE: rfid_uid
-- ==============================
CREATE TABLE IF NOT EXISTS rfid_uid (
    id SMALLSERIAL PRIMARY KEY,
    resident_id SMALLINT REFERENCES residents(id) ON DELETE CASCADE ON UPDATE CASCADE,
    rfid_uid CHAR(9) UNIQUE,
    status TEXT CHECK (status IN ('active', 'inactive')) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- ==============================
--  TABLE: brgy_staff
-- ==============================
CREATE TABLE IF NOT EXISTS brgy_staff (
    id SMALLSERIAL PRIMARY KEY,
    resident_id SMALLINT REFERENCES residents(id) ON DELETE CASCADE ON UPDATE CASCADE,
    email VARCHAR(64) UNIQUE,
    password TEXT,
    role VARCHAR(128),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- ==============================
--  TABLE: request_types
-- ==============================
CREATE TABLE IF NOT EXISTS request_types (
    id SERIAL PRIMARY KEY,
    request_type_name VARCHAR(64),
    description TEXT,
    status TEXT CHECK (status IN ('active', 'inactive')) DEFAULT 'active',
    price NUMERIC(10,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==============================
--  TABLE: templates
-- ==============================
CREATE TABLE IF NOT EXISTS templates (
    id SERIAL PRIMARY KEY,
    template_name VARCHAR(64),
    description TEXT,
    file BYTEA,
    file_name VARCHAR(128),
    request_type_id INT UNIQUE REFERENCES request_types(id) ON DELETE SET NULL ON UPDATE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==============================
--  TABLE: requests
-- ==============================
CREATE TABLE IF NOT EXISTS requests (
    id SERIAL PRIMARY KEY,
    resident_id SMALLINT REFERENCES residents(id) ON DELETE CASCADE ON UPDATE CASCADE,
    request_type_id INT REFERENCES request_types(id) ON DELETE CASCADE ON UPDATE CASCADE,
    processed_by SMALLINT REFERENCES brgy_staff(id) ON DELETE SET NULL ON UPDATE CASCADE,
    rejected_by SMALLINT REFERENCES brgy_staff(id) ON DELETE SET NULL ON UPDATE CASCADE,
    purpose TEXT,
    request_file BYTEA,
    status TEXT CHECK (status IN ('pending', 'processing', 'ready', 'released', 'rejected', 'cancelled')) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);