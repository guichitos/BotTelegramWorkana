-- Migration: Add project skill storage
-- Purpose: persist the skills scraped from Workana project cards

START TRANSACTION;

-- Table to store the skills associated to each scraped project
CREATE TABLE IF NOT EXISTS project_skills (
    id           INT UNSIGNED NOT NULL AUTO_INCREMENT,
    project_id   INT NOT NULL,
    skill_name   VARCHAR(255) NOT NULL,   -- Visible text inside the <h3> tag (e.g., "Fotografía Digital")
    skill_slug   VARCHAR(128) NOT NULL,   -- Slug extracted from the href query param (e.g., "digital-photography")
    skill_href   VARCHAR(512) DEFAULT NULL, -- Full href as scraped (optional, to preserve source URL)
    created_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT fk_project_skills_project FOREIGN KEY (project_id)
        REFERENCES proyectos(id) ON DELETE CASCADE,
    CONSTRAINT uniq_project_skill_slug UNIQUE (project_id, skill_slug)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Helpful index to query by slug across projects
CREATE INDEX idx_project_skills_slug ON project_skills (skill_slug);

COMMIT;
