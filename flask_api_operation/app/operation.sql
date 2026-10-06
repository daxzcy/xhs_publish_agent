-- Active: 1778482113220@@127.0.0.1@3306@xhs_operation
/*
 Navicat MySQL Data Transfer

 Source Server         : MySQL
 Source Server Type    : MySQL
 Source Server Version : 80012 (8.0.12)
 Source Host           : localhost:3306
 Source Schema         : xhs_operation

 Target Server Type    : MySQL
 Target Server Version : 80012 (8.0.12)
 File Encoding         : 65001

 Date: 27/03/2026 14:21:10
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for t_generation_tasks
-- ----------------------------
DROP TABLE IF EXISTS `t_generation_tasks`;
CREATE TABLE `t_generation_tasks`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '生成任务ID',
  `user_id` int(11) NOT NULL COMMENT '用户ID（逻辑关联 t_users.id）',
  `model_id` int(11) NOT NULL COMMENT '模型ID（逻辑关联 t_models.id）',
  `prompt` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '生成提示词',
  `result_url` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '生成结果地址（图片URL等）',
  `status` tinyint(4) NULL DEFAULT 0 COMMENT '任务状态：0=处理中，1=成功，2=失败',
  `error_message` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '失败原因',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_user_id`(`user_id` ASC) USING BTREE,
  INDEX `idx_model_id`(`model_id` ASC) USING BTREE,
  INDEX `idx_status`(`status` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '模型生成任务表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of t_generation_tasks
-- ----------------------------

-- ----------------------------
-- Table structure for t_models
-- ----------------------------
DROP TABLE IF EXISTS `t_models`;
CREATE TABLE `t_models`  (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '模型唯一ID',
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '模型名称，例如 Stable Diffusion',
  `type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '模型类型：text=文本生成，image=图像生成',
  `version` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '模型版本',
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '模型描述',
  `status` tinyint(4) NULL DEFAULT 1 COMMENT '模型状态：1=可用，0=停用',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_type`(`type` ASC) USING BTREE,
  INDEX `idx_status`(`status` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 2 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = 'AI模型表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of t_models
-- ----------------------------
INSERT INTO `t_models` VALUES (1, 'wan2.6-t2i', 'image', '2.6', '万相2.6\r\n\r\n支持在总像素面积与宽高比约束内，自由选尺寸（同wan2.5）', 1, '2026-02-22 17:38:38', '2026-02-22 17:38:38');

-- ----------------------------
-- Table structure for t_publish_images
-- ----------------------------
DROP TABLE IF EXISTS `t_publish_images`;
CREATE TABLE `t_publish_images`  (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `publish_id` int(11) NOT NULL COMMENT '关联发布记录ID（t_publish_records.id）',
  `image_id` int(11) NOT NULL COMMENT '图片id',
  `image_type` tinyint(4) NULL DEFAULT 1 COMMENT '\r\n  1=正文图\r\n  2=封面图\r\n  3=详情图\r\n  ',
  `sort_order` int(11) NULL DEFAULT 1 COMMENT '图片顺序，1为第一张',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_publish_id`(`publish_id` ASC) USING BTREE,
  INDEX `idx_sort`(`sort_order` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 87 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '发布内容图片表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of t_publish_images
-- ----------------------------

-- ----------------------------
-- Table structure for t_publish_records
-- ----------------------------
DROP TABLE IF EXISTS `t_publish_records`;
CREATE TABLE `t_publish_records`  (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '发布记录ID',
  `user_id` int(11) NULL DEFAULT NULL COMMENT '用户id',
  `title_id` int(11) NOT NULL COMMENT '关联标题ID（t_titles.id）',
  `platform` tinyint(4) NOT NULL COMMENT '\r\n  1=小红书\r\n  2=抖音\r\n  3=快手\r\n  4=微信公众号\r\n  ',
  `publish_status` tinyint(4) NOT NULL DEFAULT 0 COMMENT '\r\n  0=待发布\r\n  1=发布中\r\n  2=发布成功\r\n  3=发布失败\r\n  4=已删除\r\n  ',
  `publish_time` datetime NULL DEFAULT NULL COMMENT '实际发布时间',
  `content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '发布时的最终文案',
  `view_count` int(11) NULL DEFAULT 0 COMMENT '阅读量',
  `like_count` int(11) NULL DEFAULT 0 COMMENT '点赞量',
  `comment_count` int(11) NULL DEFAULT 0 COMMENT '评论数',
  `share_count` int(11) NULL DEFAULT 0 COMMENT '分享数',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_title_id`(`title_id` ASC) USING BTREE,
  INDEX `idx_platform`(`platform` ASC) USING BTREE,
  INDEX `idx_status`(`publish_status` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 13 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '内容发布记录表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of t_publish_records
-- ----------------------------

-- ----------------------------
-- Table structure for t_sections
-- ----------------------------
DROP TABLE IF EXISTS `t_sections`;
CREATE TABLE `t_sections`  (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '板块唯一ID',
  `user_id` int(11) NOT NULL COMMENT '所属用户ID（逻辑关联 t_users.id）',
  `source_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '主题',
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '板块名称',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '板块创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_user_id`(`user_id` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 86 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '板块表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of t_sections
-- ----------------------------
INSERT INTO `t_sections` VALUES (66, 1, 'openclaw', '每日行业热点', '2026-03-17 23:14:32', '2026-03-17 15:14:32');
INSERT INTO `t_sections` VALUES (67, 1, 'openclaw', '热点榜单', '2026-03-17 23:14:32', '2026-03-17 15:14:32');
INSERT INTO `t_sections` VALUES (68, 1, 'openclaw', '专业知识榜单', '2026-03-17 23:14:32', '2026-03-17 15:14:32');
INSERT INTO `t_sections` VALUES (69, 1, 'openclaw', '人设共鸣', '2026-03-17 23:14:33', '2026-03-17 15:14:33');
INSERT INTO `t_sections` VALUES (70, 1, 'openclaw', '灵感广场', '2026-03-17 23:14:33', '2026-03-17 15:14:33');
INSERT INTO `t_sections` VALUES (76, 1, 'python', '每日行业热点', '2026-03-17 23:25:45', '2026-03-17 15:25:45');
INSERT INTO `t_sections` VALUES (77, 1, 'python', '热点榜单', '2026-03-17 23:25:46', '2026-03-17 15:25:46');
INSERT INTO `t_sections` VALUES (78, 1, 'python', '专业知识榜单', '2026-03-17 23:25:46', '2026-03-17 15:25:46');
INSERT INTO `t_sections` VALUES (79, 1, 'python', '人设共鸣', '2026-03-17 23:25:46', '2026-03-17 15:25:46');
INSERT INTO `t_sections` VALUES (80, 1, 'python', '灵感广场', '2026-03-17 23:25:46', '2026-03-17 15:25:46');
INSERT INTO `t_sections` VALUES (81, 1, 'java', '每日行业热点', '2026-03-17 15:29:35', '2026-03-17 07:29:35');
INSERT INTO `t_sections` VALUES (82, 1, 'java', '热点榜单', '2026-03-17 15:29:35', '2026-03-17 07:29:35');
INSERT INTO `t_sections` VALUES (83, 1, 'java', '专业知识榜单', '2026-03-17 15:29:36', '2026-03-17 07:29:36');
INSERT INTO `t_sections` VALUES (84, 1, 'java', '人设共鸣', '2026-03-17 15:29:36', '2026-03-17 07:29:36');
INSERT INTO `t_sections` VALUES (85, 1, 'java', '灵感广场', '2026-03-17 15:29:36', '2026-03-17 07:29:36');

-- ----------------------------
-- Table structure for t_style
-- ----------------------------
DROP TABLE IF EXISTS `t_style`;
CREATE TABLE `t_style`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `fengge` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `create_time` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 8 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of t_style
-- ----------------------------
INSERT INTO `t_style` VALUES (1, '扁平化海报', '极简主义扁平化海报设计风格，整体采用非常清淡柔和的浅色调背景，背景由大面积的纯白色与少量浅粉色、浅紫色的圆形光晕渐变色块构成，营造出朦胧且科技感较弱的清新氛围，视觉中心采用经典的垂直居中排版布局，文字层级分明，顶部为主标题区域使用醒目的红色加粗无衬线字体，下方跟随黑色的副标题与深灰色的正文说明，字体均为现代简洁的无衬线黑体，底部排列着两行胶囊形状的白色标签，配以浅灰色的文字，整体画面留白充足，风格干净利落，具有典型的新媒体资讯或知识卡片的美学特征，色彩搭配为白色底色辅以淡粉淡紫装饰，字色为鲜红与深黑的强烈对比。', '2026-02-22 13:36:57');
INSERT INTO `t_style` VALUES (2, '手绘', '一张竖构图的教育类科普长图，主题是关于上述文案。风格定义为手绘视觉笔记和极简涂鸦风。视觉元素包含马克笔手绘线条、可爱的简笔画图标、以及波浪状的连接箭头。配色方案强制锁定为：温暖的大地色系，使用焦糖橙色作为高光、巧克力深棕色作为轮廓线，背景由于干净的米白色纸张纹理构成。整体氛围轻松、有着手作的质感，高清晰度。', '2026-02-22 13:36:55');
INSERT INTO `t_style` VALUES (3, '公众号', '极简风格公众号文章长图文排版设计，整体采用温暖且具有高级感的暖米色调作为背景，营造阅读舒适的氛围。主体视觉为大字报式的标题设计，标题采用极粗的无衬线字体，字色呈现深褐咖啡色，并在文字下方垫有浅米色或半透明的浅色块作为高光衬托，形成层次感。正文部分排版疏朗，行间距宽绰，采用深棕色或黑褐色的常规无衬线衬线字体，文字段落清晰，段落之间留白充足。整体设计语言强调文字信息的传递效率，风格干净、素雅、现代化，没有任何多余的复杂装饰元素，仅通过字体大小对比、颜色深浅变化和留白来构建视觉层级，呈现出典型的知识分享类自媒体图文风格。', '2026-02-22 13:36:59');
INSERT INTO `t_style` VALUES (4, '极简主义海报', '一张垂直构图的极简主义科技风格海报设计，背景采用干净清爽的浅灰白色，画面顶部居中放置一个简单的紫色线条几何图标，视觉主体为居中对齐的大号无衬线粗体文字排版，采用深灰色与鲜艳的亮紫色进行强调对比，亮紫色文字区域底部衬有淡粉色或肉色的长条状高亮色块装饰，底部为整齐排列的小号深灰色说明文字，整体风格呈现出现代、扁平化且具有商务演示感的视觉美学。', '2026-02-22 13:37:01');
INSERT INTO `t_style` VALUES (5, '插画', '极简主义扁平化风格的社交媒体信息卡片设计背景采用高饱和度的明亮蓝色主体为一张居中的大面积白色圆角矩形备忘录卡片呈现出现代UI界面质感卡片内部布局为左对齐的标题与列表格式部分条目背景带有浅嫩绿色荧光笔涂抹效果的高亮色块底部设计有极细的水平分割线及两侧微小的辅助文本标识整体视觉干净清爽高对比度无噪点矢量插画风格', '2026-02-22 13:37:03');
INSERT INTO `t_style` VALUES (6, '用户界面', '极简主义深色模式用户界面设计风格，采用高对比度的现代科技美学，背景为纯净的哑光深炭灰色，视觉重心在于严谨的排版布局，顶部采用巨大的白色无衬线粗体文字作为标题，具有强烈的冲击力，中部包含微小的圆形头像与元数据行，正文段落排列整齐且行间距宽敞，底部点缀极简的彩色矩形数据图例，整体呈现出一种扁平化、理性且高效的数字化笔记或阅读软件界面质感，无多余装饰，强调文字的可读性与信息层级。', '2026-02-22 13:37:05');

-- ----------------------------
-- Table structure for t_title_images
-- ----------------------------
DROP TABLE IF EXISTS `t_title_images`;
CREATE TABLE `t_title_images`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '图片ID',
  `user_id` int(11) NULL DEFAULT NULL COMMENT '用户id',
  `title_id` int(11) NOT NULL COMMENT '所属标题ID（逻辑关联 t_titles.id）',
  `image_url` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '图片访问地址',
  `image_type` tinyint(4) NOT NULL DEFAULT 0 COMMENT '图片类型 0=正文图 1=封面图 2=缩略图',
  `sort_order` int(11) NOT NULL DEFAULT 0 COMMENT '图片排序',
  `file_size` int(11) NULL DEFAULT NULL COMMENT '文件大小(字节)',
  `width` int(11) NULL DEFAULT NULL COMMENT '图片宽度',
  `height` int(11) NULL DEFAULT NULL COMMENT '图片高度',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_title_id`(`title_id` ASC) USING BTREE,
  INDEX `idx_image_type`(`image_type` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 39 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '标题图片表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of t_title_images
-- ----------------------------

-- ----------------------------
-- Table structure for t_titles
-- ----------------------------
DROP TABLE IF EXISTS `t_titles`;
CREATE TABLE `t_titles`  (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '标题唯一ID',
  `section_id` int(11) NOT NULL COMMENT '所属板块ID（逻辑关联 t_sections.id）',
  `title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '标题内容',
  `sort_order` int(11) NOT NULL COMMENT '热度排序，1为最高',
  `content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '文章内容',
  `status` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '状态 0=未生成，\n1=已生成，\n2=已发布，3=已废弃',
  `view_count` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '阅读量',
  `like_count` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '点赞量',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '标题创建时间',
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_section_id`(`section_id` ASC) USING BTREE,
  INDEX `idx_sort_order`(`sort_order` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 851 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '标题表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of t_titles
-- ----------------------------
INSERT INTO `t_titles` VALUES (651, 66, '突发！OpenClaw成开源界新奇迹🎉', 1, NULL, NULL, NULL, NULL, '2026-03-17 23:14:32', '2026-03-17 15:14:32');
INSERT INTO `t_titles` VALUES (652, 66, '最新！OpenClaw超越Linux引关注🔥', 2, NULL, NULL, NULL, NULL, '2026-03-17 23:14:32', '2026-03-17 15:14:32');
INSERT INTO `t_titles` VALUES (653, 66, '重磅！OpenClaw安全风险需警惕⚠️', 3, NULL, NULL, NULL, NULL, '2026-03-17 23:14:32', '2026-03-17 15:14:32');
INSERT INTO `t_titles` VALUES (654, 66, '快看！OpenClaw成年度现象级项目👏', 4, NULL, NULL, NULL, NULL, '2026-03-17 23:14:32', '2026-03-17 15:14:32');
INSERT INTO `t_titles` VALUES (655, 66, '惊爆！OpenClaw增长速度太惊人😲', 5, NULL, NULL, NULL, NULL, '2026-03-17 23:14:32', '2026-03-17 15:14:32');
INSERT INTO `t_titles` VALUES (656, 66, '注意！OpenClaw使用安全指南📖', 6, NULL, NULL, NULL, NULL, '2026-03-17 23:14:32', '2026-03-17 15:14:32');
INSERT INTO `t_titles` VALUES (657, 66, '揭秘！OpenClaw走红背后的秘密🤫', 7, NULL, NULL, NULL, NULL, '2026-03-17 23:14:32', '2026-03-17 15:14:32');
INSERT INTO `t_titles` VALUES (658, 66, '大事！OpenClaw引发开源狂欢🎊', 8, NULL, NULL, NULL, NULL, '2026-03-17 23:14:32', '2026-03-17 15:14:32');
INSERT INTO `t_titles` VALUES (659, 66, '聚焦！OpenClaw或改变AI格局💥', 9, NULL, NULL, NULL, NULL, '2026-03-17 23:14:32', '2026-03-17 15:14:32');
INSERT INTO `t_titles` VALUES (660, 66, '震撼！OpenClaw星标数超越所有开源软件🌟', 10, NULL, NULL, NULL, NULL, '2026-03-17 23:14:32', '2026-03-17 15:14:32');
INSERT INTO `t_titles` VALUES (661, 67, '热搜第一！OpenClaw，AI新宠谁不爱😍', 1, NULL, NULL, NULL, NULL, '2026-03-17 23:14:32', '2026-03-17 15:14:32');
INSERT INTO `t_titles` VALUES (662, 67, '知乎热榜！OpenClaw创新亮点大揭秘🧐', 2, NULL, NULL, NULL, NULL, '2026-03-17 23:14:32', '2026-03-17 15:14:32');
INSERT INTO `t_titles` VALUES (663, 67, '热议！OpenClaw能否引领AI新时代？🤔', 3, NULL, NULL, NULL, NULL, '2026-03-17 23:14:32', '2026-03-17 15:14:32');
INSERT INTO `t_titles` VALUES (664, 67, '爆火话题！OpenClaw安全问题引担忧🙁', 4, NULL, NULL, NULL, NULL, '2026-03-17 23:14:32', '2026-03-17 15:14:32');
INSERT INTO `t_titles` VALUES (665, 67, '全网讨论！OpenClaw与腾讯AI的较量🤺', 5, NULL, NULL, NULL, NULL, '2026-03-17 23:14:32', '2026-03-17 15:14:32');
INSERT INTO `t_titles` VALUES (666, 67, '话题出圈！OpenClaw发展前景如何？👀', 6, NULL, NULL, NULL, NULL, '2026-03-17 23:14:32', '2026-03-17 15:14:32');
INSERT INTO `t_titles` VALUES (667, 67, '热榜来袭！OpenClaw的独特魅力在哪？😎', 7, NULL, NULL, NULL, NULL, '2026-03-17 23:14:32', '2026-03-17 15:14:32');
INSERT INTO `t_titles` VALUES (668, 67, '高热度！OpenClaw成AI界焦点👀', 8, NULL, NULL, NULL, NULL, '2026-03-17 23:14:32', '2026-03-17 15:14:32');
INSERT INTO `t_titles` VALUES (669, 67, '超火话题！OpenClaw使用体验大分享😜', 9, NULL, NULL, NULL, NULL, '2026-03-17 23:14:32', '2026-03-17 15:14:32');
INSERT INTO `t_titles` VALUES (670, 67, '热搜爆了！OpenClaw掀起AI新风暴🌪️', 10, NULL, NULL, NULL, NULL, '2026-03-17 23:14:32', '2026-03-17 15:14:32');
INSERT INTO `t_titles` VALUES (671, 68, '黄仁勋演讲！OpenClaw与新科技碰撞💥', 1, NULL, NULL, NULL, NULL, '2026-03-17 23:14:32', '2026-03-17 15:14:32');
INSERT INTO `t_titles` VALUES (672, 68, 'DLSS 5发布！OpenClaw如何借势发展？🚀', 2, NULL, NULL, NULL, NULL, '2026-03-17 23:14:32', '2026-03-17 15:14:32');
INSERT INTO `t_titles` VALUES (673, 68, '苹果新品登场！OpenClaw与之有何关联？🤔', 3, NULL, NULL, NULL, NULL, '2026-03-17 23:14:32', '2026-03-17 15:14:32');
INSERT INTO `t_titles` VALUES (674, 68, '内存涨价潮！OpenClaw受影响几何？📉', 4, NULL, NULL, NULL, NULL, '2026-03-17 23:14:32', '2026-03-17 15:14:32');
INSERT INTO `t_titles` VALUES (675, 68, '鸿蒙智行曝光！OpenClaw能否与之融合？👫', 5, NULL, NULL, NULL, NULL, '2026-03-17 23:14:32', '2026-03-17 15:14:32');
INSERT INTO `t_titles` VALUES (676, 68, '雷军揭秘底盘！OpenClaw在汽车领域潜力大？🚗', 6, NULL, NULL, NULL, NULL, '2026-03-17 23:14:33', '2026-03-17 15:14:33');
INSERT INTO `t_titles` VALUES (677, 68, 'AI大模型投毒曝光！OpenClaw安全咋保障？🛡️', 7, NULL, NULL, NULL, NULL, '2026-03-17 23:14:33', '2026-03-17 15:14:33');
INSERT INTO `t_titles` VALUES (678, 68, '英伟达新技术！OpenClaw发展新机遇？🌟', 8, NULL, NULL, NULL, NULL, '2026-03-17 23:14:33', '2026-03-17 15:14:33');
INSERT INTO `t_titles` VALUES (679, 68, '华为新动态！OpenClaw与鸿蒙的合作可能？🤝', 9, NULL, NULL, NULL, NULL, '2026-03-17 23:14:33', '2026-03-17 15:14:33');
INSERT INTO `t_titles` VALUES (680, 68, '手机定价逻辑崩坏！OpenClaw市场策略调整？📈', 10, NULL, NULL, NULL, NULL, '2026-03-17 23:14:33', '2026-03-17 15:14:33');
INSERT INTO `t_titles` VALUES (681, 69, 'AI浪潮下！OpenClaw助你提升竞争力💪', 1, NULL, NULL, NULL, NULL, '2026-03-17 23:14:33', '2026-03-17 15:14:33');
INSERT INTO `t_titles` VALUES (682, 69, '程序员破防！OpenClaw改变代码编写模式😭', 2, NULL, NULL, NULL, NULL, '2026-03-17 23:14:33', '2026-03-17 15:14:33');
INSERT INTO `t_titles` VALUES (683, 69, '科技变革中！OpenClaw带来新职业挑战😰', 3, NULL, NULL, NULL, NULL, '2026-03-17 23:14:33', '2026-03-17 15:14:33');
INSERT INTO `t_titles` VALUES (684, 69, 'AI时代焦虑！OpenClaw能否成为救星？🙏', 4, NULL, NULL, NULL, NULL, '2026-03-17 23:14:33', '2026-03-17 15:14:33');
INSERT INTO `t_titles` VALUES (685, 69, '担心被替代！OpenClaw如何让你更不可替代？🤔', 5, NULL, NULL, NULL, NULL, '2026-03-17 23:14:33', '2026-03-17 15:14:33');
INSERT INTO `t_titles` VALUES (686, 69, '技术革新！OpenClaw让工作效率飙升🚀', 6, NULL, NULL, NULL, NULL, '2026-03-17 23:14:33', '2026-03-17 15:14:33');
INSERT INTO `t_titles` VALUES (687, 69, '职业转型期！OpenClaw指引新方向🌟', 7, NULL, NULL, NULL, NULL, '2026-03-17 23:14:33', '2026-03-17 15:14:33');
INSERT INTO `t_titles` VALUES (688, 69, '面对AI冲击！OpenClaw给你安全感🛡️', 8, NULL, NULL, NULL, NULL, '2026-03-17 23:14:33', '2026-03-17 15:14:33');
INSERT INTO `t_titles` VALUES (689, 69, '工作压力大！OpenClaw帮你轻松应对😌', 9, NULL, NULL, NULL, NULL, '2026-03-17 23:14:33', '2026-03-17 15:14:33');
INSERT INTO `t_titles` VALUES (690, 69, '科技进步太快！OpenClaw带你跟上节奏💨', 10, NULL, NULL, NULL, NULL, '2026-03-17 23:14:33', '2026-03-17 15:14:33');
INSERT INTO `t_titles` VALUES (691, 70, '如果OpenClaw去打网球...太上头了🎾', 1, NULL, NULL, NULL, NULL, '2026-03-17 23:14:33', '2026-03-17 15:14:33');
INSERT INTO `t_titles` VALUES (692, 70, '当OpenClaw遇上小巷人家2，奇妙联动😜', 2, NULL, NULL, NULL, NULL, '2026-03-17 23:14:33', '2026-03-17 15:14:33');
INSERT INTO `t_titles` VALUES (693, 70, 'OpenClaw与金价下跌，会擦出啥火花？📉', 3, NULL, NULL, NULL, NULL, '2026-03-17 23:14:33', '2026-03-17 15:14:33');
INSERT INTO `t_titles` VALUES (694, 70, '让OpenClaw给周也搭配穿搭，绝了🤩', 4, NULL, NULL, NULL, NULL, '2026-03-17 23:14:33', '2026-03-17 15:14:33');
INSERT INTO `t_titles` VALUES (695, 70, 'OpenClaw和职场工位按职级排有啥关系？🤔', 5, NULL, NULL, NULL, NULL, '2026-03-17 23:14:33', '2026-03-17 15:14:33');
INSERT INTO `t_titles` VALUES (696, 70, '假如OpenClaw参与南极游，体验拉满🧊', 6, NULL, NULL, NULL, NULL, '2026-03-17 23:14:33', '2026-03-17 15:14:33');
INSERT INTO `t_titles` VALUES (697, 70, 'OpenClaw碰上高中生过马路悲剧，深思😢', 7, NULL, NULL, NULL, NULL, '2026-03-17 23:14:33', '2026-03-17 15:14:33');
INSERT INTO `t_titles` VALUES (698, 70, '当OpenClaw与养QQ宠物结合，太有趣了🐾', 8, NULL, NULL, NULL, NULL, '2026-03-17 23:14:33', '2026-03-17 15:14:33');
INSERT INTO `t_titles` VALUES (699, 70, 'OpenClaw和A股两大利好能共舞吗？📈', 9, NULL, NULL, NULL, NULL, '2026-03-17 23:14:33', '2026-03-17 15:14:33');
INSERT INTO `t_titles` VALUES (700, 70, '让OpenClaw指导鹿晗专辑发售，期待😎', 10, NULL, NULL, NULL, NULL, '2026-03-17 23:14:33', '2026-03-17 15:14:33');
INSERT INTO `t_titles` VALUES (751, 76, '突发！Python成编程界新宠🔥', 1, NULL, NULL, NULL, NULL, '2026-03-17 23:25:46', '2026-03-17 15:25:46');
INSERT INTO `t_titles` VALUES (752, 76, '最新！Python应用领域再拓展💥', 2, NULL, NULL, NULL, NULL, '2026-03-17 23:25:46', '2026-03-17 15:25:46');
INSERT INTO `t_titles` VALUES (753, 76, '重磅！Python学习热潮来袭🎉', 3, NULL, NULL, NULL, NULL, '2026-03-17 23:25:46', '2026-03-17 15:25:46');
INSERT INTO `t_titles` VALUES (754, 76, 'Python！编程界的明日之星🌟', 4, NULL, NULL, NULL, NULL, '2026-03-17 23:25:46', '2026-03-17 15:25:46');
INSERT INTO `t_titles` VALUES (755, 76, '快看！Python优势凸显啦👏', 5, NULL, NULL, NULL, NULL, '2026-03-17 23:25:46', '2026-03-17 15:25:46');
INSERT INTO `t_titles` VALUES (756, 76, 'Python，编程新热点来袭😎', 6, NULL, NULL, NULL, NULL, '2026-03-17 23:25:46', '2026-03-17 15:25:46');
INSERT INTO `t_titles` VALUES (757, 76, '突发！Python发展前景大好🎊', 7, NULL, NULL, NULL, NULL, '2026-03-17 23:25:46', '2026-03-17 15:25:46');
INSERT INTO `t_titles` VALUES (758, 76, '最新！Python应用范围扩大啦📈', 8, NULL, NULL, NULL, NULL, '2026-03-17 23:25:46', '2026-03-17 15:25:46');
INSERT INTO `t_titles` VALUES (759, 76, '重磅！Python学习热度飙升🔥', 9, NULL, NULL, NULL, NULL, '2026-03-17 23:25:46', '2026-03-17 15:25:46');
INSERT INTO `t_titles` VALUES (760, 76, 'Python，编程界的潜力股💪', 10, NULL, NULL, NULL, NULL, '2026-03-17 23:25:46', '2026-03-17 15:25:46');
INSERT INTO `t_titles` VALUES (761, 77, '热搜第一！Python助力AI发展🤖', 1, NULL, NULL, NULL, NULL, '2026-03-17 23:25:46', '2026-03-17 15:25:46');
INSERT INTO `t_titles` VALUES (762, 77, '永辉喊话山姆，Python有啥关联？🤔', 2, NULL, NULL, NULL, NULL, '2026-03-17 23:25:46', '2026-03-17 15:25:46');
INSERT INTO `t_titles` VALUES (763, 77, 'Kimi新模块，Python能做啥？🧐', 3, NULL, NULL, NULL, NULL, '2026-03-17 23:25:46', '2026-03-17 15:25:46');
INSERT INTO `t_titles` VALUES (764, 77, '网络热梗卡片，Python可检测❓', 4, NULL, NULL, NULL, NULL, '2026-03-17 23:25:46', '2026-03-17 15:25:46');
INSERT INTO `t_titles` VALUES (765, 77, '美以伊局势，Python能分析吗？🌍', 5, NULL, NULL, NULL, NULL, '2026-03-17 23:25:46', '2026-03-17 15:25:46');
INSERT INTO `t_titles` VALUES (766, 77, '黄仁勋演讲，Python有新机遇？💡', 6, NULL, NULL, NULL, NULL, '2026-03-17 23:25:46', '2026-03-17 15:25:46');
INSERT INTO `t_titles` VALUES (767, 77, '上海房贷政策，Python能预测？🏠', 7, NULL, NULL, NULL, NULL, '2026-03-17 23:25:46', '2026-03-17 15:25:46');
INSERT INTO `t_titles` VALUES (768, 77, '油菜花期打药，Python来研究？🌼', 8, NULL, NULL, NULL, NULL, '2026-03-17 23:25:46', '2026-03-17 15:25:46');
INSERT INTO `t_titles` VALUES (769, 77, '英伟达DLSS5，Python能适配？🎮', 9, NULL, NULL, NULL, NULL, '2026-03-17 23:25:46', '2026-03-17 15:25:46');
INSERT INTO `t_titles` VALUES (770, 77, '多国抗议美以，Python看局势？👀', 10, NULL, NULL, NULL, NULL, '2026-03-17 23:25:46', '2026-03-17 15:25:46');
INSERT INTO `t_titles` VALUES (771, 78, '黄仁勋演讲，Python如何助力芯片？💥', 1, NULL, NULL, NULL, NULL, '2026-03-17 23:25:46', '2026-03-17 15:25:46');
INSERT INTO `t_titles` VALUES (772, 78, '苹果新品发布，Python开发应用？📱', 2, NULL, NULL, NULL, NULL, '2026-03-17 23:25:46', '2026-03-17 15:25:46');
INSERT INTO `t_titles` VALUES (773, 78, '内存涨价，Python优化成本？💰', 3, NULL, NULL, NULL, NULL, '2026-03-17 23:25:46', '2026-03-17 15:25:46');
INSERT INTO `t_titles` VALUES (774, 78, '华为账号异常，Python保障安全？🔒', 4, NULL, NULL, NULL, NULL, '2026-03-17 23:25:46', '2026-03-17 15:25:46');
INSERT INTO `t_titles` VALUES (775, 78, '小米SU7底盘，Python模拟测试？🚗', 5, NULL, NULL, NULL, NULL, '2026-03-17 23:25:46', '2026-03-17 15:25:46');
INSERT INTO `t_titles` VALUES (776, 78, '英伟达DLSS5，Python图形编程？🖥️', 6, NULL, NULL, NULL, NULL, '2026-03-17 23:25:46', '2026-03-17 15:25:46');
INSERT INTO `t_titles` VALUES (777, 78, '央视曝光AI投毒，Python防范策略？🛡️', 7, NULL, NULL, NULL, NULL, '2026-03-17 23:25:46', '2026-03-17 15:25:46');
INSERT INTO `t_titles` VALUES (778, 78, 'OpenClaw福利，Python开发新体验？🎉', 8, NULL, NULL, NULL, NULL, '2026-03-17 23:25:46', '2026-03-17 15:25:46');
INSERT INTO `t_titles` VALUES (779, 78, '鸿蒙智行新车，Python智能交互？🌟', 9, NULL, NULL, NULL, NULL, '2026-03-17 23:25:46', '2026-03-17 15:25:46');
INSERT INTO `t_titles` VALUES (780, 78, '追觅旗舰手机，Python性能优化？💪', 10, NULL, NULL, NULL, NULL, '2026-03-17 23:25:46', '2026-03-17 15:25:46');
INSERT INTO `t_titles` VALUES (781, 79, 'AI时代，Python助程序员逆袭😭', 1, NULL, NULL, NULL, NULL, '2026-03-17 23:25:46', '2026-03-17 15:25:46');
INSERT INTO `t_titles` VALUES (782, 79, 'Python，让程序员告别焦虑😌', 2, NULL, NULL, NULL, NULL, '2026-03-17 23:25:46', '2026-03-17 15:25:46');
INSERT INTO `t_titles` VALUES (783, 79, '学Python，程序员不再怕失业啦👏', 3, NULL, NULL, NULL, NULL, '2026-03-17 23:25:46', '2026-03-17 15:25:46');
INSERT INTO `t_titles` VALUES (784, 79, 'Python在手，程序员底气十足💪', 4, NULL, NULL, NULL, NULL, '2026-03-17 23:25:46', '2026-03-17 15:25:46');
INSERT INTO `t_titles` VALUES (785, 79, 'AI浪潮下，Python成程序员救星🌟', 5, NULL, NULL, NULL, NULL, '2026-03-17 23:25:46', '2026-03-17 15:25:46');
INSERT INTO `t_titles` VALUES (786, 79, '用Python，程序员效率飙升啦🚀', 6, NULL, NULL, NULL, NULL, '2026-03-17 23:25:46', '2026-03-17 15:25:46');
INSERT INTO `t_titles` VALUES (787, 79, 'Python，程序员的新希望🎉', 7, NULL, NULL, NULL, NULL, '2026-03-17 23:25:46', '2026-03-17 15:25:46');
INSERT INTO `t_titles` VALUES (788, 79, '学Python，程序员开启新征程🎊', 8, NULL, NULL, NULL, NULL, '2026-03-17 23:25:46', '2026-03-17 15:25:46');
INSERT INTO `t_titles` VALUES (789, 79, 'Python助力，程序员突破瓶颈💥', 9, NULL, NULL, NULL, NULL, '2026-03-17 23:25:46', '2026-03-17 15:25:46');
INSERT INTO `t_titles` VALUES (790, 79, '有Python，程序员不再迷茫😎', 10, NULL, NULL, NULL, NULL, '2026-03-17 23:25:46', '2026-03-17 15:25:46');
INSERT INTO `t_titles` VALUES (791, 80, '如果Python去开网店，会怎样？🛍️', 1, NULL, NULL, NULL, NULL, '2026-03-17 23:25:46', '2026-03-17 15:25:46');
INSERT INTO `t_titles` VALUES (792, 80, 'Python遇上职场宫斗，谁赢？👑', 2, NULL, NULL, NULL, NULL, '2026-03-17 23:25:46', '2026-03-17 15:25:46');
INSERT INTO `t_titles` VALUES (793, 80, 'Python和机器人打网球，战况？🎾', 3, NULL, NULL, NULL, NULL, '2026-03-17 23:25:46', '2026-03-17 15:25:46');
INSERT INTO `t_titles` VALUES (794, 80, 'Python帮大爷炖排骨，香吗？🍖', 4, NULL, NULL, NULL, NULL, '2026-03-17 23:25:46', '2026-03-17 15:25:46');
INSERT INTO `t_titles` VALUES (795, 80, 'Python指导周也穿搭，美爆？👗', 5, NULL, NULL, NULL, NULL, '2026-03-17 23:25:46', '2026-03-17 15:25:46');
INSERT INTO `t_titles` VALUES (796, 80, 'Python助力高中生写作业，牛吧？📚', 6, NULL, NULL, NULL, NULL, '2026-03-17 23:25:46', '2026-03-17 15:25:46');
INSERT INTO `t_titles` VALUES (797, 80, 'Python和易烊千玺歌曲投票，咋玩？🎵', 7, NULL, NULL, NULL, NULL, '2026-03-17 23:25:46', '2026-03-17 15:25:46');
INSERT INTO `t_titles` VALUES (798, 80, 'Python帮刘昊然拍电影，绝了？🎬', 8, NULL, NULL, NULL, NULL, '2026-03-17 23:25:46', '2026-03-17 15:25:46');
INSERT INTO `t_titles` VALUES (799, 80, 'Python和瞿颖结婚，啥剧情？💒', 9, NULL, NULL, NULL, NULL, '2026-03-17 23:25:46', '2026-03-17 15:25:46');
INSERT INTO `t_titles` VALUES (800, 80, 'Python陪鹿晗发专辑，火不？💿', 10, NULL, NULL, NULL, NULL, '2026-03-17 23:25:46', '2026-03-17 15:25:46');
INSERT INTO `t_titles` VALUES (801, 81, '重磅！2025 InfoQ报告，Java新趋势揭秘📖', 1, '家人们，今天必须来给你们分享2025 InfoQ报告里Java的新趋势！我自己是搞Java开发的，平时就很关注行业动态，看到这份报告的时候，我真的一整个大震惊🤯。\n\n报告里说Java在云原生领域的应用会越来越广泛，好多企业都开始用Java构建云原生应用了。而且Java的性能优化也有了新突破，新的垃圾回收算法让程序运行速度更快了。还有啊，Java在人工智能和机器学习方面也有了新进展，感觉未来Java的发展前景一片光明！\n\n我亲测，这些新趋势对我们开发者来说，既是机遇也是挑战。我们得不断学习新的知识和技能，才能跟上行业的发展。说真的，我最近就在恶补云原生和人工智能相关的知识，真的有点上头😆。\n\n懂行的姐妹都知道，掌握这些新趋势，在职场上那就是超派的存在！有同样想提升自己的姐妹快冲，一起在Java的世界里搞事情💪！', '1', NULL, NULL, '2026-03-17 15:29:35', '2026-03-24 02:26:24');
INSERT INTO `t_titles` VALUES (802, 81, '突发！Spring新版本发布，Java开发者有福啦🎉', 2, NULL, NULL, NULL, NULL, '2026-03-17 15:29:35', '2026-03-17 07:29:35');
INSERT INTO `t_titles` VALUES (803, 81, '最新！Java领域技术采用新动态✨', 3, NULL, NULL, NULL, NULL, '2026-03-17 15:29:35', '2026-03-17 07:29:35');
INSERT INTO `t_titles` VALUES (804, 81, '震惊！Java速度实测，能否追上Rust？⚡', 4, NULL, NULL, NULL, NULL, '2026-03-17 15:29:35', '2026-03-17 07:29:35');
INSERT INTO `t_titles` VALUES (805, 81, '快看！Java反射机制深度解析🧐', 5, NULL, NULL, NULL, NULL, '2026-03-17 15:29:35', '2026-03-17 07:29:35');
INSERT INTO `t_titles` VALUES (806, 81, '厉害啦！Java走过30年仍影响力十足👍', 6, NULL, NULL, NULL, NULL, '2026-03-17 15:29:35', '2026-03-17 07:29:35');
INSERT INTO `t_titles` VALUES (807, 81, '揭秘！Java与其他语言的区别对比🤔', 7, NULL, NULL, NULL, NULL, '2026-03-17 15:29:35', '2026-03-17 07:29:35');
INSERT INTO `t_titles` VALUES (808, 81, '注意！Java领域新兴趋势大曝光📢', 8, NULL, NULL, NULL, NULL, '2026-03-17 15:29:35', '2026-03-17 07:29:35');
INSERT INTO `t_titles` VALUES (809, 81, '哇塞！InfoQ报告解读Java新走向🌟', 9, NULL, NULL, NULL, NULL, '2026-03-17 15:29:35', '2026-03-17 07:29:35');
INSERT INTO `t_titles` VALUES (810, 81, '瞧瞧！Java在编程世界的地位变迁🚀', 10, NULL, NULL, NULL, NULL, '2026-03-17 15:29:35', '2026-03-17 07:29:35');
INSERT INTO `t_titles` VALUES (811, 82, '热搜第一！永辉喊话山姆，Java开发者咋看？🤔', 1, NULL, NULL, NULL, NULL, '2026-03-17 15:29:35', '2026-03-17 07:29:35');
INSERT INTO `t_titles` VALUES (812, 82, '知乎热议！Kimi新模块，Java能借鉴啥？💡', 2, NULL, NULL, NULL, NULL, '2026-03-17 15:29:35', '2026-03-17 07:29:35');
INSERT INTO `t_titles` VALUES (813, 82, '爆火！网络热梗卡片，Java圈有啥梗？😜', 3, NULL, NULL, NULL, NULL, '2026-03-17 15:29:35', '2026-03-17 07:29:35');
INSERT INTO `t_titles` VALUES (814, 82, '热议！伊朗局势，Java行业受影响吗？🌍', 4, NULL, NULL, NULL, NULL, '2026-03-17 15:29:35', '2026-03-17 07:29:35');
INSERT INTO `t_titles` VALUES (815, 82, '超火！英伟达DLSS5，Java图形开发有新招？🎮', 5, NULL, NULL, NULL, NULL, '2026-03-17 15:29:35', '2026-03-17 07:29:35');
INSERT INTO `t_titles` VALUES (816, 82, '出圈！年轻人追新三金，Java投资新方向？💰', 6, NULL, NULL, NULL, NULL, '2026-03-17 15:29:35', '2026-03-17 07:29:35');
INSERT INTO `t_titles` VALUES (817, 82, '刷屏！多国抗议美以，Java国际市场咋变？🌏', 7, NULL, NULL, NULL, NULL, '2026-03-17 15:29:35', '2026-03-17 07:29:35');
INSERT INTO `t_titles` VALUES (818, 82, '沸腾！山姆被控诉，Java供应链会紧张吗？📈', 8, NULL, NULL, NULL, NULL, '2026-03-17 15:29:35', '2026-03-17 07:29:35');
INSERT INTO `t_titles` VALUES (819, 82, '疯传！金价下跌买不进，Java从业者咋理财？💸', 9, NULL, NULL, NULL, NULL, '2026-03-17 15:29:36', '2026-03-17 07:29:36');
INSERT INTO `t_titles` VALUES (820, 82, '炸裂！中国机器人打网球，Java有何应用？🤖', 10, NULL, NULL, NULL, NULL, '2026-03-17 15:29:36', '2026-03-17 07:29:36');
INSERT INTO `t_titles` VALUES (821, 83, '黄仁勋演讲亮点，Java开发有新启发吗？💡', 1, NULL, NULL, NULL, NULL, '2026-03-17 15:29:36', '2026-03-17 07:29:36');
INSERT INTO `t_titles` VALUES (822, 83, '苹果新品发布，Java适配有啥新挑战？📱', 2, NULL, NULL, NULL, NULL, '2026-03-17 15:29:36', '2026-03-17 07:29:36');
INSERT INTO `t_titles` VALUES (823, 83, '内存涨价潮，Java应用成本咋控制？💸', 3, NULL, NULL, NULL, NULL, '2026-03-17 15:29:36', '2026-03-17 07:29:36');
INSERT INTO `t_titles` VALUES (824, 83, '鸿蒙智行新车，Java开发有新机遇吗？🚗', 4, NULL, NULL, NULL, NULL, '2026-03-17 15:29:36', '2026-03-17 07:29:36');
INSERT INTO `t_titles` VALUES (825, 83, '英伟达DLSS5，Java图形性能提升秘籍📚', 5, NULL, NULL, NULL, NULL, '2026-03-17 15:29:36', '2026-03-17 07:29:36');
INSERT INTO `t_titles` VALUES (826, 83, 'OpenClaw新进展，Java与AI咋融合？🤖', 6, NULL, NULL, NULL, NULL, '2026-03-17 15:29:36', '2026-03-17 07:29:36');
INSERT INTO `t_titles` VALUES (827, 83, '央视曝光AI投毒，Java安全咋保障？🔒', 7, NULL, NULL, NULL, NULL, '2026-03-17 15:29:36', '2026-03-17 07:29:36');
INSERT INTO `t_titles` VALUES (828, 83, '小米SU7底盘揭秘，Java汽车开发新思路🚘', 8, NULL, NULL, NULL, NULL, '2026-03-17 15:29:36', '2026-03-17 07:29:36');
INSERT INTO `t_titles` VALUES (829, 83, '华为账号异常，Java应用稳定性咋确保？💪', 9, NULL, NULL, NULL, NULL, '2026-03-17 15:29:36', '2026-03-17 07:29:36');
INSERT INTO `t_titles` VALUES (830, 83, '追觅旗舰手机，Java开发适配要点📝', 10, NULL, NULL, NULL, NULL, '2026-03-17 15:29:36', '2026-03-17 07:29:36');
INSERT INTO `t_titles` VALUES (831, 84, 'AI写代码吓到我，Java开发者要失业？😭', 1, NULL, NULL, NULL, NULL, '2026-03-17 15:29:36', '2026-03-17 07:29:36');
INSERT INTO `t_titles` VALUES (832, 84, '职场压力大，Java人何时能逆袭？💪', 2, NULL, NULL, NULL, NULL, '2026-03-17 15:29:36', '2026-03-17 07:29:36');
INSERT INTO `t_titles` VALUES (833, 84, '行业竞争激烈，Java开发者出路在哪？😫', 3, NULL, NULL, NULL, NULL, '2026-03-17 15:29:36', '2026-03-17 07:29:36');
INSERT INTO `t_titles` VALUES (834, 84, '技术更新快，Java人学习压力好大啊😣', 4, NULL, NULL, NULL, NULL, '2026-03-17 15:29:36', '2026-03-17 07:29:36');
INSERT INTO `t_titles` VALUES (835, 84, '薪资没涨，Java开发者何时能加薪？🥺', 5, NULL, NULL, NULL, NULL, '2026-03-17 15:29:36', '2026-03-17 07:29:36');
INSERT INTO `t_titles` VALUES (836, 84, '项目难题多，Java人何时能轻松点？😩', 6, NULL, NULL, NULL, NULL, '2026-03-17 15:29:36', '2026-03-17 07:29:36');
INSERT INTO `t_titles` VALUES (837, 84, '市场变化快，Java开发者如何应对？🤯', 7, NULL, NULL, NULL, NULL, '2026-03-17 15:29:36', '2026-03-17 07:29:36');
INSERT INTO `t_titles` VALUES (838, 84, '同行竞争强，Java人优势在哪呢？😕', 8, NULL, NULL, NULL, NULL, '2026-03-17 15:29:36', '2026-03-17 07:29:36');
INSERT INTO `t_titles` VALUES (839, 84, '技术瓶颈难突破，Java开发者好焦虑😭', 9, NULL, NULL, NULL, NULL, '2026-03-17 15:29:36', '2026-03-17 07:29:36');
INSERT INTO `t_titles` VALUES (840, 84, '加班成常态，Java人何时能双休？🙏', 10, NULL, NULL, NULL, NULL, '2026-03-17 15:29:36', '2026-03-17 07:29:36');
INSERT INTO `t_titles` VALUES (841, 85, '如果Java开发者去养虾...太上头了🦐', 1, NULL, NULL, NULL, NULL, '2026-03-17 15:29:36', '2026-03-17 07:29:36');
INSERT INTO `t_titles` VALUES (842, 85, 'Java遇上职场宫斗剧，谁能笑到最后？🎭', 2, NULL, NULL, NULL, NULL, '2026-03-17 15:29:36', '2026-03-17 07:29:36');
INSERT INTO `t_titles` VALUES (843, 85, '当Java代码遇上黄金投资，会擦出啥火花？💎', 3, NULL, NULL, NULL, NULL, '2026-03-17 15:29:36', '2026-03-17 07:29:36');
INSERT INTO `t_titles` VALUES (844, 85, 'Java开发者开特斯拉，代码灵感会爆棚吗？🚗', 4, NULL, NULL, NULL, NULL, '2026-03-17 15:29:36', '2026-03-17 07:29:36');
INSERT INTO `t_titles` VALUES (845, 85, '假如Java和机器人打网球，谁能赢？🎾', 5, NULL, NULL, NULL, NULL, '2026-03-17 15:29:36', '2026-03-17 07:29:36');
INSERT INTO `t_titles` VALUES (846, 85, 'Java碰上国际局势，会有啥奇妙反应？🌍', 6, NULL, NULL, NULL, NULL, '2026-03-17 15:29:36', '2026-03-17 07:29:36');
INSERT INTO `t_titles` VALUES (847, 85, '当Java开发者追新三金，理财思路变了吗？💰', 7, NULL, NULL, NULL, NULL, '2026-03-17 15:29:36', '2026-03-17 07:29:36');
INSERT INTO `t_titles` VALUES (848, 85, 'Java与南极游结合，会有新商机吗？❄️', 8, NULL, NULL, NULL, NULL, '2026-03-17 15:29:36', '2026-03-17 07:29:36');
INSERT INTO `t_titles` VALUES (849, 85, '如果Java代码能变成美食，会是啥味道？🍔', 9, NULL, NULL, NULL, NULL, '2026-03-17 15:29:36', '2026-03-17 07:29:36');
INSERT INTO `t_titles` VALUES (850, 85, 'Java开发者玩QQ宠物，能开发新玩法吗？🐾', 10, NULL, NULL, NULL, NULL, '2026-03-17 15:29:36', '2026-03-17 07:29:36');

-- ----------------------------
-- Table structure for t_users
-- ----------------------------
DROP TABLE IF EXISTS `t_users`;
CREATE TABLE `t_users`  (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '用户唯一ID',
  `username` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '登录用户名，唯一',
  `password` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '密码（存储加密后的哈希值）',
  `name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '真实姓名或昵称',
  `department` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '所属部门',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `username`(`username` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 4 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '用户表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of t_users
-- ----------------------------
INSERT INTO `t_users` VALUES (1, 'admin', '123', '张三', '运营1部', '2026-02-22 14:48:35');
INSERT INTO `t_users` VALUES (2, 'itbaizhan', '123456', '王磊', '运营2部', '2026-02-25 21:54:34');
INSERT INTO `t_users` VALUES (3, 'kaiwen', 'kaiwen', '凯文', '小店1部', '2026-02-26 14:56:56');

-- ----------------------------
-- 2026-06-23 新增：发布记录表加字段
-- ----------------------------
ALTER TABLE `t_publish_records`
ADD COLUMN `xhs_id` int(11) NOT NULL DEFAULT 0 COMMENT '小红书账号ID' AFTER `title_id`;

ALTER TABLE `t_publish_records`
ADD COLUMN `title_title` varchar(255) DEFAULT NULL COMMENT '标题内容' AFTER `title_id`;

ALTER TABLE `t_publish_records`
ADD COLUMN `xhs_name` varchar(100) DEFAULT NULL COMMENT '小红书账号昵称' AFTER `xhs_id`;

ALTER TABLE `t_publish_records`
ADD COLUMN `note_url` varchar(255) DEFAULT NULL COMMENT '笔记链接' AFTER `xhs_id`;

ALTER TABLE `t_publish_records`
ADD COLUMN `complete_url` varchar(255) DEFAULT NULL COMMENT '完整笔记URL' AFTER `note_url`;

ALTER TABLE `t_publish_records`
ADD COLUMN `collected_count` int(11) DEFAULT 0 COMMENT '收藏量' AFTER `share_count`;

-- ----------------------------
-- 2026-06-23 新增：发布图片表加字段
-- ----------------------------
ALTER TABLE `t_publish_images`
ADD COLUMN `image_url` varchar(255) NOT NULL DEFAULT '' COMMENT '图片URL' AFTER `image_id`;

-- ----------------------------
-- Table structure for t_xhs_accounts（新增）
-- ----------------------------
DROP TABLE IF EXISTS `t_xhs_accounts`;
CREATE TABLE `t_xhs_accounts` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT DEFAULT NULL COMMENT '所属用户',
  `name` VARCHAR(100) DEFAULT NULL COMMENT '账号昵称',
  `a1` VARCHAR(255) NOT NULL COMMENT 'cookie a1',
  `web_session` VARCHAR(255) NOT NULL COMMENT 'cookie web_session',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_user_web_session` (`user_id`, `web_session`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='小红书账号表';

-- ----------------------------
-- Table structure for t_material_text（新增）
-- ----------------------------
DROP TABLE IF EXISTS `t_material_text`;
CREATE TABLE `t_material_text` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT DEFAULT NULL COMMENT '所属用户',
  `title` VARCHAR(255) DEFAULT NULL COMMENT '标题',
  `content` TEXT DEFAULT NULL COMMENT '内容',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='素材文案表';

-- ----------------------------
-- Table structure for t_material_image（新增）
-- ----------------------------
DROP TABLE IF EXISTS `t_material_image`;
CREATE TABLE `t_material_image` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT DEFAULT NULL COMMENT '所属用户',
  `image_url` VARCHAR(255) NOT NULL COMMENT '图片 URL',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='素材图片表';

SET FOREIGN_KEY_CHECKS = 1;
