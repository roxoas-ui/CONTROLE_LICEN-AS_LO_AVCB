-- Schema inicial (PostgreSQL)

CREATE TABLE clients (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    document VARCHAR(20),
    contact JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE projects (
    id BIGSERIAL PRIMARY KEY,
    client_id BIGINT REFERENCES clients(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    location JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE licenses (
    id BIGSERIAL PRIMARY KEY,
    project_id BIGINT REFERENCES projects(id) ON DELETE CASCADE,
    number VARCHAR(100) NOT NULL,
    issuer VARCHAR(255) NOT NULL,
    issued_at DATE,
    expires_at DATE,
    type VARCHAR(100),
    status VARCHAR(50),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE avcbs (
    id BIGSERIAL PRIMARY KEY,
    license_id BIGINT REFERENCES licenses(id) ON DELETE SET NULL,
    project_id BIGINT REFERENCES projects(id) ON DELETE CASCADE,
    ppci_number VARCHAR(100),
    issued_at DATE,
    expires_at DATE,
    has_compensatory_measures BOOLEAN DEFAULT false,
    status VARCHAR(50),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE conditionals (
    id BIGSERIAL PRIMARY KEY,
    license_id BIGINT REFERENCES licenses(id) ON DELETE CASCADE,
    description TEXT,
    due_date DATE,
    frequency VARCHAR(20),
    status VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE conditional_executions (
    id BIGSERIAL PRIMARY KEY,
    conditional_id BIGINT REFERENCES conditionals(id) ON DELETE CASCADE,
    executed_by BIGINT,
    executed_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20),
    evidence_attachment_id BIGINT,
    notes TEXT
);

CREATE TABLE processes (
    id BIGSERIAL PRIMARY KEY,
    license_id BIGINT REFERENCES licenses(id) ON DELETE CASCADE,
    protocol_number VARCHAR(100),
    current_status VARCHAR(100),
    timeline JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE attachments (
    id BIGSERIAL PRIMARY KEY,
    attachable_type VARCHAR(100) NOT NULL,
    attachable_id BIGINT NOT NULL,
    filename VARCHAR(255) NOT NULL,
    path TEXT NOT NULL,
    mime VARCHAR(100),
    size BIGINT,
    uploaded_by BIGINT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Users, roles and permissions (recommended to use spatie tables via package)

CREATE TABLE audits (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT,
    auditable_type VARCHAR(100),
    auditable_id BIGINT,
    action VARCHAR(50),
    old_values JSONB,
    new_values JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE calendar_events (
    id BIGSERIAL PRIMARY KEY,
    related_type VARCHAR(100),
    related_id BIGINT,
    title VARCHAR(255),
    start_at TIMESTAMP WITH TIME ZONE,
    end_at TIMESTAMP WITH TIME ZONE,
    color VARCHAR(20),
    reminder_days JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
