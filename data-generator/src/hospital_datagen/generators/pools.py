"""Curated domain value pools used by the generators."""

from __future__ import annotations

DEPARTMENT_NAMES: tuple[str, ...] = (
    "Cardiology",
    "Pediatrics",
    "Orthopedics",
    "Neurology",
    "Oncology",
    "Dermatology",
    "Radiology",
    "Emergency",
    "Gastroenterology",
    "Nephrology",
    "Urology",
    "Pulmonology",
    "Endocrinology",
    "Ophthalmology",
    "Psychiatry",
    "Obstetrics",
)

SPECIALTY_NAMES: tuple[str, ...] = (
    "Interventional Cardiology",
    "General Pediatrics",
    "Sports Medicine",
    "Clinical Neurology",
    "Medical Oncology",
    "Cosmetic Dermatology",
    "Diagnostic Radiology",
    "Emergency Medicine",
    "Hepatology",
    "Renal Care",
    "Endourology",
    "Respiratory Medicine",
    "Diabetology",
    "Retinal Surgery",
    "Child Psychiatry",
    "Maternal-Fetal Medicine",
)

MEDICATION_NAMES: tuple[str, ...] = (
    "Aspirin",
    "Amoxicillin",
    "Ibuprofen",
    "Paracetamol",
    "Metformin",
    "Atorvastatin",
    "Omeprazole",
    "Amlodipine",
    "Lisinopril",
    "Levothyroxine",
    "Azithromycin",
    "Ciprofloxacin",
    "Prednisone",
    "Salbutamol",
    "Insulin Glargine",
    "Warfarin",
    "Losartan",
    "Gabapentin",
    "Sertraline",
    "Hydrochlorothiazide",
    "Clopidogrel",
    "Furosemide",
    "Pantoprazole",
    "Tramadol",
    "Cetirizine",
    "Diazepam",
    "Naproxen",
    "Doxycycline",
    "Metronidazole",
    "Ranitidine",
)

MEDICATION_FORMS: tuple[str, ...] = ("tablet", "capsule", "syrup", "injection", "cream", "drops")

MEDICATION_STRENGTHS: tuple[str, ...] = (
    "50mg",
    "100mg",
    "250mg",
    "400mg",
    "500mg",
    "5ml",
    "10ml",
    "250mg/5ml",
    "5mg",
    "20mg",
)

APPOINTMENT_REASONS: tuple[str, ...] = (
    "Routine checkup",
    "Follow-up consultation",
    "Chest pain evaluation",
    "Annual physical exam",
    "Vaccination",
    "Blood pressure review",
    "Post-surgery follow-up",
    "Lab results review",
    "Chronic condition management",
    "Acute injury assessment",
    "Medication review",
    "Specialist referral",
)

DOSAGE_PATTERNS: tuple[str, ...] = (
    "1 tablet once a day",
    "1 tablet twice a day",
    "1 tablet every 8 hours",
    "2 tablets after meals",
    "5ml three times a day",
    "1 capsule at bedtime",
    "1 injection weekly",
    "Apply twice daily",
    "1 tablet every 12 hours",
    "1 tablet as needed for pain",
)
