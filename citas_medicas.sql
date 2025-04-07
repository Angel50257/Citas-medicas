create database citas_medicas

use citas_medicas

CREATE TABLE Pacientes (
    id INT PRIMARY KEY IDENTITY(1,1),
    nombre NVARCHAR(100) NOT NULL,
    edad INT,
    telefono NVARCHAR(50),
    direccion NVARCHAR(255)
);

CREATE TABLE Doctores (
    id INT PRIMARY KEY IDENTITY(1,1),
    nombre NVARCHAR(100) NOT NULL,
    especialidad NVARCHAR(100),
    telefono NVARCHAR(50)
);

CREATE TABLE Citas (
    id INT PRIMARY KEY IDENTITY(1,1),
    paciente_id INT,
    doctor_id INT,
    fecha DATETIME,
    motivo NVARCHAR(255),
    FOREIGN KEY (paciente_id) REFERENCES Pacientes(id),
    FOREIGN KEY (doctor_id) REFERENCES Doctores(id)
);

select * from Pacientes
select * from Doctores
select * from Citas