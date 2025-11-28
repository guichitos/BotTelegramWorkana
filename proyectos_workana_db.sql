-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 28-11-2025 a las 22:13:12
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.2.12
SET
  SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";

START TRANSACTION;

SET
  time_zone = "+00:00";

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;

/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;

/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;

/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `proyectos_workana_db`
--
-- --------------------------------------------------------
--
-- Estructura de tabla para la tabla `proyectos`
--
CREATE TABLE `proyectos` (
  `id` int(11) NOT NULL,
  `fecha_hora` datetime DEFAULT NULL,
  `titulo` varchar(255) DEFAULT NULL,
  `descripcion` text DEFAULT NULL,
  `enlace` varchar(255) DEFAULT NULL
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `proyectos`
--
INSERT INTO
  `proyectos` (
    `id`,
    `fecha_hora`,
    `titulo`,
    `descripcion`,
    `enlace`
  )
VALUES
  (
    1,
    '2024-07-06 11:31:35',
    'Asistente virtual para agencia de modelos Onlyfans',
    'Hola,\n\nSoy un francés que tiene una agencia de modelos de OnlyFans. Vivo en Buenos Aires y estoy buscando una asistente virtual para ayudarme a clasificar las solicitudes de modelos en mi agencia porque recibimos muchas cada día.\n\nAdemás, necesitaré tu ayuda para gestionar mi agenda y realizar algunas tareas de community managem ... Ver más detalles',
    'https://www.workana.com/job/asistente-virtual-para-agencia-de-modelos-onlyfans?ref=projects_1'
  ),
  (
    2,
    '2024-07-06 11:32:18',
    '¡Buscamos Experto en Cro/constructor de embudos de ventas para E-co...',
    'Descripción de la Empresa\nSomos una tienda de comercio electrónico en rápido crecimiento. Vendemos diversas soluciones para los dolores musculares y articulares, en mercados como México, Chile y Colombia, a través de plataformas de tráfico pago como Meta Ads, Google Ads, Whatsapp, Tiktok, Instagram, etc. Trabajamos en Shopify, Funnelish y Gemp ... Ver más detalles',
    'https://www.workana.com/job/buscamos-experto-en-cro-constructor-de-embudos-de-ventas-trabajo-remoto-y-horarios-flexibles?ref=projects_1'
  ),
  (
    3,
    '2024-07-06 11:52:34',
    'Bot en solana.',
    'Requiero un bot especializado en la red de Solana, diseñado para ejecutar transacciones a alta frecuencia y con un rendimiento excepcional. El bot deberá ser capaz de operar bajo parámetros específicos y personalizables\n\nCategoría: Programación y Tecnología\nSubcategoría: Otros\nTamaño del ... Ver más detalles',
    'https://www.workana.com/job/bot-en-solana?ref=projects_1'
  ),
  -- --------------------------------------------------------
  --
  -- Estructura de tabla para la tabla `user_skills`
  --
CREATE TABLE `user_skills` (
  `id` int(10) UNSIGNED NOT NULL,
  `user_id` varchar(128) NOT NULL,
  `skill_slug` varchar(128) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `user_skills`
--
INSERT INTO
  `user_skills` (
    `id`,
    `user_id`,
    `skill_slug`,
    `created_at`,
    `updated_at`
  )
VALUES
  (
    29,
    '123456789',
    'adobe-photoshop',
    '2025-08-14 15:59:23',
    '2025-08-14 15:59:23'
  ),
  (
    30,
    '123456789',
    'microsoft-word',
    '2025-08-14 15:59:23',
    '2025-08-14 15:59:23'
  ),
  (
    31,
    '123456789',
    'outlook',
    '2025-08-14 15:59:23',
    '2025-08-14 15:59:23'
  ),
  (
    41,
    '1341946489',
    'php',
    '2025-11-27 15:12:01',
    '2025-11-27 15:12:01'
  ),
  (
    42,
    '1341946489',
    'python',
    '2025-11-27 15:12:19',
    '2025-11-27 15:12:19'
  ),
  (
    43,
    '1341946489',
    'excel',
    '2025-11-27 15:12:29',
    '2025-11-27 15:12:29'
  ),
  (
    44,
    '1341946489',
    'access',
    '2025-11-27 15:12:36',
    '2025-11-27 15:12:36'
  );

-- --------------------------------------------------------
--
-- Estructura de tabla para la tabla `usuarios_bot`
--
CREATE TABLE `usuarios_bot` (
  `id` int(11) NOT NULL,
  `telegram_user_id` bigint(20) NOT NULL,
  `nombre_usuario` varchar(255) DEFAULT NULL,
  `activo` tinyint (1) DEFAULT 1,
  `creado_en` datetime DEFAULT current_timestamp()
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `usuarios_bot`
--
INSERT INTO
  `usuarios_bot` (
    `id`,
    `telegram_user_id`,
    `nombre_usuario`,
    `activo`,
    `creado_en`
  )
VALUES
  (14, 1, 'test_user', 1, '2025-08-18 10:51:54');

--
-- Índices para tablas volcadas
--
--
-- Indices de la tabla `proyectos`
--
ALTER TABLE `proyectos` ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `user_skills`
--
ALTER TABLE `user_skills` ADD PRIMARY KEY (`id`),
ADD UNIQUE KEY `uniq_user_skill` (`user_id`, `skill_slug`),
ADD KEY `idx_user` (`user_id`);

--
-- Indices de la tabla `usuarios_bot`
--
ALTER TABLE `usuarios_bot` ADD PRIMARY KEY (`id`),
ADD UNIQUE KEY `telegram_user_id` (`telegram_user_id`);

--
-- AUTO_INCREMENT de las tablas volcadas
--
--
-- AUTO_INCREMENT de la tabla `proyectos`
--
ALTER TABLE `proyectos` MODIFY `id` int(11) NOT NULL AUTO_INCREMENT,
AUTO_INCREMENT = 738;

--
-- AUTO_INCREMENT de la tabla `user_skills`
--
ALTER TABLE `user_skills` MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT,
AUTO_INCREMENT = 45;

--
-- AUTO_INCREMENT de la tabla `usuarios_bot`
--
ALTER TABLE `usuarios_bot` MODIFY `id` int(11) NOT NULL AUTO_INCREMENT,
AUTO_INCREMENT = 17;

COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;

/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;

/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
