# ERD (texto) - Entidades principais

Clients
- id
- name
- document (CNPJ/CPF)
- contact
- created_at, updated_at

Projects
- id
- client_id
- name
- description
- location (json)
- created_at, updated_at

Licenses
- id
- project_id
- number
- issuer
- issued_at
- expires_at
- type
- status
- metadata (jsonb)
- created_at, updated_at

AVCBs
- id
- license_id (nullable)
- project_id
- ppci_number
- issued_at
- expires_at
- has_compensatory_measures (boolean)
- status
- metadata (jsonb)

Conditionals
- id
- license_id
- description
- due_date
- frequency (once, monthly, quarterly, yearly)
- status
- created_at, updated_at

Conditional Executions (history)
- id
- conditional_id
- executed_by
- executed_at
- status
- evidence_attachment_id

Processes
- id
- license_id
- protocol_number
- current_status
- timeline (jsonb)

Attachments
- id
- attachable_type
- attachable_id
- filename
- path
- mime
- size
- uploaded_by
- created_at

Users / Roles / Permissions
- users
- roles
- permissions (spatie tables)

Audits
- id
- user_id
- auditable_type
- auditable_id
- action
- old_values (jsonb)
- new_values (jsonb)
- created_at

Calendar Events
- id
- related_type
- related_id
- title
- start_at
- end_at
- color
- reminder_days (json)

Observação: usar chaves estrangeiras e índices conforme necessidade.
