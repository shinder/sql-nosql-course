--
-- shin02 資料庫 PostgreSQL 版本
-- 來源：phpMyAdmin SQL Dump (MariaDB 10.6.22)
-- 轉換日期：2026-04-25
--
-- 主要改寫：
--   * `int(11)`               -> INTEGER
--   * AUTO_INCREMENT          -> SERIAL（自動建立 sequence）
--   * datetime / datetime(3)  -> TIMESTAMP / TIMESTAMP(3)
--   * varchar(N)              -> VARCHAR(N)
--   * 反引號 `xxx`            -> 不加引號（一般識別符號）或 "xxx"（含特殊字元）
--   * 移除 ENGINE / CHARSET / COLLATE（PostgreSQL 由資料庫層級設定）
--   * 表名 Hobby / Post 改為小寫 hobby / post（PostgreSQL 慣例）
--   * 欄位 `last-name` 因含連字號，保留雙引號 "last-name"
--   * AUTO_INCREMENT=N 起始值改用 setval() 校正 sequence
--
-- 執行方式（須透過 psql，因為下面用到 \gexec、\c 等 metacommand）：
--   psql -d postgres -f shin02-pg.sql
--

-- =====================================================
-- 若 shin02 資料庫不存在則建立，然後切換進去
-- （PostgreSQL 沒有 CREATE DATABASE IF NOT EXISTS，
--   用 \gexec 動態執行查詢結果產生的 SQL）
-- =====================================================

/* SELECT 'CREATE DATABASE shin02'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'shin02')\gexec

\c shin02 */


BEGIN;

-- =====================================================
-- 為了可重複執行，先清除舊資料表（依外鍵相反順序）
-- =====================================================
DROP TABLE IF EXISTS ab_likes      CASCADE;
DROP TABLE IF EXISTS order_details CASCADE;
DROP TABLE IF EXISTS orders        CASCADE;
DROP TABLE IF EXISTS products      CASCADE;
DROP TABLE IF EXISTS categories    CASCADE;
DROP TABLE IF EXISTS address_book  CASCADE;
DROP TABLE IF EXISTS members       CASCADE;
DROP TABLE IF EXISTS post          CASCADE;
DROP TABLE IF EXISTS users         CASCADE;
DROP TABLE IF EXISTS hobby         CASCADE;


-- =====================================================
-- members
-- =====================================================
CREATE TABLE members (
  member_id     SERIAL PRIMARY KEY,
  email         VARCHAR(100) NOT NULL UNIQUE,
  password_hash VARCHAR(100) NOT NULL,
  mobile        VARCHAR(30),
  nickname      VARCHAR(30)  NOT NULL,
  create_at     TIMESTAMP    NOT NULL
);

INSERT INTO members (member_id, email, password_hash, mobile, nickname, create_at) VALUES
  (3, 'ming@test.com', '$2b$12$oKaX5/UXXNQv5oEFWGWr2.ER.jL2DBs7w.ErhuglqmUH4.YMBeZie', '0918222333', '大明',   '2019-01-07 10:39:38'),
  (7, 'shin@test.com', '$2b$12$oKaX5/UXXNQv5oEFWGWr2.ER.jL2DBs7w.ErhuglqmUH4.YMBeZie', '0918222555', '小新',   '2020-09-17 10:30:38'),
  (8, 'mary@test.com', '$2b$12$oKaX5/UXXNQv5oEFWGWr2.ER.jL2DBs7w.ErhuglqmUH4.YMBeZie', '0918222555', '瑪麗亞', '2020-09-17 10:30:38');


-- =====================================================
-- address_book
-- =====================================================
CREATE TABLE address_book (
  ab_id      SERIAL PRIMARY KEY,
  name       VARCHAR(255) NOT NULL,
  email      VARCHAR(255) NOT NULL,
  mobile     VARCHAR(255) NOT NULL,
  birthday   DATE,
  address    VARCHAR(255) NOT NULL,
  created_at TIMESTAMP    NOT NULL,
  updated_at TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO address_book (ab_id, name, email, mobile, birthday, address, created_at, updated_at) VALUES
  (1,  '高鈺婷', 'mail72522@test.com', '0918911926', '1998-01-30', '屏東縣', '2024-07-08 09:52:01', '2024-07-08 09:52:01'),
  (2,  '曾怡君', 'mail49240@test.com', '0918762681', '1996-09-12', '南投縣', '2024-07-08 09:52:01', '2024-07-08 09:52:01'),
  (3,  '羅雅婷', 'mail22544@test.com', '0918962840', '1992-09-26', '新北市', '2024-07-08 09:52:01', '2024-07-08 09:52:01'),
  (4,  '曹雅婷', 'mail21172@test.com', '0918255840', '1991-03-03', '新竹市', '2024-07-08 09:52:01', '2024-07-08 09:52:01'),
  (5,  '朱冠宇', 'mail87166@test.com', '0918272435', '1988-10-26', '嘉義市', '2024-07-08 09:52:01', '2024-07-08 09:52:01'),
  (6,  '於雅婷', 'mail31122@test.com', '0918838719', '1993-09-27', '新竹市', '2024-07-08 09:52:01', '2024-07-08 09:52:01'),
  (7,  '鄧宗翰', 'mail44439@test.com', '0918108125', '1990-03-15', '苗栗縣', '2024-07-08 09:52:01', '2024-07-08 09:52:01'),
  (8,  '李彥廷', 'mail59396@test.com', '0918706116', '1988-04-22', '嘉義市', '2024-07-08 09:52:01', '2024-07-08 09:52:01'),
  (9,  '沈家瑋', 'mail26479@test.com', '0918992248', '1990-11-15', '新竹市', '2024-07-08 09:52:01', '2024-07-08 09:52:01'),
  (10, '何雅筑', 'mail81631@test.com', '0918959070', '1991-10-05', '基隆市', '2024-07-08 09:52:01', '2024-07-08 09:52:01'),
  (11, '宋雅筑', 'mail95623@test.com', '0918550912', '1989-10-24', '雲林縣', '2024-07-08 09:52:01', '2024-07-08 09:52:01'),
  (12, '蕭佳穎', 'mail64017@test.com', '0918266742', '1985-03-01', '新竹市', '2024-07-08 09:52:01', '2024-07-08 09:52:01'),
  (13, '沈佳穎', 'mail44215@test.com', '0918367123', '1992-11-13', '新竹市', '2024-07-08 09:52:01', '2024-07-08 09:52:01'),
  (14, '鄧家瑋', 'mail31405@test.com', '0918438995', '1985-01-24', '臺南市', '2024-07-08 09:52:01', '2024-07-08 09:52:01'),
  (15, '蕭冠廷', 'mail16640@test.com', '0918517444', '1996-09-21', '臺東縣', '2024-07-08 09:52:01', '2024-07-08 09:52:01'),
  (16, '馮怡婷', 'mail83277@test.com', '0918709341', '1998-09-13', '屏東縣', '2024-07-08 09:52:01', '2024-07-08 09:52:01'),
  (17, '唐郁婷', 'mail15342@test.com', '0918227022', '1985-12-22', '桃園市', '2024-07-08 09:52:01', '2024-07-08 09:52:01'),
  (18, '唐詩涵', 'mail20426@test.com', '0918658069', '1996-02-03', '高雄市', '2024-07-08 09:52:01', '2024-07-08 09:52:01'),
  (19, '王雅婷', 'mail48272@test.com', '0918383777', '1989-10-12', '屏東縣', '2024-07-08 09:52:01', '2024-07-08 09:52:01'),
  (20, '張承翰', 'mail84311@test.com', '0918385918', '1985-08-19', '苗栗縣', '2024-07-08 09:52:01', '2024-07-08 09:52:01');


-- 觸發器：UPDATE 時自動把 updated_at 設成當下時間
-- ---------------------------------------------------
-- PostgreSQL 沒有 MySQL 的 ON UPDATE CURRENT_TIMESTAMP 欄位層級語法，
-- 「自動更新時間欄位」這種需求在 PostgreSQL 必須用 trigger 達成。

-- 觸發函式：BEFORE UPDATE 時把 NEW.updated_at 設成當下時間。
-- 設計成通用函式（沒寫死表名），未來其他表也想要這個行為時可以共用同一個函式。
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = CURRENT_TIMESTAMP;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 把上面的函式掛到 address_book 上，BEFORE UPDATE 觸發。
-- 注意：只要有 UPDATE 就會觸發（即使 SET name = name 這種沒實際改值的也算）。
-- 想嚴格「只在欄位真的變動時才更新」的話，把函式改成：
--   IF NEW IS DISTINCT FROM OLD THEN NEW.updated_at = CURRENT_TIMESTAMP; END IF;
CREATE TRIGGER address_book_set_updated_at
BEFORE UPDATE ON address_book
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();


-- =====================================================
-- categories（含自我參照外鍵 parent_id）
-- =====================================================
CREATE TABLE categories (
  category_id SERIAL PRIMARY KEY,
  name        VARCHAR(30) NOT NULL,
  parent_id   INTEGER     REFERENCES categories(category_id)
);

CREATE INDEX idx_categories_parent_id ON categories(parent_id);

INSERT INTO categories (category_id, name, parent_id) VALUES
  (1, '程式設計',     NULL),
  (2, '繪圖軟體',     NULL),
  (3, '網際網路應用', NULL),
  (4, 'PHP',          1),
  (5, 'JavaScript',   1),
  (6, 'Illustrator',  2),
  (7, 'PhotoShop',    2),
  (8, 'Chrome',       3),
  (9, 'C++',          1);


-- =====================================================
-- products
-- =====================================================
CREATE TABLE products (
  product_id   SERIAL PRIMARY KEY,
  author       VARCHAR(50) NOT NULL,
  book_name    VARCHAR(60) NOT NULL,
  category_id  INTEGER     NOT NULL REFERENCES categories(category_id),
  publish_date DATE        NOT NULL,
  pages        INTEGER     NOT NULL,
  price        INTEGER     NOT NULL,
  isbn         VARCHAR(30) NOT NULL UNIQUE
);

CREATE INDEX idx_products_category_id ON products(category_id);

INSERT INTO products (product_id, author, book_name, category_id, publish_date, pages, price, isbn) VALUES
  (1,  '洪一新、許瑞珍',         '圖解C++程式設計',                                            1, '2010-02-08', 624, 560, '978-986-201-306-9 '),
  (2,  '吳睿紘',                 '圖解資料結構-使用JAVA',                                      1, '2009-12-15', 384, 420, '978-986-201-281-9 '),
  (3,  '江家頡、陳怡均',         'Visual C# 2008網路遊戲程式設計',                             1, '2009-11-27', 424, 480, '978-986-201-278-9 '),
  (4,  '結城 浩',                'Java 重構- Java Refactoring',                                1, '2010-01-21', 432, 490, '978-986-201-087-7 '),
  (5,  '平田豊',                 'Linux Device Driver Programming 驅動程式設計',               1, '2009-01-05', 624, 690, '978-986-201-186-7 '),
  (6,  '王鴻儒',                 'Excel VBA 2007程式設計 - 增訂新版',                          1, '2008-05-27', 400, 450, '978-986-201-129-4'),
  (7,  '姜姃延',                 '彩繪天堂Painter數位插畫輕鬆學',                              2, '2009-09-14', 448, 550, '978-986-201-255-0'),
  (8,  '金惠京',                 '不一樣的創作設計風格- Photoshop Artworks Stylebook ',        2, '2009-11-30', 304, 520, '978-986-201-276-5'),
  (9,  '大室はじめ Hajime',      '日式風格藝術紋樣素材選集',                                   2, '2009-03-09', 128, 350, '978-986-201-203-1'),
  (10, '五島由實',               'Illustrator GOODS COLLECTION',                               2, '2008-10-29', 192, 350, '978-986-201-172-0 '),
  (11, '久米原榮、上田浩',       'Wireshark 網路協定分析與管理',                               3, '2010-01-12', 400, 480, '978-986-201-292-5'),
  (12, '陳佩婷',                 'Flash CS4動畫設計應用集',                                    3, '2010-01-07', 464, 520, '978-986-201-290-1'),
  (13, '陳東偉',                 'Internet網路實務與應用',                                     3, '2010-01-04', 512, 500, '978-986-201-286-4'),
  (14, '奧山壽史',               '打開就能用的整站網頁設計範例集',                             3, '2009-12-23', 176, 380, '978-986-201-284-0'),
  (15, 'Time研究室 陳錦輝',      'ASP.NET 3.5初學指引-使用Visual Basic 2008',                  3, '2009-10-29', 896, 650, '978-986-201-270-3'),
  (16, '榮欽科技 鄭苑鳳',        'Dreamweaver CS4網頁設計應用集',                              3, '2009-09-07', 480, 520, '978-986-201-261-1'),
  (17, '賈蓉生、胡大源、許世豪', 'Java互動網站實作 -JSP與資料庫',                              3, '2009-08-13', 656, 620, '978-986-201-250-5'),
  (18, '田中康博、林拓也',       'ActionScript 3.0 活用範例大辭典',                            3, '2009-03-23', 544, 550, '978-986-201-207-9'),
  (19, '數位新知',               '網頁設計應用集 -Dreamweaver+PhotoImpact+Flash',               3, '2009-03-16', 464, 520, '978-986-201-202-4'),
  (20, '陳湘揚 ',                '網路概論(第二版)',                                           3, '2008-12-30', 592, 580, '978-986-201-187-4'),
  (21, '林季嫻',                 'Joomla圖解架站實例應用',                                     3, '2008-11-25', 560, 490, '978-986-201-178-2'),
  (22, '前沿科技 溫謙',          'Web CSS網頁設計大全',                                        3, '2008-10-29', 448, 580, '978-986-201-169-0'),
  (23, '林新德',                 'Flash CS3 ActionScript 3.0應用程式設計',                     3, '2007-11-22', 560, 520, '978-986-201-067-9');


-- =====================================================
-- orders
-- =====================================================
CREATE TABLE orders (
  order_id   SERIAL PRIMARY KEY,
  member_id  INTEGER   NOT NULL REFERENCES members(member_id),
  amount     INTEGER   NOT NULL,
  ordered_at TIMESTAMP NOT NULL
);

CREATE INDEX idx_orders_member_id ON orders(member_id);

INSERT INTO orders (order_id, member_id, amount, ordered_at) VALUES
  (5,  3, 1820, '2016-03-25 12:19:05'),
  (10, 7, 1460, '2016-06-01 11:15:53'),
  (11, 3, 2030, '2017-10-03 13:49:20');


-- =====================================================
-- order_details
-- =====================================================
CREATE TABLE order_details (
  od_id      SERIAL PRIMARY KEY,
  order_id   INTEGER NOT NULL REFERENCES orders(order_id),
  product_id INTEGER NOT NULL REFERENCES products(product_id),
  price      INTEGER NOT NULL,
  quantity   INTEGER NOT NULL
);

CREATE INDEX idx_order_details_order_id   ON order_details(order_id);
CREATE INDEX idx_order_details_product_id ON order_details(product_id);

INSERT INTO order_details (od_id, order_id, product_id, price, quantity) VALUES
  (4,  5,  22, 580, 1),
  (5,  5,  17, 620, 2),
  (9,  10, 1,  560, 1),
  (10, 10, 2,  420, 1),
  (11, 10, 3,  480, 1),
  (12, 11, 5,  690, 2),
  (13, 11, 15, 650, 1),
  (14, 11, 3,  480, 2);


-- =====================================================
-- ab_likes
-- =====================================================
CREATE TABLE ab_likes (
  like_id    SERIAL PRIMARY KEY,
  member_id  INTEGER   NOT NULL REFERENCES members(member_id),
  ab_id      INTEGER   NOT NULL REFERENCES address_book(ab_id),
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (member_id, ab_id)
);

CREATE INDEX idx_ab_likes_member_id ON ab_likes(member_id);
CREATE INDEX idx_ab_likes_ab_id     ON ab_likes(ab_id);


-- =====================================================
-- hobby（原 MariaDB 表名 Hobby，PostgreSQL 慣用小寫）
-- =====================================================
CREATE TABLE hobby (
  id   SERIAL PRIMARY KEY,
  name VARCHAR(191) NOT NULL
);


-- =====================================================
-- users
-- =====================================================
CREATE TABLE users (
  id           SERIAL PRIMARY KEY,
  first_name   VARCHAR(191) NOT NULL,
  "last-name"  VARCHAR(191) NOT NULL,
  email        VARCHAR(191) NOT NULL UNIQUE,
  created_at   TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at   TIMESTAMP(3) NOT NULL,
  password     VARCHAR(191) NOT NULL DEFAULT ''
);


-- =====================================================
-- post（原 MariaDB 表名 Post，PostgreSQL 慣用小寫）
-- =====================================================
CREATE TABLE post (
  id        SERIAL PRIMARY KEY,
  content   TEXT    NOT NULL,
  author_id INTEGER NOT NULL REFERENCES users(id) ON UPDATE CASCADE
);

CREATE INDEX idx_post_author_id ON post(author_id);


-- =====================================================
-- 校正 SERIAL sequence 起始值
-- （對應原 MariaDB 的 AUTO_INCREMENT=N 設定）
-- 用 setval(seq, N, false) 表示「下次取出的值就是 N」
-- =====================================================
SELECT setval('ab_likes_like_id_seq',         4,    false);
SELECT setval('address_book_ab_id_seq',       1003, false);
SELECT setval('categories_category_id_seq',   10,   false);
SELECT setval('members_member_id_seq',        9,    false);
SELECT setval('orders_order_id_seq',          12,   false);
SELECT setval('order_details_od_id_seq',      15,   false);
SELECT setval('products_product_id_seq',      24,   false);
-- hobby / post / users 原本沒有指定 AUTO_INCREMENT，PostgreSQL 會自動從 1 開始

COMMIT;
