-- HONEYPOT SYSTEM BACKUP
-- FAKE DATA ONLY

CREATE TABLE users (
    user_id INT,
    username VARCHAR(50),
    role VARCHAR(30)
);

INSERT INTO users VALUES
(1, 'admin_honeypot', 'administrator'),
(2, 'backup_admin', 'administrator'),
(3, 'employee_demo', 'employee');

CREATE TABLE audit_logs (
    log_id INT,
    username VARCHAR(50),
    action VARCHAR(100)
);

INSERT INTO audit_logs VALUES
(1, 'admin_honeypot', 'LOGIN'),
(2, 'employee_demo', 'VIEW_PROFILE');