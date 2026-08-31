import re
from pathlib import Path
from typing import Dict, Any, List

try:
    from backend.src.config import DATA_DIR, ACADEMY_NAME, HUMAN_SUPPORT_EMAIL, HUMAN_SUPPORT_PHONE, HUMAN_SUPPORT_HOURS
except ImportError:
    from src.config import DATA_DIR, ACADEMY_NAME, HUMAN_SUPPORT_EMAIL, HUMAN_SUPPORT_PHONE, HUMAN_SUPPORT_HOURS


def extract_catalog_from_documents() -> Dict[str, Any]:
    """
    Dynamically scan and parse whatever markdown files exist in data/.
    Extracts programs, schedules, campuses, and quick query chips.
    """
    programs: List[Dict[str, Any]] = []
    schedules: List[Dict[str, Any]] = []
    campuses: List[Dict[str, Any]] = []
    quick_chips: List[Dict[str, str]] = []

    if not DATA_DIR.exists():
        return _fallback_catalog()

    md_files = sorted(DATA_DIR.glob("*.md"))
    if not md_files:
        return _fallback_catalog()

    for file_path in md_files:
        try:
            content = file_path.read_text(encoding="utf-8")
            fname = file_path.name.lower()

            # Find all ### X.Y Sections
            sections = re.findall(
                r"^###\s+(\d+\.\d+)\s+([^\n]+)\n(.*?)(?=\n###|\n##|\n---|\Z)",
                content,
                re.MULTILINE | re.DOTALL
            )

            # --- 1. PROGRAMS PARSER (programs_and_levels.md - Section 1) ---
            if "program" in fname or "curso" in fname or "carrera" in fname:
                for num, header, body in sections:
                    if not num.startswith("1."):
                        continue  # Skip CEFR levels in section 2
                    
                    header = header.strip()
                    body = body.strip()

                    overview_match = re.search(r"-\s*(?:Overview|Descripción|Resumen):\s*([^\n]+)", body, re.IGNORECASE)
                    overview = overview_match.group(1).strip() if overview_match else body.splitlines()[0].lstrip("- *").strip()

                    highlights = []
                    for line in body.splitlines():
                        clean_line = line.strip().lstrip("- *").strip()
                        if clean_line and not clean_line.lower().startswith("overview:") and len(highlights) < 3:
                            highlights.append(clean_line)

                    programs.append({
                        "title": header,
                        "badge": "Programa Oficial",
                        "overview": overview or "Programa de formación estructurado con certificación.",
                        "highlights": highlights or ["Metodología comunicativa", "Acompañamiento docente", "Evaluación continua"],
                        "query": f"Cuéntame todos los detalles sobre el programa de {header}, requisitos y precios",
                    })

            # --- 2. SCHEDULES & CAMPUSES PARSER (schedules_and_certifications.md) ---
            if "schedule" in fname or "horario" in fname or "jornada" in fname:
                for num, header, body in sections:
                    header = header.strip()
                    body = body.strip()

                    # 2.1 Study Schedules (Section 1)
                    if num.startswith("1."):
                        details = []
                        for line in body.splitlines():
                            clean_line = line.strip().lstrip("- *").strip()
                            if clean_line and len(details) < 2:
                                details.append(clean_line)

                        schedules.append({
                            "title": header,
                            "subtitle": "Jornada Oficial",
                            "details": details or ["Horario disponible."],
                            "query": f"¿Qué disponibilidad y cupos tienen para {header}?",
                        })

                    # 2.2 Modalities & Campuses (Section 2)
                    elif num.startswith("2."):
                        locs = []
                        for line in body.splitlines():
                            clean = line.strip().lstrip("- *").strip()
                            if clean:
                                locs.append(clean)

                        campuses.append({
                            "name": header,
                            "locations": locs[:3] or ["Sede con aulas modernas y laboratorios."],
                            "hours": HUMAN_SUPPORT_HOURS,
                        })

        except Exception as e:
            continue

    # Fallback if no specific tags matched: parse any Markdown headers
    if not programs:
        for file_path in md_files:
            try:
                content = file_path.read_text(encoding="utf-8")
                matches = re.finditer(r"^##\s+([^\n]+)\n(.*?)(?=\n##|\Z)", content, re.MULTILINE | re.DOTALL)
                for m in matches:
                    header = m.group(1).strip()
                    body = m.group(2).strip()
                    programs.append({
                        "title": header,
                        "badge": "Módulo / Documento",
                        "overview": body.splitlines()[0].lstrip("- *# ").strip() if body.splitlines() else "Contenido oficial.",
                        "highlights": [l.lstrip("- *").strip() for l in body.splitlines()[1:4] if l.strip()],
                        "query": f"Explícame todo lo relativo a {header}",
                    })
            except Exception:
                pass

    # Generate Dynamic Quick Query Chips
    if programs:
        for p in programs[:3]:
            short_name = p['title'].split('(')[0].strip()
            quick_chips.append({
                "label": f"Consultar {short_name}",
                "query": f"¿Qué detalles, precios y duración tiene {p['title']}?",
                "icon": "book-marked"
            })
    
    quick_chips.append({
        "label": "Precios oficiales en COP",
        "query": "¿Cuáles son los precios oficiales en pesos colombianos y opciones de pago en cuotas?",
        "icon": "circle-dollar-sign"
    })
    quick_chips.append({
        "label": "Descuentos con Cajas",
        "query": "¿Qué convenios tienen con Cajas de Compensación como Compensar, Colsubsidio o Comfama?",
        "icon": "tag"
    })
    quick_chips.append({
        "label": "Horarios y sedes",
        "query": "¿Cuáles son los horarios de clases y sedes disponibles en Bogotá y Medellín?",
        "icon": "clock"
    })

    return {
        "institution_name": ACADEMY_NAME,
        "contact_email": HUMAN_SUPPORT_EMAIL,
        "contact_phone": HUMAN_SUPPORT_PHONE,
        "contact_hours": HUMAN_SUPPORT_HOURS,
        "total_documents": len(md_files),
        "programs": programs,
        "schedules": schedules,
        "campuses": campuses,
        "quick_chips": quick_chips,
    }


def _fallback_catalog() -> Dict[str, Any]:
    return {
        "institution_name": "Language Academy",
        "contact_email": "admisiones@languageacademy.edu.co",
        "contact_phone": "+57 (300) 123-4567",
        "contact_hours": "Monday - Friday, 8:00 AM - 6:00 PM; Saturday, 8:00 AM - 1:00 PM (COT / UTC-5)",
        "total_documents": 0,
        "programs": [],
        "schedules": [],
        "campuses": [],
        "quick_chips": [],
    }
