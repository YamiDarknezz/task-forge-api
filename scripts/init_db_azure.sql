-- TaskForge API - Azure SQL Database Schema
-- Database: taskforge_db
-- Server: yamidarknezz.database.windows.net

-- ===================================
-- Create Tables
-- ===================================

-- Roles Table
CREATE TABLE roles (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(50) NOT NULL UNIQUE,
    description NVARCHAR(255),
    created_at DATETIME2 DEFAULT GETUTCDATE()
);

-- Users Table
CREATE TABLE users (
    id INT IDENTITY(1,1) PRIMARY KEY,
    username NVARCHAR(80) NOT NULL UNIQUE,
    email NVARCHAR(120) NOT NULL UNIQUE,
    password_hash NVARCHAR(255) NOT NULL,
    first_name NVARCHAR(50),
    last_name NVARCHAR(50),
    is_active BIT DEFAULT 1,
    role_id INT NOT NULL,
    created_at DATETIME2 DEFAULT GETUTCDATE(),
    updated_at DATETIME2 DEFAULT GETUTCDATE(),
    CONSTRAINT FK_User_Role FOREIGN KEY (role_id) REFERENCES roles(id)
);

-- Refresh Tokens Table
CREATE TABLE refresh_tokens (
    id INT IDENTITY(1,1) PRIMARY KEY,
    token NVARCHAR(500) NOT NULL UNIQUE,
    user_id INT NOT NULL,
    is_revoked BIT DEFAULT 0,
    expires_at DATETIME2 NOT NULL,
    created_at DATETIME2 DEFAULT GETUTCDATE(),
    CONSTRAINT FK_RefreshToken_User FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Tasks Table
CREATE TABLE tasks (
    id INT IDENTITY(1,1) PRIMARY KEY,
    title NVARCHAR(200) NOT NULL,
    description NVARCHAR(MAX),
    status NVARCHAR(50) DEFAULT 'pending' NOT NULL,
    priority NVARCHAR(50) DEFAULT 'medium' NOT NULL,
    due_date DATETIME2,
    completed_at DATETIME2,
    user_id INT NOT NULL,
    created_at DATETIME2 DEFAULT GETUTCDATE(),
    updated_at DATETIME2 DEFAULT GETUTCDATE(),
    CONSTRAINT FK_Task_User FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT CHK_Task_Status CHECK (status IN ('pending', 'in_progress', 'completed', 'cancelled')),
    CONSTRAINT CHK_Task_Priority CHECK (priority IN ('low', 'medium', 'high', 'urgent'))
);

-- Tags Table
CREATE TABLE tags (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(50) NOT NULL UNIQUE,
    color NVARCHAR(7) DEFAULT '#808080',
    description NVARCHAR(255),
    created_at DATETIME2 DEFAULT GETUTCDATE(),
    updated_at DATETIME2 DEFAULT GETUTCDATE()
);

-- Task-Tags Junction Table (Many-to-Many)
CREATE TABLE task_tags (
    task_id INT NOT NULL,
    tag_id INT NOT NULL,
    created_at DATETIME2 DEFAULT GETUTCDATE(),
    PRIMARY KEY (task_id, tag_id),
    CONSTRAINT FK_TaskTag_Task FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
    CONSTRAINT FK_TaskTag_Tag FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

-- ===================================
-- Create Indexes for Performance
-- ===================================

CREATE INDEX IDX_Users_Username ON users(username);
CREATE INDEX IDX_Users_Email ON users(email);
CREATE INDEX IDX_Users_RoleId ON users(role_id);
CREATE INDEX IDX_RefreshTokens_Token ON refresh_tokens(token);
CREATE INDEX IDX_RefreshTokens_UserId ON refresh_tokens(user_id);
CREATE INDEX IDX_Tasks_UserId ON tasks(user_id);
CREATE INDEX IDX_Tasks_Status ON tasks(status);
CREATE INDEX IDX_Tasks_Priority ON tasks(priority);
CREATE INDEX IDX_Tasks_DueDate ON tasks(due_date);
CREATE INDEX IDX_Tags_Name ON tags(name);

-- ===================================
-- Insert Default Roles
-- ===================================

INSERT INTO roles (name, description) VALUES
('admin', 'Administrator role with full access'),
('user', 'Standard user role with limited access');

-- ===================================
-- Insert Default Admin User
-- ===================================
-- Password: Admin123! (bcrypt hashed)
-- NOTE: This is a DEVELOPMENT password. Change it immediately in production!
-- You can change it using the /auth/change-password endpoint or scripts/reset_admin_password.py

INSERT INTO users (username, email, password_hash, first_name, last_name, role_id, is_active)
VALUES (
    'admin',
    'admin@taskforge.com',
    '$2b$12$FZcQR4FNLppbydmvfPDHdOx3zsakQ7xmphqt0VjcyO1dXyeVU3RAu',
    'System',
    'Administrator',
    (SELECT id FROM roles WHERE name = 'admin'),
    1
);

-- ===================================
-- Insert Sample Tags
-- ===================================

INSERT INTO tags (name, color, description) VALUES
('Work', '#FF5733', 'Work-related tasks'),
('Personal', '#33FF57', 'Personal tasks'),
('Urgent', '#FF3333', 'Urgent tasks'),
('Important', '#3357FF', 'Important tasks'),
('Later', '#808080', 'Tasks for later');

-- ===================================
-- Create Stored Procedures (Optional)
-- ===================================

-- Procedure to clean up expired refresh tokens
CREATE PROCEDURE CleanupExpiredTokens
AS
BEGIN
    DELETE FROM refresh_tokens WHERE expires_at < GETUTCDATE();
END;
GO

-- Procedure to get user statistics
CREATE PROCEDURE GetUserTaskStats
    @UserId INT
AS
BEGIN
    SELECT
        COUNT(*) AS total_tasks,
        SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) AS completed_tasks,
        SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) AS pending_tasks,
        SUM(CASE WHEN status = 'in_progress' THEN 1 ELSE 0 END) AS in_progress_tasks,
        SUM(CASE WHEN due_date < GETUTCDATE() AND status != 'completed' THEN 1 ELSE 0 END) AS overdue_tasks
    FROM tasks
    WHERE user_id = @UserId;
END;
GO

-- ===================================
-- Create Trigger for Updated_At
-- ===================================

-- Trigger for Users table
CREATE TRIGGER TR_Users_UpdatedAt
ON users
AFTER UPDATE
AS
BEGIN
    UPDATE users
    SET updated_at = GETUTCDATE()
    FROM users u
    INNER JOIN inserted i ON u.id = i.id
END;
GO

-- Trigger for Tasks table
CREATE TRIGGER TR_Tasks_UpdatedAt
ON tasks
AFTER UPDATE
AS
BEGIN
    UPDATE tasks
    SET updated_at = GETUTCDATE()
    FROM tasks t
    INNER JOIN inserted i ON t.id = i.id
END;
GO

-- Trigger for Tags table
CREATE TRIGGER TR_Tags_UpdatedAt
ON tags
AFTER UPDATE
AS
BEGIN
    UPDATE tags
    SET updated_at = GETUTCDATE()
    FROM tags tg
    INNER JOIN inserted i ON tg.id = i.id
END;
GO

-- ===================================
-- Database Setup Complete
-- ===================================

-- Verification Queries
SELECT 'Roles:' AS Info, COUNT(*) AS Count FROM roles
UNION ALL
SELECT 'Users:', COUNT(*) FROM users
UNION ALL
SELECT 'Tags:', COUNT(*) FROM tags
UNION ALL
SELECT 'Tasks:', COUNT(*) FROM tasks;
