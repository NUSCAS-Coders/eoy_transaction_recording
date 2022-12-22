-- Adminer 4.8.1 MySQL 8.0.31 dump

SET NAMES utf8;
SET time_zone = '+00:00';
SET foreign_key_checks = 0;
SET sql_mode = 'NO_AUTO_VALUE_ON_ZERO';

SET NAMES utf8mb4;

CREATE DATABASE dbs_webapp;
USE dbs_webapp;

DROP TABLE IF EXISTS `user`;
CREATE TABLE `user` (
  `username` varchar(80) NOT NULL,
  `email` varchar(80) NOT NULL,
  `password_salt` varchar(80) NOT NULL,
  `password_hash` varchar(80) NOT NULL,
  `id` varchar(80) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


-- 2022-11-29 16:35:29
