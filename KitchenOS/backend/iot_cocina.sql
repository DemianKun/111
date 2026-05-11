-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 11-05-2026 a las 13:52:21
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `iot_cocina`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tareas`
--

CREATE TABLE `tareas` (
  `id` int(11) NOT NULL,
  `receta_nombre` varchar(100) NOT NULL,
  `empleado_id` int(11) DEFAULT NULL,
  `estado` varchar(20) DEFAULT 'PROPUESTA',
  `fecha_asignacion` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `tareas`
--

INSERT INTO `tareas` (`id`, `receta_nombre`, `empleado_id`, `estado`, `fecha_asignacion`) VALUES
(1, 'Hamburguesa K-OS', 2, 'COMPLETADA', '2026-03-01 14:00:00'),
(2, 'Papas Fritas Giga', 3, 'COMPLETADA', '2026-03-01 14:15:00'),
(3, 'Pechuga Especial', 4, 'COMPLETADA', '2026-03-01 15:00:00'),
(4, 'Ensalada de la Casa', 2, 'COMPLETADA', '2026-03-02 13:00:00'),
(5, 'Hamburguesa K-OS', 3, 'COMPLETADA', '2026-03-05 19:00:00'),
(6, 'Papas Fritas Giga', 4, 'COMPLETADA', '2026-03-05 20:00:00'),
(7, 'Pechuga Especial', 2, 'COMPLETADA', '2026-03-08 15:00:00'),
(8, 'Hamburguesa K-OS', 3, 'COMPLETADA', '2026-03-12 18:30:00'),
(9, 'Ensalada de la Casa', 4, 'COMPLETADA', '2026-03-15 21:00:00'),
(10, 'Pechuga Especial', 2, 'COMPLETADA', '2026-03-18 12:00:00'),
(11, 'Hamburguesa K-OS', 3, 'COMPLETADA', '2026-04-01 14:00:00'),
(12, 'Papas Fritas Giga', 4, 'COMPLETADA', '2026-04-03 16:00:00'),
(13, 'Ensalada de la Casa', 2, 'COMPLETADA', '2026-04-06 20:30:00'),
(14, 'Hamburguesa K-OS', 3, 'COMPLETADA', '2026-04-10 12:00:00'),
(15, 'Pechuga Especial', 4, 'COMPLETADA', '2026-04-15 17:00:00'),
(16, 'Papas Fritas Giga', 2, 'COMPLETADA', '2026-04-18 13:00:00'),
(17, 'Hamburguesa K-OS', 3, 'COMPLETADA', '2026-05-01 14:30:00'),
(18, 'Pechuga Especial', 4, 'COMPLETADA', '2026-05-05 19:00:00'),
(19, 'Ensalada de la Casa', 2, 'COMPLETADA', '2026-05-08 15:00:00'),
(20, 'Hamburguesa K-OS', 2, 'EN_PROCESO', '2026-05-11 12:30:00'),
(21, 'Papas Fritas Giga', 3, 'PENDIENTE', '2026-05-11 12:40:00');

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `tareas`
--
ALTER TABLE `tareas`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `tareas`
--
ALTER TABLE `tareas`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=26;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
