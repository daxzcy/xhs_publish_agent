from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `t_xhs_accounts` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `user_id` INT,
    `name` VARCHAR(100),
    `a1` VARCHAR(255) NOT NULL,
    `web_session` VARCHAR(255) NOT NULL,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6)
) CHARACTER SET utf8mb4 COMMENT='小红书账号表 t_xhs_accounts。';

CREATE TABLE IF NOT EXISTS `t_material_text` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `user_id` INT,
    `title` VARCHAR(255),
    `content` LONGTEXT,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6)
) CHARACTER SET utf8mb4 COMMENT='素材文案表 t_material_text。';

CREATE TABLE IF NOT EXISTS `t_material_image` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `user_id` INT,
    `image_url` VARCHAR(255) NOT NULL,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6)
) CHARACTER SET utf8mb4 COMMENT='素材图片表 t_material_image。';

ALTER TABLE `t_publish_images` ADD COLUMN IF NOT EXISTS `image_url` VARCHAR(255) DEFAULT '' AFTER `image_id`;

ALTER TABLE `t_publish_records` ADD COLUMN IF NOT EXISTS `title_title` VARCHAR(255) DEFAULT '' AFTER `title_id`;
ALTER TABLE `t_publish_records` ADD COLUMN IF NOT EXISTS `xhs_id` INT DEFAULT 0 AFTER `title_title`;
ALTER TABLE `t_publish_records` ADD COLUMN IF NOT EXISTS `xhs_name` VARCHAR(100) DEFAULT '' AFTER `xhs_id`;
ALTER TABLE `t_publish_records` ADD COLUMN IF NOT EXISTS `note_url` VARCHAR(255) DEFAULT '' AFTER `xhs_name`;
ALTER TABLE `t_publish_records` ADD COLUMN IF NOT EXISTS `complete_url` VARCHAR(255) DEFAULT '' AFTER `note_url`;
ALTER TABLE `t_publish_records` ADD COLUMN IF NOT EXISTS `collected_count` INT DEFAULT 0 AFTER `share_count`;
"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS `t_xhs_accounts`;
        DROP TABLE IF EXISTS `t_material_text`;
        DROP TABLE IF EXISTS `t_material_image`;
    """
