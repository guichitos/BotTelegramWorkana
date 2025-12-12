-- Add a toggle for the general Workana web scraper.
INSERT INTO variables (name, value)
SELECT 'general_scraper_enabled', 'true'
WHERE NOT EXISTS (
    SELECT 1 FROM variables WHERE name = 'general_scraper_enabled'
);
