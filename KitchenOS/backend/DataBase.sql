CREATE DATABASE IF NOT EXISTS iot_cocina;
USE iot_cocina;

-- 1. Usuarios con Roles
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    rol ENUM('chef', 'cocinero') NOT NULL
);

-- 2. Configuración de Básculas (Qué producto hay en cada una)
CREATE TABLE IF NOT EXISTS configuracion_inventario (
    id_bascula VARCHAR(10) PRIMARY KEY, -- peso_b1, peso_b2...
    nombre_producto VARCHAR(50),
    stock_minimo FLOAT
);

-- 3. Historial de Sensores (6 básculas reales)
CREATE TABLE IF NOT EXISTS historial_sensores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    temp_camara FLOAT,
    peso_b1 FLOAT, peso_b2 FLOAT, peso_b3 FLOAT,
    peso_b4 FLOAT, peso_b5 FLOAT, peso_b6 FLOAT
);

-- 4. Recetas del Chef
CREATE TABLE IF NOT EXISTS recetas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100),
    descripcion TEXT,
    ingredientes_json JSON -- Formato: {"Tomates": 2.0, "Cebollas": 0.5}
);

-- Datos iniciales de ejemplo
INSERT INTO usuarios (username, password_hash, rol) VALUES 
('demian_chef', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6L6s57OTWzKuH6u.', 'chef'); -- Pass: tesi123

INSERT INTO configuracion_inventario (id_bascula, nombre_producto, stock_minimo) VALUES
('peso_b1', 'Tomates', 1.0), ('peso_b2', 'Cebollas', 0.5), ('peso_b3', 'Papas', 2.0),
('peso_b4', 'Carne', 1.5), ('peso_b5', 'Leche', 1.0), ('peso_b6', 'Huevos', 0.8);