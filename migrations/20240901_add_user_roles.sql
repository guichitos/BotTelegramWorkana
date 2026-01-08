-- Add a role column to distinguish admin/users in bot_users.

START TRANSACTION;

ALTER TABLE bot_users
    ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'user';

COMMIT;
