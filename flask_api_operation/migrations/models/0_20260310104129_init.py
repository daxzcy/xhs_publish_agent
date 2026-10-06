from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `t_models` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `name` VARCHAR(100) NOT NULL,
    `type` VARCHAR(50) NOT NULL,
    `version` VARCHAR(50),
    `description` LONGTEXT,
    `status` INT NOT NULL DEFAULT 1,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6)
) CHARACTER SET utf8mb4 COMMENT='AI 模型表 t_models。';
CREATE TABLE IF NOT EXISTS `t_publish_images` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `publish_id` INT NOT NULL,
    `image_id` INT NOT NULL,
    `image_type` SMALLINT NOT NULL DEFAULT 1,
    `sort_order` INT NOT NULL DEFAULT 1,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6)
) CHARACTER SET utf8mb4 COMMENT='发布内容图片表 t_publish_images。';
CREATE TABLE IF NOT EXISTS `t_publish_records` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `user_id` INT,
    `title_id` INT NOT NULL,
    `platform` SMALLINT NOT NULL,
    `publish_status` SMALLINT NOT NULL DEFAULT 0,
    `publish_time` DATETIME(6),
    `content` LONGTEXT,
    `view_count` INT NOT NULL DEFAULT 0,
    `like_count` INT NOT NULL DEFAULT 0,
    `comment_count` INT NOT NULL DEFAULT 0,
    `share_count` INT NOT NULL DEFAULT 0,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6)
) CHARACTER SET utf8mb4 COMMENT='发布记录表 t_publish_records。';
CREATE TABLE IF NOT EXISTS `t_sections` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `user_id` INT NOT NULL,
    `source_name` VARCHAR(255),
    `name` VARCHAR(100) NOT NULL,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6)
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `t_style` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `name` VARCHAR(255),
    `fengge` LONGTEXT,
    `create_time` DATETIME(6)
) CHARACTER SET utf8mb4 COMMENT='风格表 t_style。';
CREATE TABLE IF NOT EXISTS `t_titles` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `section_id` INT NOT NULL,
    `title` VARCHAR(255) NOT NULL,
    `sort_order` INT NOT NULL,
    `content` VARCHAR(255),
    `status` VARCHAR(255),
    `view_count` VARCHAR(255),
    `like_count` VARCHAR(255),
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6)
) CHARACTER SET utf8mb4 COMMENT='标题表 t_titles。';
CREATE TABLE IF NOT EXISTS `t_title_images` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `user_id` INT,
    `title_id` INT NOT NULL,
    `image_url` VARCHAR(500) NOT NULL,
    `image_type` SMALLINT NOT NULL DEFAULT 0,
    `sort_order` INT NOT NULL DEFAULT 0,
    `file_size` INT,
    `width` INT,
    `height` INT,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6)
) CHARACTER SET utf8mb4 COMMENT='标题图片表 t_title_images。image_type: 0=正文图 1=封面图 2=缩略图';
CREATE TABLE IF NOT EXISTS `t_users` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `username` VARCHAR(50) NOT NULL UNIQUE,
    `password` VARCHAR(255) NOT NULL,
    `name` VARCHAR(50) NOT NULL,
    `department` VARCHAR(50),
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6)
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `aerich` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `version` VARCHAR(255) NOT NULL,
    `app` VARCHAR(100) NOT NULL,
    `content` JSON NOT NULL
) CHARACTER SET utf8mb4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """


MODELS_STATE = (
    "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"
)
