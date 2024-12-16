CREATE DATABASE qualify_design_db;
USE qualify_design_db;

CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE analisis (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT,
    url_analizada TEXT NOT NULL,
    screenshot_path TEXT NOT NULL,
    resultado_analisis TEXT,
    puntuacion DECIMAL(3,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

CREATE TABLE historial (
    id INT AUTO_INCREMENT PRIMARY KEY,
    analisis_id INT,
    pdf_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (analisis_id) REFERENCES analisis(id)
);
