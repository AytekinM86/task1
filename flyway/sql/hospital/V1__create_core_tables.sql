-- V1: core hospital tables (3NF).
-- Lookup tables first, then entities that reference them.

CREATE TABLE departments (
    department_id SERIAL PRIMARY KEY,
    name          VARCHAR(100) NOT NULL UNIQUE,
    location      VARCHAR(100)
);

CREATE TABLE specialties (
    specialty_id SERIAL PRIMARY KEY,
    name         VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE doctors (
    doctor_id     SERIAL PRIMARY KEY,
    first_name    VARCHAR(50) NOT NULL,
    last_name     VARCHAR(50) NOT NULL,
    department_id INT NOT NULL REFERENCES departments(department_id),
    specialty_id  INT NOT NULL REFERENCES specialties(specialty_id)
);

CREATE TABLE patients (
    patient_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name  VARCHAR(50) NOT NULL,
    dob        DATE NOT NULL,
    gender     CHAR(1) CHECK (gender IN ('M', 'F', 'O')),
    phone      VARCHAR(20),
    email      VARCHAR(120) UNIQUE
);

CREATE TABLE appointments (
    appointment_id SERIAL PRIMARY KEY,
    patient_id     INT NOT NULL REFERENCES patients(patient_id),
    doctor_id      INT NOT NULL REFERENCES doctors(doctor_id),
    scheduled_at   TIMESTAMP NOT NULL,
    status         VARCHAR(20) NOT NULL DEFAULT 'scheduled'
                   CHECK (status IN ('scheduled', 'completed', 'cancelled', 'no_show')),
    reason         VARCHAR(255)
);

CREATE INDEX idx_doctors_department ON doctors(department_id);
CREATE INDEX idx_appointments_patient ON appointments(patient_id);
CREATE INDEX idx_appointments_doctor ON appointments(doctor_id);
