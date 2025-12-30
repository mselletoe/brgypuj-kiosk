-- ========================================================
-- 1. SEQUENCES & INDEPENDENT TABLES (Parent Tables)
-- ========================================================

CREATE SEQUENCE IF NOT EXISTS global_transaction_seq START 1;

-- ==============================
-- puroks
-- ==============================
CREATE TABLE IF NOT EXISTS puroks (
    id SMALLSERIAL PRIMARY KEY,
    purok_name VARCHAR(16) NOT NULL UNIQUE
);

-- ==============================
-- residents
-- ==============================
CREATE TABLE IF NOT EXISTS residents (
    id SERIAL PRIMARY KEY,
    last_name VARCHAR(128) NOT NULL,
    first_name VARCHAR(128) NOT NULL,
    middle_name VARCHAR(128),
    suffix VARCHAR(8),
    gender VARCHAR(10) NOT NULL CHECK (gender IN ('male', 'female', 'other')),
    birthdate DATE NOT NULL,
    residency_start_date DATE NOT NULL DEFAULT CURRENT_DATE,
    email VARCHAR(255) UNIQUE,
    phone_number VARCHAR(15),
    rfid_pin VARCHAR(255),
    registered_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ==============================
-- document_types
-- ==============================
CREATE TABLE IF NOT EXISTS document_types (
    id SMALLSERIAL PRIMARY KEY,
    doctype_name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) DEFAULT 0.00,
    file BYTEA, 
    fields JSON DEFAULT '[]', 
    is_available BOOLEAN DEFAULT TRUE
);

-- ==============================
-- equipment_inventory
-- ==============================
CREATE TABLE IF NOT EXISTS equipment_inventory (
    id SERIAL PRIMARY KEY,
    name VARCHAR(128) NOT NULL UNIQUE,
    total_quantity INTEGER NOT NULL DEFAULT 0,
    available_quantity INTEGER NOT NULL DEFAULT 0,
    rate_per_day DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    
    CONSTRAINT chk_available_range CHECK (available_quantity >= 0 AND available_quantity <= total_quantity)
);

-- ==============================
-- announcements
-- ==============================
CREATE TABLE IF NOT EXISTS announcements (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    event_date DATE NOT NULL,
    event_time VARCHAR(32),
    location VARCHAR(255) NOT NULL,
    image BYTEA,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- ========================================================
-- 2. RESIDENT SUB-DATA (Dependent on Residents)
-- ========================================================

-- ==============================
-- addresses
-- ==============================
CREATE TABLE IF NOT EXISTS addresses (
    id SERIAL PRIMARY KEY,
    resident_id INTEGER NOT NULL,
    house_no_street VARCHAR(255) NOT NULL,
    purok_id SMALLINT NOT NULL,
    barangay VARCHAR(64) DEFAULT 'YourBarangay',
    municipality VARCHAR(16) DEFAULT 'YourCity',
    province VARCHAR(16) DEFAULT 'YourProvince',
    region VARCHAR(64) DEFAULT 'Region III',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_current BOOLEAN NOT NULL DEFAULT TRUE,

    -- Foreign Keys
    CONSTRAINT fk_resident_address FOREIGN KEY (resident_id) 
        REFERENCES residents(id) ON DELETE CASCADE,
    CONSTRAINT fk_purok_address FOREIGN KEY (purok_id) 
        REFERENCES puroks(id) ON DELETE RESTRICT
);

-- ==============================
-- resident_rfid
-- ==============================
CREATE TABLE IF NOT EXISTS resident_rfid (
    id SERIAL PRIMARY KEY,
    resident_id INTEGER NOT NULL,
    rfid_uid VARCHAR(16) UNIQUE NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    -- Foreign Keys
    CONSTRAINT fk_resident_rfid FOREIGN KEY (resident_id) 
        REFERENCES residents(id) ON DELETE CASCADE
);

-- ==============================
-- admin
-- ==============================
CREATE TABLE IF NOT EXISTS admin (
    id SMALLSERIAL PRIMARY KEY,
    resident_id INTEGER NOT NULL, 
    username VARCHAR(255) UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role VARCHAR(50) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Foreign Keys
    CONSTRAINT fk_admin_resident FOREIGN KEY (resident_id) 
        REFERENCES residents(id) ON DELETE CASCADE
);

-- ==============================
-- feedbacks
-- ==============================
CREATE TABLE IF NOT EXISTS feedbacks (
    id SERIAL PRIMARY KEY,
    resident_id INTEGER, 
    category VARCHAR(50) NOT NULL 
        CHECK (category IN (
            'Service Quality', 
            'Interface Design', 
            'System Speed', 
            'Accessibility', 
            'General Experience'
        )),
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    additional_comments TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT fk_feedback_resident FOREIGN KEY (resident_id) 
        REFERENCES residents(id) ON DELETE SET NULL
);

-- ==============================
-- rfid_reports
-- ==============================
CREATE TABLE IF NOT EXISTS rfid_reports (
    id SERIAL PRIMARY KEY,
    resident_id INTEGER, 
    status VARCHAR(32) DEFAULT 'Pending' 
        CHECK (status IN ('Pending', 'Acknowledged')),
    created_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT fk_rfid_report_resident FOREIGN KEY (resident_id) 
        REFERENCES residents(id) ON DELETE CASCADE
);

-- ========================================================
-- 3. REQUESTS & TRANSACTIONS
-- ========================================================

-- ==============================
-- document_requests
-- ==============================
CREATE TABLE IF NOT EXISTS document_requests (
    id SERIAL PRIMARY KEY,
    transaction_no VARCHAR(20) UNIQUE NOT NULL 
        DEFAULT ('DR-' || LPAD(nextval('global_transaction_seq')::text, 5, '0')),
    resident_id INTEGER NOT NULL,
    doctype_id INT NOT NULL,
    processed_by SMALLINT,
    status VARCHAR(32) DEFAULT 'Pending' 
        CHECK (status IN ('Pending', 'Approved', 'Ready', 'Released', 'Rejected')),
    payment_status VARCHAR(20) DEFAULT 'unpaid' 
        CHECK (payment_status IN ('unpaid', 'paid')),
    form_data JSONB,
    request_file_path TEXT,
    requested_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    -- Foreign Keys
    CONSTRAINT fk_res_doc FOREIGN KEY (resident_id) REFERENCES residents(id) ON DELETE CASCADE,
    CONSTRAINT fk_type_doc FOREIGN KEY (doctype_id) REFERENCES document_types(id),
    CONSTRAINT fk_admin_doc FOREIGN KEY (processed_by) REFERENCES admin(id) ON DELETE SET NULL
);

-- ==============================
-- equipment_requests
-- ==============================
CREATE TABLE IF NOT EXISTS equipment_requests (
    id SERIAL PRIMARY KEY,
    transaction_no VARCHAR(20) UNIQUE NOT NULL 
        DEFAULT ('ER-' || LPAD(nextval('global_transaction_seq')::text, 5, '0')),
    resident_id INTEGER, 
    borrower_name VARCHAR(255) NOT NULL,
    contact_person VARCHAR(255),
    contact_number VARCHAR(16),
    purpose VARCHAR(255),
    status VARCHAR(32) DEFAULT 'Pending' 
        CHECK (status IN ('Pending', 'Approved', 'Picked-Up', 'Returned', 'Rejected')),
    notes TEXT,
    borrow_date TIMESTAMPTZ NOT NULL,
    return_date TIMESTAMPTZ NOT NULL,
    returned_at TIMESTAMPTZ,
    total_cost DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    payment_status VARCHAR(20) DEFAULT 'unpaid' 
        CHECK (payment_status IN ('unpaid', 'paid')),
    is_refunded BOOLEAN DEFAULT FALSE,
    requested_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    -- Foreign Keys
    CONSTRAINT fk_res_equip FOREIGN KEY (resident_id) 
        REFERENCES residents(id) ON DELETE SET NULL
);

-- ==============================
-- equipment_request_items
-- ==============================
CREATE TABLE IF NOT EXISTS equipment_request_items (
    id SERIAL PRIMARY KEY,
    equipment_request_id INTEGER NOT NULL REFERENCES equipment_requests(id) ON DELETE CASCADE,
    item_id INTEGER NOT NULL REFERENCES equipment_inventory(id) ON DELETE RESTRICT,
    quantity INTEGER NOT NULL DEFAULT 1 CHECK (quantity > 0)
);



-- ========================================================
-- 4. PERFORMANCE INDEXES
-- ========================================================
-- Search residents by name
CREATE INDEX IF NOT EXISTS idx_residents_last_name ON residents(last_name);

-- Ensure only one current address per resident
CREATE UNIQUE INDEX IF NOT EXISTS idx_one_current_address_per_resident
ON addresses (resident_id) WHERE is_current IS TRUE;

-- Speed up RFID login
CREATE INDEX IF NOT EXISTS idx_rfid_active_lookup ON resident_rfid(rfid_uid) WHERE is_active IS TRUE;

-- Lookup admin accounts by resident
CREATE INDEX IF NOT EXISTS idx_admin_resident_lookup ON admin(resident_id);

-- Filter requests by status (for Dashboard)
CREATE INDEX IF NOT EXISTS idx_doc_requests_status ON document_requests(status);
CREATE INDEX IF NOT EXISTS idx_equip_req_status ON equipment_requests(status);

-- Index for the Kiosk Home Screen (Upcoming events first)
CREATE INDEX IF NOT EXISTS idx_announcements_date ON announcements(event_date) 
WHERE is_active IS TRUE;

-- Indexes for Admin Dashboard performance
CREATE INDEX IF NOT EXISTS idx_feedback_category ON feedbacks(category);
CREATE INDEX IF NOT EXISTS idx_rfid_report_status ON rfid_reports(status);