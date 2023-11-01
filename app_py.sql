-- phpMyAdmin SQL Dump
-- version 5.1.1
-- https://www.phpmyadmin.net/
--
-- Hôte : 127.0.0.1:3306
-- Généré le : mer. 01 nov. 2023 à 12:11
-- Version du serveur : 5.7.36
-- Version de PHP : 7.4.26

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de données : `app_py`
--

-- --------------------------------------------------------

--
-- Structure de la table `alertes`
--

DROP TABLE IF EXISTS `alertes`;
CREATE TABLE IF NOT EXISTS `alertes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cryptomonnaie` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `prix` float NOT NULL,
  `devise` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Déchargement des données de la table `alertes`
--

INSERT INTO `alertes` (`id`, `cryptomonnaie`, `prix`, `devise`) VALUES
(19, 'BTC', 49000, 'USD'),
(20, 'BTC', 48000, 'USD'),
(21, 'BTC', 5000, 'USD'),
(22, 'BTC', 50000, 'USD'),
(23, 'BTC', 45000, 'USD'),
(24, 'BTC', 6000, 'BTC'),
(25, 'BTC', 40000, 'USD');

-- --------------------------------------------------------

--
-- Structure de la table `user`
--

DROP TABLE IF EXISTS `user`;
CREATE TABLE IF NOT EXISTS `user` (
  `userid` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  PRIMARY KEY (`userid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Déchargement des données de la table `user`
--

INSERT INTO `user` (`userid`, `name`, `email`, `password`) VALUES
(1, 'Jhon smith', 'smith@webdamn.com', '123'),
(2, 'Adam William', 'adam@webdamn.com', '123');
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
