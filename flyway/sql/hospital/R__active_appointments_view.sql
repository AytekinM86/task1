-- Repeatable migration (R__): has no version number. Flyway re-runs it whenever
-- its checksum changes (i.e. whenever you edit this file), AFTER all versioned
-- migrations. Perfect for views, functions, and other replaceable objects.

CREATE OR REPLACE VIEW active_appointments AS
SELECT a.appointment_id,
       a.scheduled_at,
       a.status,
       a.reason,
       p.first_name || ' ' || p.last_name AS patient_name,
       d.first_name || ' ' || d.last_name AS doctor_name,
       dep.name                           AS department
FROM appointments a
JOIN patients   p   ON p.patient_id   = a.patient_id
JOIN doctors    d   ON d.doctor_id    = a.doctor_id
JOIN departments dep ON dep.department_id = d.department_id
WHERE a.status = 'scheduled'
ORDER BY a.scheduled_at;
