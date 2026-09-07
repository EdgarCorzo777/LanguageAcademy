import os
import sqlite3
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

DB_DIR = Path(__file__).resolve().parent.parent.parent / "database"
DB_PATH = DB_DIR / "academy.db"
SCHEMA_PATH = DB_DIR / "schema.sql"


def get_db_connection() -> sqlite3.Connection:
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    try:
        if not SCHEMA_PATH.exists():
            logger.warning(f"Schema file not found at {SCHEMA_PATH}")
            return
        conn = get_db_connection()
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            schema_script = f.read()
        conn.executescript(schema_script)
        conn.commit()
        conn.close()
        logger.info(f"Relational SQLite database initialized at {DB_PATH}")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")


def record_lead(nombre: str, email: str, telefono: Optional[str] = None, tipo_doc: str = "CC", num_doc: Optional[str] = None) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM estudiantes_leads WHERE email = ?", (email,))
    row = cursor.fetchone()
    if row:
        lead_id = row["id"]
    else:
        cursor.execute(
            "INSERT INTO estudiantes_leads (tipo_documento, numero_documento, nombre_completo, email, telefono) VALUES (?, ?, ?, ?, ?)",
            (tipo_doc, num_doc, nombre, email, telefono)
        )
        conn.commit()
        lead_id = cursor.lastrowid
    conn.close()
    return lead_id


def record_placement_booking(
    student_name: str,
    email: str,
    language: str,
    modality: str = "Online",
    preferred_date: Optional[str] = None,
    phone: Optional[str] = None
) -> Dict[str, Any]:
    init_database()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Resolve sede_id based on modality
    sede_id = 5  # Online
    mod_lower = modality.lower()
    if "chapinero" in mod_lower or "bogota" in mod_lower:
        sede_id = 1
    elif "calle 100" in mod_lower or "chico" in mod_lower:
        sede_id = 2
    elif "poblado" in mod_lower:
        sede_id = 3
    elif "medellin" in mod_lower or "laureles" in mod_lower:
        sede_id = 4
        
    lead_id = record_lead(student_name, email, phone)
    cursor.execute("UPDATE estudiantes_leads SET sede_preferida_id = ? WHERE id = ?", (sede_id, lead_id))
    
    confirmation_id = f"TEST-{datetime.now().strftime('%Y%m')}-{uuid.uuid4().hex[:6].upper()}"
    
    # Find matching program_id if possible
    cursor.execute("SELECT id FROM programas WHERE LOWER(idioma) LIKE ? LIMIT 1", (f"%{language.lower()}%",))
    p_row = cursor.fetchone()
    program_id = p_row["id"] if p_row else None
    
    cursor.execute(
        "INSERT INTO agendamientos_test (codigo_confirmacion, estudiante_id, programa_id, sede_id, idioma, modalidad, fecha_preferida, estado) VALUES (?, ?, ?, ?, ?, ?, ?, 'Programado')",
        (confirmation_id, lead_id, program_id, sede_id, language, modality, preferred_date)
    )
    conn.commit()
    conn.close()
    return {
        "confirmation_id": confirmation_id,
        "student_name": student_name,
        "email": email,
        "language": language,
        "modality": modality,
        "preferred_date": preferred_date,
        "status": "Programado"
    }


def record_quote(
    program_type: str,
    payment_plan: str,
    discount_code: str,
    quote_data: Dict[str, Any],
    email: Optional[str] = None
) -> str:
    init_database()
    num_cot = f"COT-{datetime.now().strftime('%Y%m')}-{uuid.uuid4().hex[:6].upper()}"
    conn = get_db_connection()
    cursor = conn.cursor()
    
    lead_id = None
    if email:
        lead_id = record_lead("Aspirante Web", email)
        
    cursor.execute("SELECT id FROM programas WHERE LOWER(codigo) LIKE ? OR LOWER(idioma) LIKE ? LIMIT 1", (f"%{program_type}%", f"%{program_type}%"))
    prog_row = cursor.fetchone()
    prog_id = prog_row["id"] if prog_row else 1
    
    cursor.execute(
        """INSERT INTO cotizaciones (
            numero_cotizacion, estudiante_id, programa_id, plan_pago,
            codigo_descuento, nombre_descuento, porcentaje_descuento,
            valor_base_cop, descuento_cop, valor_final_cop, info_cuotas
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            num_cot, lead_id, prog_id, payment_plan,
            discount_code, quote_data.get("discount_applied", "Sin descuento"),
            quote_data.get("discount_percentage", 0),
            quote_data.get("base_price_cop", 0),
            quote_data.get("discount_amount_cop", 0),
            quote_data.get("final_price_cop", 0),
            quote_data.get("installments_info", "Contado")
        )
    )
    conn.commit()
    conn.close()
    return num_cot


if __name__ == "__main__":
    init_database()
