-- V3: seed sample data so the tables are immediately explorable.

INSERT INTO departments (name, location) VALUES
    ('Cardiology', 'Building A, Floor 2'),
    ('Pediatrics', 'Building B, Floor 1'),
    ('Orthopedics', 'Building A, Floor 3');

INSERT INTO specialties (name) VALUES
    ('Interventional Cardiology'),
    ('General Pediatrics'),
    ('Sports Medicine');

INSERT INTO doctors (first_name, last_name, department_id, specialty_id) VALUES
    ('Alice', 'Hart',   1, 1),
    ('Bashir', 'Khan',  2, 2),
    ('Carla', 'Mendes', 3, 3);

INSERT INTO patients (first_name, last_name, dob, gender, phone, email) VALUES
    ('John',  'Doe',   '1985-04-12', 'M', '+1-555-0101', 'john.doe@example.com'),
    ('Mary',  'Smith', '1992-11-30', 'F', '+1-555-0102', 'mary.smith@example.com'),
    ('Sam',   'Lee',   '2015-06-08', 'M', '+1-555-0103', 'sam.lee@example.com');

INSERT INTO appointments (patient_id, doctor_id, scheduled_at, status, reason) VALUES
    (1, 1, '2026-07-01 09:00', 'scheduled', 'Chest pain follow-up'),
    (3, 2, '2026-07-01 10:30', 'scheduled', 'Routine child checkup'),
    (2, 3, '2026-06-20 14:00', 'completed', 'Knee injury assessment');

INSERT INTO medications (name, form, strength) VALUES
    ('Aspirin',     'tablet', '100mg'),
    ('Amoxicillin', 'syrup',  '250mg/5ml'),
    ('Ibuprofen',   'tablet', '400mg');

INSERT INTO prescriptions (appointment_id, issued_at) VALUES
    (3, '2026-06-20 14:30');

INSERT INTO prescription_items (prescription_id, medication_id, dosage) VALUES
    (1, 3, '1 tablet every 8 hours after meals');
