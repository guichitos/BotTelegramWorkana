-- 20240520_rename_schema_to_english.sql
-- Rename core tables and columns to English equivalents

START TRANSACTION;

-- Drop foreign keys that reference Spanish table names
ALTER TABLE project_skills DROP FOREIGN KEY fk_project_skills_project;
ALTER TABLE proyectos DROP FOREIGN KEY fk_proyectos_usuario;
ALTER TABLE user_skills DROP FOREIGN KEY fk_user_skills_user;

-- Rename tables
RENAME TABLE usuarios_bot TO bot_users;
RENAME TABLE proyectos TO projects;

-- Rename columns in bot_users
ALTER TABLE bot_users
    CHANGE COLUMN nombre_usuario username VARCHAR(255) NOT NULL,
    CHANGE COLUMN activo active TINYINT(1) DEFAULT 1,
    CHANGE COLUMN creado_en created_at DATETIME NOT NULL DEFAULT current_timestamp();

-- Rename columns in projects
ALTER TABLE projects
    CHANGE COLUMN fecha_hora posted_at DATETIME NOT NULL DEFAULT current_timestamp(),
    CHANGE COLUMN titulo title VARCHAR(255) NOT NULL,
    CHANGE COLUMN descripcion description TEXT NOT NULL,
    CHANGE COLUMN enlace url VARCHAR(255) NOT NULL;

-- Recreate foreign keys pointing to the new table names
ALTER TABLE projects
    ADD CONSTRAINT fk_projects_user FOREIGN KEY (user_id) REFERENCES bot_users(id) ON DELETE CASCADE;

ALTER TABLE user_skills
    ADD CONSTRAINT fk_user_skills_user FOREIGN KEY (user_id) REFERENCES bot_users(id) ON DELETE CASCADE;

ALTER TABLE project_skills
    ADD CONSTRAINT fk_project_skills_project FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE;

COMMIT;
