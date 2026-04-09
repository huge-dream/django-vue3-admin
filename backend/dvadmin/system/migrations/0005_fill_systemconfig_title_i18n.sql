/*
Fill SystemConfig title_i18n fields from existing title values
SQL reference (Django uses RunPython instead):

UPDATE `dvadmin_system_config`
SET `title_en` = `title`, `title_zh_tw` = `title`
WHERE `title_en` IS NULL AND `title_zh_tw` IS NULL;
*/
