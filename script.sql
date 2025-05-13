#CREATE DATABASE grafo_guatemala;
CREATE TABLE grafo_municipios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    origen VARCHAR(255) NOT NULL,
    destino VARCHAR(255) NOT NULL,
    distancia INT NOT NULL
);
