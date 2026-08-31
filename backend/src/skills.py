import uuid
from typing import Dict, Any, Optional
from datetime import datetime

PRICING_TABLE = {
    "standard": {
        "name": "Standard Language Program (English / French / German / Italian / Portuguese)",
        "upfront": 1450000,
        "installment_total": 1580000,
        "installments_count": 4,
        "installment_amount": 395000,
    },
    "intensive": {
        "name": "Intensive Language Program (96 hours in 8 weeks)",
        "upfront": 1650000,
        "installment_total": 1750000,
        "installments_count": 2,
        "installment_amount": 875000,
    },
    "business": {
        "name": "Business English Specialization (48 hours)",
        "upfront": 1200000,
        "installment_total": 1290000,
        "installments_count": 3,
        "installment_amount": 430000,
    },
    "exam_prep": {
        "name": "International Exam Prep (IELTS / TOEFL / Cambridge / DELF)",
        "upfront": 980000,
        "installment_total": 980000,
        "installments_count": 1,
        "installment_amount": 980000,
    },
}

DISCOUNT_RATES = {
    "early_bird": {"name": "Early Bird (Pronto Pago)", "pct": 0.15},
    "family": {"name": "Family & Dual Language", "pct": 0.10},
    "compensar_a": {"name": "Caja Compensar (Categoria A)", "pct": 0.20},
    "compensar_b": {"name": "Caja Compensar (Categoria B)", "pct": 0.15},
    "colsubsidio_a": {"name": "Caja Colsubsidio (Categoria A)", "pct": 0.20},
    "comfama_a": {"name": "Caja Comfama (Categoria A)", "pct": 0.20},
    "university_student": {"name": "University Student Card", "pct": 0.10},
    "none": {"name": "No Discount Applied", "pct": 0.00},
}


def calculate_tuition_quote(
    program_type: str = "standard",
    payment_plan: str = "upfront",
    discount_code: str = "none",
) -> Dict[str, Any]:
    """Calculate official tuition in COP with applicable discounts and payment plans."""
    prog_key = program_type.lower()
    if prog_key not in PRICING_TABLE:
        prog_key = "standard"

    disc_key = discount_code.lower()
    if disc_key not in DISCOUNT_RATES:
        disc_key = "none"

    program = PRICING_TABLE[prog_key]
    discount = DISCOUNT_RATES[disc_key]

    base_price = program["upfront"] if payment_plan == "upfront" else program["installment_total"]
    discount_amount = int(base_price * discount["pct"])
    final_price = base_price - discount_amount

    return {
        "program_name": program["name"],
        "payment_plan": payment_plan,
        "base_price_cop": base_price,
        "discount_applied": discount["name"],
        "discount_percentage": int(discount["pct"] * 100),
        "discount_amount_cop": discount_amount,
        "final_price_cop": final_price,
        "installments_info": (
            f"{program['installments_count']} monthly payments of ${(final_price // program['installments_count']):,} COP"
            if payment_plan != "upfront" and program["installments_count"] > 1
            else "Single upfront payment"
        ),
        "currency": "COP",
    }


def schedule_placement_test(
    student_name: str,
    language: str,
    modality: str = "online",
    preferred_date: Optional[str] = None,
    email: Optional[str] = None,
) -> Dict[str, Any]:
    """Register and schedule a diagnostic language level placement test."""
    test_id = f"TEST-{datetime.now().strftime('%Y%m')}-{uuid.uuid4().hex[:6].upper()}"
    return {
        "confirmation_id": test_id,
        "status": "scheduled",
        "student_name": student_name,
        "language": language.capitalize(),
        "modality": modality.capitalize(),
        "scheduled_date": preferred_date or "To be coordinated with admissions coordinator within 24 hours",
        "email": email or "Pending email confirmation",
        "instructions": "The placement test consists of 20 min grammar/listening + 10 min live speaking diagnostic.",
    }


def create_escalation_ticket(
    user_query: str,
    contact_email: Optional[str] = None,
    contact_phone: Optional[str] = None,
    reason: str = "out_of_scope",
) -> Dict[str, Any]:
    """Create tracked customer support ticket for human advisor follow-up."""
    ticket_id = f"TICK-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:5].upper()}"
    return {
        "ticket_id": ticket_id,
        "status": "escalated_to_admissions_team",
        "created_at": datetime.now().isoformat(),
        "reason": reason,
        "query_summary": user_query[:120],
        "contact_email": contact_email or "Not provided by user",
        "contact_phone": contact_phone or "Not provided by user",
    }
