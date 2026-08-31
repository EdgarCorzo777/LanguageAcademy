import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"

PROGRAMS_AND_LEVELS_CONTENT = """# Academic Programs, Levels and Academic FAQ - Language Academy

## 1. Available Language Programs

### 1.1 General and Intensive English (Ingles General e Intensivo)
- Overview: Comprehensive English program based on the Common European Framework of Reference (CEFR). Covers speaking, listening, reading, writing, and cultural immersion.
- Available Tracks:
  - Standard Track: 16 weeks per level (6 hours per week).
  - Intensive Track: 8 weeks per level (12 hours per week).
  - Immersion Bootcamp: 4 weeks per level (25 hours per week).
- Target Audience: Adults, university students, and teenagers (ages 14+).

### 1.2 Business English and Corporate Communication (Ingles de Negocios)
- Overview: Specialized curriculum focusing on executive presentations, contract negotiations, international business correspondence, technical reporting, and cross-cultural communication.
- Duration: 12 weeks (4 hours per week, 48 total instructional hours).
- Prerequisites: Minimum certified B1 level in English.

### 1.3 French Program (Programa de Frances)
- Overview: French as a foreign language (FLE) accredited curriculum preparing students for DELF/DALF certifications.
- Levels Offered: A1 (Discovery), A2 (Intermediate), B1 (Threshold), B2 (Vantage).
- Duration: 16 weeks per level (6 hours per week).

### 1.4 German Program (Programa de Aleman)
- Overview: German language program aligned with the Goethe-Institut standards, covering everyday communication, academic preparation (Studienkolleg), and professional terminology.
- Levels Offered: A1, A2, B1, B2.
- Duration: 18 weeks per level (6 hours per week).

### 1.5 Italian and Portuguese Programs (Italiano y Portugues)
- Overview: Communicative language courses emphasizing rapid conversational fluency, latin grammar structures, and cultural immersion (CELI and Celpe-Bras exam readiness).
- Levels Offered: A1 through B2.
- Duration: 14 weeks per level (5 hours per week).

---

## 2. Common European Framework of Reference (CEFR) Levels

### 2.1 Level A1 - Acceso / Beginner (60 hours)
- Can understand and use familiar everyday expressions and very basic phrases.
- Can introduce him/herself and others, ask and answer basic personal questions.

### 2.2 Level A2 - Plataforma / Elementary (80 hours)
- Can understand sentences and frequently used expressions related to areas of most immediate relevance (personal info, shopping, local geography, employment).
- Can communicate in simple and routine tasks requiring direct exchange of information.

### 2.3 Level B1 - Umbral / Intermediate (100 hours)
- Can understand the main points of clear standard input on familiar matters regularly encountered in work, school, leisure.
- Can deal with most situations likely to arise while travelling in an area where the language is spoken.

### 2.4 Level B2 - Avanzado / Upper Intermediate (120 hours)
- Can understand the main ideas of complex text on both concrete and abstract topics, including technical discussions in his/her field of specialization.
- Can interact with a degree of fluency and spontaneity with native speakers without strain.

### 2.5 Level C1 / C2 - Dominio Operativo Eficaz / Advanced and Mastery (140 hours)
- C1: Can express ideas fluently and spontaneously without much obvious searching for expressions. Can use language flexibly and effectively for social, academic and professional purposes.
- C2: Mastery level capable of effortless comprehension and precise expression in demanding academic and professional contexts.

---

## 3. Academic Requirements and Placement FAQ (Preguntas Frecuentes Academicas)

### 3.1 Free Diagnostic Placement Test (Examen de Nivelacion Gratuito)
- Is the level placement test mandatory?
  - If you are a complete beginner (starting at Level A1), no test is needed.
  - If you have prior language experience, you are entitled to a 100% free 30-minute diagnostic test (20 min digital assessment + 10 min conversational interview with a teacher) to place you in the exact CEFR level.

### 3.2 Age Limits and Document Requirements
- Minimum Age: 14 years old for general tracks; teenagers and adults.
- Accepted IDs: Cedula de Ciudadania (CC), Tarjeta de Identidad (TI for ages 14-17), Cedula de Extranjeria (CE), valid Passport, or PPT for foreign residents in Colombia.
- No prior academic transcripts required to enroll in proficiency levels.

### 3.3 Study Materials and Platform Inclusions
- Every enrollment includes full access to digital campus, interactive e-books, multimedia labs, recorded lessons library, and certificate of completion at no extra charge.

### 3.4 Module Retake Policy (Repeticion de Nivel)
- Students with at least 85% attendance who do not pass the level exam can retake the module with a 50% solidarity discount.
"""

ADMISSIONS_AND_PRICING_CONTENT = """# Admissions, Tuition Pricing and Payment Troubleshooting - Language Academy (Tarifas en COP)

## 1. Official Tuition Rates in Colombian Pesos (COP)

### 1.1 Standard Language Programs (English, French, German, Italian, Portuguese)
- Price per Academic Level (16 weeks / 96 instructional hours):
  - Upfront Single Payment (Pago de Contado): $1,450,000 COP per level.
  - Installment Plan (Plan Financiado en Cuotas): Total of $1,580,000 COP, divided into 4 monthly installments of $395,000 COP (0% interest rate applied).
- Included Materials: Access to digital campus, interactive e-book, multimedia conversational labs, and certificate of completion.

### 1.2 Intensive Immersion Track (Track Intensivo)
- Price per Academic Level (8 weeks / 96 intensive hours):
  - Upfront Single Payment: $1,650,000 COP per level.
  - Installment Plan: Total of $1,750,000 COP in 2 monthly installments of $875,000 COP.

### 1.3 Business English Specialization (Ingles Corporativo)
- Total Module Cost (12 weeks / 48 instructional hours):
  - Upfront Single Payment: $1,200,000 COP.
  - Installment Plan: Total of $1,290,000 COP in 3 monthly installments of $430,000 COP.

### 1.4 International Exam Preparation Modules (IELTS / TOEFL / DELF / Goethe)
- 8-Week Workshop (32 instructional hours + 3 full computer simulation mocks):
  - Cost: $850,000 COP (Does not include the official examination registration fee paid to test centers).

---

## 2. Institutional Discounts and Strategic Partnerships (Convenios y Descuentos)

### 2.1 Cajas de Compensacion Familiar (Official Colombian Benefit Plans)
- Compensar:
  - Category A Members: 20% discount on standard upfront tuition ($1,160,000 COP final price).
  - Category B Members: 15% discount on standard upfront tuition ($1,232,500 COP final price).
  - Category C Members: 5% discount ($1,377,500 COP final price).
- Colsubsidio: 20% discount for Category A and B affiliated workers.
- Comfama / Comfenalco (Antioquia region): 20% discount for Category A affiliates.

### 2.2 Early Bird Discount (Descuento por Pronto Pago)
- 15% discount on any program when registering and paying at least 15 calendar days before the official cohort start date.

### 2.3 University Student & Youth Agreement
- Active university or technical institute students with valid student ID card receive a 10% discount on all language tracks.

### 2.4 Family and Multi-Language Benefit
- 10% discount for second family member enrolled or when enrolling simultaneously in a second foreign language.

---

## 3. Payment Methods and Troubleshooting Electronic Transactions (Solucion de Problemas con Pagos)

### 3.1 Accepted Payment Channels
- Electronic: PSE (Pagos Seguros en Linea), Nequi, Daviplata, Credit and Debit Cards (Visa, Mastercard, American Express).
- Physical: Direct deposit at Bancolombia and Banco de Bogota, or cash/card at campus offices in Bogota and Medellin.

### 3.2 Resolving Declined Payments via PSE or Credit Card (Pago Rechazado por PSE)
- Common Reasons and Immediate Solutions:
  1. Daily Transfer Limit in Banking App: Most Colombian banks (Bancolombia, Davivienda, BBVA, Banco de Bogota) have default daily transfer limits of $1,000,000 COP for PSE. If your level fee is $1,450,000 COP, log into your banking app and temporarily raise your PSE daily transaction limit.
  2. Alternative Immediate Option: Choose the 4-installment plan ($395,000 COP/month) which easily falls below any bank transfer limit, or pay via Nequi / Daviplata QR transfer.
  3. Browser Pop-up Blocker: PSE opens a redirect window. Ensure pop-ups are allowed or try an incognito window.

### 3.3 Money Debited from Bank Account Without Confirmation (Debito sin Confirmacion)
- Verification Process:
  - Banking networks occasionally delay payment status notifications by 15 to 45 minutes.
  - If money was debited from your account, take a screenshot or download the transfer voucher (comprobante con numero CUS / aprobacion).
  - Send the voucher via WhatsApp to +57 (300) 123-4567 or email to admisiones@languageacademy.edu.co with your full name and ID number.
  - Admissions accounting manually activates your enrollment within 2 business hours.

### 3.4 Electronic Invoicing and Company Billing (Facturacion Electronica con RUT)
- Send your company RUT and payment confirmation to admisiones@languageacademy.edu.co.
- Invoices compliant with DIAN regulations are issued within 24 business hours.
"""

SCHEDULES_AND_CERTIFICATIONS_CONTENT = """# Class Schedules, Learning Modalities, Campuses and Certifications - Language Academy

## 1. Study Schedules and Cohort Shifts (Horarios y Jornadas)

### 1.1 Morning Shift (Jornada Manana)
- Schedule: Monday through Thursday, 7:00 AM to 8:30 AM or 9:00 AM to 11:00 AM (COT / UTC-5).
- Designed for early risers, university students, and professionals before business hours.

### 1.2 Afternoon Shift (Jornada Tarde)
- Schedule: Monday through Thursday, 2:00 PM to 4:00 PM or 4:30 PM to 6:30 PM (COT / UTC-5).

### 1.3 Evening Shift (Jornada Noche)
- Schedule: Monday through Thursday, 6:30 PM to 8:30 PM or 8:30 PM to 10:00 PM (COT / UTC-5).
- Popular choice for working professionals and career changers.

### 1.4 Saturday Intensive Shift (Sabatino Intensivo)
- Schedule: Saturdays, 8:00 AM to 1:00 PM or 1:30 PM to 6:30 PM (COT / UTC-5).
- Complete weekly lesson plan delivered in an interactive 5-hour immersion session with breaks.

### 1.5 Sunday Shift (Dominical)
- Schedule: Sundays, 8:30 AM to 1:30 PM (COT / UTC-5). Available in 100% Live Online modality.

---

## 2. Learning Modalities and Physical Campuses (Modalidades y Sedes)

### 2.1 100% Live Online Modality (Modalidad Online en Vivo)
- Real-time interactive video classes via Zoom and Google Meet with certified native and bilingual instructors.
- Small cohorts of 8 to 12 students maximum to ensure individual speaking practice.
- 24/7 access to digital learning platform and class recordings.
- Troubleshooting Missing Class Links (¿No te llegó el enlace de Zoom/Meet para la clase de hoy?):
  1. Check your Spam or Promotions folder for emails from `@languageacademy.edu.co`.
  2. Access the student portal at `https://campus.languageacademy.edu.co` with your registered email and ID number; click the permanent "Unirse a Clase en Vivo" button that activates 10 minutes before class.
  3. Cohort WhatsApp chat: Check the group description where the teacher pins the daily Zoom/Meet link.
- Credentials Activation Time: Automatic activation occurs within 30 minutes for PSE/card payments; direct bank deposit slips are activated within 2 business hours.

### 2.2 In-Person Modality (Modalidad Presencial)
- Physical campuses equipped with language laboratories, multimedia classrooms, and conversational lounges:
  - Bogota Sede Norte: Calle 100 # 19-61, Chico Norte.
  - Bogota Sede Chapinero: Carrera 7 # 54-30, Chapinero.
  - Medellin Sede Poblado: Carrera 43A # 5A-113, El Poblado.
  - Medellin Sede Laureles: Circular 73B # 39B-20, Laureles.

### 2.3 Hybrid Modality (Modalidad Hibrida)
- Combines 1 weekly in-person conversational workshop at campus with online theoretical live sessions.

---

## 3. Official Diplomas, International Certifications and Policies

### 3.1 Academy Graduation Certificate (Certificado de Aptitud Ocupacional)
- Official institutional certification of language proficiency (e.g., "Certificado de Conocimientos Academicos en Lengua Inglesa").
- Requirements: Minimum 85% attendance and passing score of 80% (4.0 / 5.0).

### 3.2 International Certification Preparation
- English: Preparation for IELTS, TOEFL iBT, Cambridge English (B2 First, C1 Advanced), and MET.
- French: DELF (A1-B2) and DALF (C1).
- German: Goethe-Zertifikat (A1-B2).
- Italian: CELI.
- Portuguese: Celpe-Bras.

### 3.3 Freezing and Refund Policies (Aplazamientos y Reembolsos)
- Freezing an Academic Module: You can freeze your active module for up to 6 months without financial penalty by notifying admisiones@languageacademy.edu.co at least 5 business days in advance.
- Full Refund (100%): When requested in writing at least 3 business days prior to cohort start date.
- Medical / Force Majeure Credit: Remaining unused hours are preserved as credit valid for 12 months.

---

## 4. Human Support and Academic Escalation Contact (Atencion Humana)
- For customized group corporate training, special credit transfers, or inquiries outside standard admissions:
  - Official Admissions Email: admisiones@languageacademy.edu.co
  - WhatsApp and Phone Support: +57 (300) 123-4567
  - Campus PBX: +57 (601) 745-8900
  - Support Hours: Monday through Friday, 8:00 AM to 6:00 PM; Saturdays, 8:00 AM to 1:00 PM (Colombia Time / UTC-5).
"""


def generate_business_documents():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    files = {
        DATA_DIR / "programs_and_levels.md": PROGRAMS_AND_LEVELS_CONTENT,
        DATA_DIR / "admissions_and_pricing.md": ADMISSIONS_AND_PRICING_CONTENT,
        DATA_DIR / "schedules_and_certifications.md": SCHEDULES_AND_CERTIFICATIONS_CONTENT,
    }

    # Clean any other old file in data/
    old_faq = DATA_DIR / "admissions_faq_and_troubleshooting.md"
    if old_faq.exists():
        old_faq.unlink()

    created_paths = []
    for path, content in files.items():
        path.write_text(content.strip(), encoding="utf-8")
        created_paths.append(str(path))

    return created_paths


if __name__ == "__main__":
    paths = generate_business_documents()
    print(f"Generated {len(paths)} comprehensive business documents in data/ directory:")
    for path in paths:
        print(f" - {path}")
