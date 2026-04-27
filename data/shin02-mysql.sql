-- phpMyAdmin SQL Dump
-- version 4.9.11
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Apr 25, 2026 at 09:15 PM
-- Server version: 10.6.22-MariaDB-0ubuntu0.22.04.1
-- PHP Version: 5.6.40-81+ubuntu22.04.1+deb.sury.org+1

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `shin02`
--

-- --------------------------------------------------------

--
-- Table structure for table `ab_likes`
--

CREATE TABLE `ab_likes` (
  `like_id` int(11) NOT NULL,
  `member_id` int(11) NOT NULL,
  `ab_id` int(11) NOT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `address_book`
--

CREATE TABLE `address_book` (
  `ab_id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `mobile` varchar(255) NOT NULL,
  `birthday` date DEFAULT NULL,
  `address` varchar(255) NOT NULL,
  `created_at` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `address_book`
--

INSERT INTO `address_book` (`ab_id`, `name`, `email`, `mobile`, `birthday`, `address`, `created_at`) VALUES
(1, '高鈺婷', 'mail72522@test.com', '0918911926', '1998-01-30', '屏東縣', '2024-07-08 09:52:01'),
(2, '曾怡君', 'mail49240@test.com', '0918762681', '1996-09-12', '南投縣', '2024-07-08 09:52:01'),
(3, '羅雅婷', 'mail22544@test.com', '0918962840', '1992-09-26', '新北市', '2024-07-08 09:52:01'),
(4, '曹雅婷', 'mail21172@test.com', '0918255840', '1991-03-03', '新竹市', '2024-07-08 09:52:01'),
(5, '朱冠宇', 'mail87166@test.com', '0918272435', '1988-10-26', '嘉義市', '2024-07-08 09:52:01'),
(6, '於雅婷', 'mail31122@test.com', '0918838719', '1993-09-27', '新竹市', '2024-07-08 09:52:01'),
(7, '鄧宗翰', 'mail44439@test.com', '0918108125', '1990-03-15', '苗栗縣', '2024-07-08 09:52:01'),
(8, '李彥廷', 'mail59396@test.com', '0918706116', '1988-04-22', '嘉義市', '2024-07-08 09:52:01'),
(9, '沈家瑋', 'mail26479@test.com', '0918992248', '1990-11-15', '新竹市', '2024-07-08 09:52:01'),
(10, '何雅筑', 'mail81631@test.com', '0918959070', '1991-10-05', '基隆市', '2024-07-08 09:52:01'),
(11, '宋雅筑', 'mail95623@test.com', '0918550912', '1989-10-24', '雲林縣', '2024-07-08 09:52:01'),
(12, '蕭佳穎', 'mail64017@test.com', '0918266742', '1985-03-01', '新竹市', '2024-07-08 09:52:01'),
(13, '沈佳穎', 'mail44215@test.com', '0918367123', '1992-11-13', '新竹市', '2024-07-08 09:52:01'),
(14, '鄧家瑋', 'mail31405@test.com', '0918438995', '1985-01-24', '臺南市', '2024-07-08 09:52:01'),
(15, '蕭冠廷', 'mail16640@test.com', '0918517444', '1996-09-21', '臺東縣', '2024-07-08 09:52:01'),
(16, '馮怡婷', 'mail83277@test.com', '0918709341', '1998-09-13', '屏東縣', '2024-07-08 09:52:01'),
(17, '唐郁婷', 'mail15342@test.com', '0918227022', '1985-12-22', '桃園市', '2024-07-08 09:52:01'),
(18, '唐詩涵', 'mail20426@test.com', '0918658069', '1996-02-03', '高雄市', '2024-07-08 09:52:01'),
(19, '王雅婷', 'mail48272@test.com', '0918383777', '1989-10-12', '屏東縣', '2024-07-08 09:52:01'),
(20, '張承翰', 'mail84311@test.com', '0918385918', '1985-08-19', '苗栗縣', '2024-07-08 09:52:01');

-- --------------------------------------------------------

--
-- Table structure for table `categories`
--

CREATE TABLE `categories` (
  `category_id` int(11) NOT NULL,
  `name` varchar(30) NOT NULL,
  `parent_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `categories`
--

INSERT INTO `categories` (`category_id`, `name`, `parent_id`) VALUES
(1, '程式設計', NULL),
(2, '繪圖軟體', NULL),
(3, '網際網路應用', NULL),
(4, 'PHP', 1),
(5, 'JavaScript', 1),
(6, 'Illustrator', 2),
(7, 'PhotoShop', 2),
(8, 'Chrome', 3),
(9, 'C++', 1);

-- --------------------------------------------------------

--
-- Table structure for table `Hobby`
--

CREATE TABLE `Hobby` (
  `id` int(11) NOT NULL,
  `name` varchar(191) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `members`
--

CREATE TABLE `members` (
  `member_id` int(11) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password_hash` varchar(100) NOT NULL,
  `mobile` varchar(30) DEFAULT NULL,
  `nickname` varchar(30) NOT NULL,
  `create_at` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `members`
--

INSERT INTO `members` (`member_id`, `email`, `password_hash`, `mobile`, `nickname`, `create_at`) VALUES
(3, 'ming@test.com', '$2b$12$oKaX5/UXXNQv5oEFWGWr2.ER.jL2DBs7w.ErhuglqmUH4.YMBeZie', '0918222333', '大明', '2019-01-07 10:39:38'),
(7, 'shin@test.com', '$2b$12$oKaX5/UXXNQv5oEFWGWr2.ER.jL2DBs7w.ErhuglqmUH4.YMBeZie', '0918222555', '小新', '2020-09-17 10:30:38'),
(8, 'mary@test.com', '$2b$12$oKaX5/UXXNQv5oEFWGWr2.ER.jL2DBs7w.ErhuglqmUH4.YMBeZie', '0918222555', '瑪麗亞', '2020-09-17 10:30:38');

-- --------------------------------------------------------

--
-- Table structure for table `orders`
--

CREATE TABLE `orders` (
  `order_id` int(11) NOT NULL,
  `member_id` int(11) NOT NULL,
  `amount` int(11) NOT NULL,
  `ordered_at` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `orders`
--

INSERT INTO `orders` (`order_id`, `member_id`, `amount`, `ordered_at`) VALUES
(5, 3, 1820, '2016-03-25 12:19:05'),
(10, 7, 1460, '2016-06-01 11:15:53'),
(11, 3, 2030, '2017-10-03 13:49:20');

-- --------------------------------------------------------

--
-- Table structure for table `order_details`
--

CREATE TABLE `order_details` (
  `od_id` int(11) NOT NULL,
  `order_id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `price` int(11) NOT NULL,
  `quantity` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `order_details`
--

INSERT INTO `order_details` (`od_id`, `order_id`, `product_id`, `price`, `quantity`) VALUES
(4, 5, 22, 580, 1),
(5, 5, 17, 620, 2),
(9, 10, 1, 560, 1),
(10, 10, 2, 420, 1),
(11, 10, 3, 480, 1),
(12, 11, 5, 690, 2),
(13, 11, 15, 650, 1),
(14, 11, 3, 480, 2);

-- --------------------------------------------------------

--
-- Table structure for table `Post`
--

CREATE TABLE `Post` (
  `id` int(11) NOT NULL,
  `content` text NOT NULL,
  `author_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `products`
--

CREATE TABLE `products` (
  `product_id` int(11) NOT NULL,
  `author` varchar(50) NOT NULL,
  `book_name` varchar(60) NOT NULL,
  `category_id` int(11) NOT NULL,
  `publish_date` date NOT NULL,
  `pages` int(11) NOT NULL,
  `price` int(11) NOT NULL,
  `isbn` varchar(30) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `products`
--

INSERT INTO `products` (`product_id`, `author`, `book_name`, `category_id`, `publish_date`, `pages`, `price`, `isbn`) VALUES
(1, '洪一新、許瑞珍', '圖解C++程式設計', 1, '2010-02-08', 624, 560, '978-986-201-306-9 '),
(2, '吳睿紘', '圖解資料結構-使用JAVA', 1, '2009-12-15', 384, 420, '978-986-201-281-9 '),
(3, '江家頡、陳怡均', 'Visual C# 2008網路遊戲程式設計', 1, '2009-11-27', 424, 480, '978-986-201-278-9 '),
(4, '結城 浩', 'Java 重構- Java Refactoring', 1, '2010-01-21', 432, 490, '978-986-201-087-7 '),
(5, '平田豊', 'Linux Device Driver Programming 驅動程式設計', 1, '2009-01-05', 624, 690, '978-986-201-186-7 '),
(6, '王鴻儒', 'Excel VBA 2007程式設計 - 增訂新版', 1, '2008-05-27', 400, 450, '978-986-201-129-4'),
(7, '姜姃延', '彩繪天堂Painter數位插畫輕鬆學', 2, '2009-09-14', 448, 550, '978-986-201-255-0'),
(8, '金惠京', '不一樣的創作設計風格- Photoshop Artworks Stylebook ', 2, '2009-11-30', 304, 520, '978-986-201-276-5'),
(9, '大室はじめ Hajime', '日式風格藝術紋樣素材選集', 2, '2009-03-09', 128, 350, '978-986-201-203-1'),
(10, '五島由實', 'Illustrator GOODS COLLECTION', 2, '2008-10-29', 192, 350, '978-986-201-172-0 '),
(11, '久米原榮、上田浩', 'Wireshark 網路協定分析與管理', 3, '2010-01-12', 400, 480, '978-986-201-292-5'),
(12, '陳佩婷', 'Flash CS4動畫設計應用集', 3, '2010-01-07', 464, 520, '978-986-201-290-1'),
(13, '陳東偉', 'Internet網路實務與應用', 3, '2010-01-04', 512, 500, '978-986-201-286-4'),
(14, '奧山壽史', '打開就能用的整站網頁設計範例集', 3, '2009-12-23', 176, 380, '978-986-201-284-0'),
(15, 'Time研究室 陳錦輝', 'ASP.NET 3.5初學指引-使用Visual Basic 2008', 3, '2009-10-29', 896, 650, '978-986-201-270-3'),
(16, '榮欽科技 鄭苑鳳', 'Dreamweaver CS4網頁設計應用集', 3, '2009-09-07', 480, 520, '978-986-201-261-1'),
(17, '賈蓉生、胡大源、許世豪', 'Java互動網站實作 -JSP與資料庫', 3, '2009-08-13', 656, 620, '978-986-201-250-5'),
(18, '田中康博、林拓也', 'ActionScript 3.0 活用範例大辭典', 3, '2009-03-23', 544, 550, '978-986-201-207-9'),
(19, '數位新知', '網頁設計應用集 -Dreamweaver+PhotoImpact+Flash', 3, '2009-03-16', 464, 520, '978-986-201-202-4'),
(20, '陳湘揚 ', '網路概論(第二版)', 3, '2008-12-30', 592, 580, '978-986-201-187-4'),
(21, '林季嫻', 'Joomla圖解架站實例應用', 3, '2008-11-25', 560, 490, '978-986-201-178-2'),
(22, '前沿科技 溫謙', 'Web CSS網頁設計大全', 3, '2008-10-29', 448, 580, '978-986-201-169-0'),
(23, '林新德', 'Flash CS3 ActionScript 3.0應用程式設計', 3, '2007-11-22', 560, 520, '978-986-201-067-9');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `first_name` varchar(191) NOT NULL,
  `last-name` varchar(191) NOT NULL,
  `email` varchar(191) NOT NULL,
  `created_at` datetime(3) NOT NULL DEFAULT current_timestamp(3),
  `updated_at` datetime(3) NOT NULL,
  `password` varchar(191) NOT NULL DEFAULT ''
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `ab_likes`
--
ALTER TABLE `ab_likes`
  ADD PRIMARY KEY (`like_id`),
  ADD UNIQUE KEY `member_id_2` (`member_id`,`ab_id`),
  ADD KEY `member_id` (`member_id`),
  ADD KEY `ab_id` (`ab_id`);

--
-- Indexes for table `address_book`
--
ALTER TABLE `address_book`
  ADD PRIMARY KEY (`ab_id`);

--
-- Indexes for table `categories`
--
ALTER TABLE `categories`
  ADD PRIMARY KEY (`category_id`),
  ADD KEY `parent_sid` (`parent_id`);

--
-- Indexes for table `Hobby`
--
ALTER TABLE `Hobby`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `members`
--
ALTER TABLE `members`
  ADD PRIMARY KEY (`member_id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- Indexes for table `orders`
--
ALTER TABLE `orders`
  ADD PRIMARY KEY (`order_id`),
  ADD KEY `member_id` (`member_id`);

--
-- Indexes for table `order_details`
--
ALTER TABLE `order_details`
  ADD PRIMARY KEY (`od_id`),
  ADD KEY `order_id` (`order_id`) USING BTREE,
  ADD KEY `product_id` (`product_id`) USING BTREE;

--
-- Indexes for table `Post`
--
ALTER TABLE `Post`
  ADD PRIMARY KEY (`id`),
  ADD KEY `Post_author_id_fkey` (`author_id`);

--
-- Indexes for table `products`
--
ALTER TABLE `products`
  ADD PRIMARY KEY (`product_id`),
  ADD UNIQUE KEY `isbn` (`isbn`),
  ADD KEY `category_id` (`category_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `users_email_key` (`email`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `ab_likes`
--
ALTER TABLE `ab_likes`
  MODIFY `like_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `address_book`
--
ALTER TABLE `address_book`
  MODIFY `ab_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1003;

--
-- AUTO_INCREMENT for table `categories`
--
ALTER TABLE `categories`
  MODIFY `category_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT for table `Hobby`
--
ALTER TABLE `Hobby`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `members`
--
ALTER TABLE `members`
  MODIFY `member_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT for table `orders`
--
ALTER TABLE `orders`
  MODIFY `order_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- AUTO_INCREMENT for table `order_details`
--
ALTER TABLE `order_details`
  MODIFY `od_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=15;

--
-- AUTO_INCREMENT for table `Post`
--
ALTER TABLE `Post`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `products`
--
ALTER TABLE `products`
  MODIFY `product_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=24;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `ab_likes`
--
ALTER TABLE `ab_likes`
  ADD CONSTRAINT `ab_likes_ibfk_1` FOREIGN KEY (`member_id`) REFERENCES `members` (`member_id`),
  ADD CONSTRAINT `ab_likes_ibfk_2` FOREIGN KEY (`ab_id`) REFERENCES `address_book` (`ab_id`);

--
-- Constraints for table `categories`
--
ALTER TABLE `categories`
  ADD CONSTRAINT `categories_ibfk_1` FOREIGN KEY (`parent_id`) REFERENCES `categories` (`category_id`);

--
-- Constraints for table `orders`
--
ALTER TABLE `orders`
  ADD CONSTRAINT `orders_ibfk_1` FOREIGN KEY (`member_id`) REFERENCES `members` (`member_id`);

--
-- Constraints for table `order_details`
--
ALTER TABLE `order_details`
  ADD CONSTRAINT `order_details_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`order_id`),
  ADD CONSTRAINT `order_details_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`);

--
-- Constraints for table `Post`
--
ALTER TABLE `Post`
  ADD CONSTRAINT `Post_author_id_fkey` FOREIGN KEY (`author_id`) REFERENCES `users` (`id`) ON UPDATE CASCADE;

--
-- Constraints for table `products`
--
ALTER TABLE `products`
  ADD CONSTRAINT `products_ibfk_1` FOREIGN KEY (`category_id`) REFERENCES `categories` (`category_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
