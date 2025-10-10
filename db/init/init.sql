-- ==============================
--  TABLE: residents
-- ==============================
CREATE TABLE IF NOT EXISTS residents (
    id SERIAL PRIMARY KEY,
    last_name VARCHAR(128),
    first_name VARCHAR(128),
    middle_name VARCHAR(128),
    suffix VARCHAR(8),
    gender TEXT CHECK (gender IN ('male', 'female')),
    birthdate DATE,
    years_residency INT,
    email VARCHAR(128) UNIQUE,
    phone_number VARCHAR(16),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==============================
--  TABLE: addresses
-- ==============================
CREATE TABLE IF NOT EXISTS addresses (
    id SERIAL PRIMARY KEY,
    resident_id INT,
    unit_blk_street TEXT,
    purok VARCHAR(16),
    barangay VARCHAR(128),
    municipality VARCHAR(16),
    province VARCHAR(16),
    region VARCHAR(32),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_current BOOLEAN DEFAULT TRUE,
    CONSTRAINT fk_addresses_resident
        FOREIGN KEY (resident_id)
        REFERENCES residents(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- ==============================
--  TABLE: rfid_uid
-- ==============================
CREATE TABLE IF NOT EXISTS rfid_uid (
    id SERIAL PRIMARY KEY,
    resident_id INT,
    rfid_uid CHAR(9) UNIQUE,
    status TEXT CHECK (status IN ('active', 'inactive')) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    CONSTRAINT fk_rfid_resident
        FOREIGN KEY (resident_id)
        REFERENCES residents(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- ==============================
--  TABLE: brgy_staff
-- ==============================
CREATE TABLE IF NOT EXISTS brgy_staff (
    id SERIAL PRIMARY KEY,
    resident_id INT,
    email VARCHAR(128) UNIQUE,
    password VARCHAR(255),
    role VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    CONSTRAINT fk_staff_resident
        FOREIGN KEY (resident_id)
        REFERENCES residents(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- ==============================
--  TABLE: templates
-- ==============================
CREATE TABLE IF NOT EXISTS templates (
    id SERIAL PRIMARY KEY,
    template_name VARCHAR(255),
    description TEXT,
    file BYTEA,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==============================
--  TABLE: request_types
-- ==============================
CREATE TABLE IF NOT EXISTS request_types (
    id SERIAL PRIMARY KEY,
    request_type_name VARCHAR(255),
    description TEXT,
    template_id INT,
    status TEXT CHECK (status IN ('active', 'inactive')) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_reqtype_template
        FOREIGN KEY (template_id)
        REFERENCES templates(id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);

-- ==============================
--  TABLE: requests
-- ==============================
CREATE TABLE IF NOT EXISTS requests (
    id SERIAL PRIMARY KEY,
    resident_id INT,
    request_type_id INT,
    processed_by INT NULL,
    rejected_by INT NULL,
    purpose TEXT,
    status TEXT CHECK (status IN ('pending', 'processing', 'ready', 'released', 'rejected', 'cancelled')) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_requests_resident
        FOREIGN KEY (resident_id)
        REFERENCES residents(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_requests_type
        FOREIGN KEY (request_type_id)
        REFERENCES request_types(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_requests_processed
        FOREIGN KEY (processed_by)
        REFERENCES brgy_staff(id)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    CONSTRAINT fk_requests_rejected
        FOREIGN KEY (rejected_by)
        REFERENCES brgy_staff(id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);