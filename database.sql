DROP TABLE IF EXISTS tickets;

CREATE TABLE tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket_number TEXT UNIQUE,
    lark_email TEXT,
    campaign TEXT,
    impact TEXT,
    request TEXT,
    description TEXT,
    priority TEXT,
    attachment_path TEXT,
    status TEXT DEFAULT 'Open',
    submission_time TEXT
);
