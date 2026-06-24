-- V2: incremental change — add prescriptions to the model.
-- medications is a lookup; prescription_items is the junction resolving the
-- many-to-many between prescriptions and medications (3NF).

CREATE TABLE medications (
    medication_id SERIAL PRIMARY KEY,
    name          VARCHAR(120) NOT NULL UNIQUE,
    form          VARCHAR(40),          -- tablet, syrup, injection, ...
    strength      VARCHAR(40)           -- 500mg, 5ml, ...
);

CREATE TABLE prescriptions (
    prescription_id SERIAL PRIMARY KEY,
    appointment_id  INT NOT NULL REFERENCES appointments(appointment_id),
    issued_at       TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE prescription_items (
    prescription_id INT NOT NULL REFERENCES prescriptions(prescription_id),
    medication_id   INT NOT NULL REFERENCES medications(medication_id),
    dosage          VARCHAR(80) NOT NULL,   -- "1 tablet twice a day"
    PRIMARY KEY (prescription_id, medication_id)
);
