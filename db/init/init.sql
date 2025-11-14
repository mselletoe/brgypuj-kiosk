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
--  TABLE: brgy_staff
-- ==============================
CREATE TABLE IF NOT EXISTS brgy_staff (
    id SMALLSERIAL PRIMARY KEY,
    resident_id SMALLINT REFERENCES residents(id) ON DELETE CASCADE ON UPDATE CASCADE NULL,
    staff_name VARCHAR(255) NULL, -- <-- ADDED THIS
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
    fields JSON DEFAULT '[]',
    available BOOLEAN DEFAULT true,
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
    status_id INT REFERENCES request_status(id) ON DELETE SET NULL,
    payment_status TEXT CHECK (payment_status IN ('Paid', 'Unpaid')) DEFAULT 'Unpaid',
    form_data JSONB,
    request_file BYTEA,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==============================
--  TABLE: requests_status
-- ==============================
CREATE TABLE IF NOT EXISTS request_status (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);

-- ==============================
--  TABLE: requests_status feed
-- ==============================
INSERT INTO request_status (name) VALUES
('pending'),
('processing'),
('ready'),
('released'),
('rejected'),
('cancelled')
ON CONFLICT (name) DO NOTHING;

-- =============================================================================
-- Tables for Equipment Borrowing
-- =============================================================================

-- 1. The master list of all borrowable equipment
CREATE TABLE IF NOT EXISTS equipment_inventory (
    id SERIAL PRIMARY KEY,
    name VARCHAR(128) NOT NULL UNIQUE,
    total_quantity INTEGER NOT NULL DEFAULT 0,
    available_quantity INTEGER NOT NULL DEFAULT 0,
    rate DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    rate_per VARCHAR(16) DEFAULT 'day'
);

-- 2. The main table for each individual request
CREATE TABLE IF NOT EXISTS equipment_requests (
    id SERIAL PRIMARY KEY,
    resident_id SMALLINT REFERENCES residents(id) ON DELETE SET NULL,
    borrower_name VARCHAR(255) NOT NULL,
    contact_number VARCHAR(16),
    purpose VARCHAR(255),
    notes TEXT,
    borrow_date TIMESTAMPTZ NOT NULL,
    return_date TIMESTAMPTZ NOT NULL,
    total_cost DECIMAL(10, 2) NOT NULL,
    requested_via VARCHAR(64),
    status VARCHAR(32) DEFAULT 'Pending',
    paid BOOLEAN DEFAULT FALSE,
    refunded BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT (NOW()),
    updated_at TIMESTAMPTZ DEFAULT (NOW())
);

-- 3. The "join table" that links a request to its items
CREATE TABLE IF NOT EXISTS equipment_request_items (
    id SERIAL PRIMARY KEY,
    request_id INTEGER NOT NULL REFERENCES equipment_requests(id) ON DELETE CASCADE,
    item_id INTEGER NOT NULL REFERENCES equipment_inventory(id) ON DELETE RESTRICT,
    quantity INTEGER NOT NULL DEFAULT 1
);

-- =============================================================================
-- Pre-fill Equipment Inventory Data
-- =============================================================================
-- This will insert the 4 items from your admin panel's dummy data.
-- 'ON CONFLICT (name) DO NOTHING' prevents errors if you run the script twice.

INSERT INTO equipment_inventory (name, total_quantity, available_quantity, rate, rate_per)
VALUES
    ('Event Tent', 10, 8, 500.00, 'day'),
    ('Monobloc Chairs', 200, 150, 10.00, 'day'),
    ('Folding Tables', 5, 5, 1500.00, 'day'),
    ('Sound System', 3, 2, 300.00, 'day')
ON CONFLICT (name) DO NOTHING;