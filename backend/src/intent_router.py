import re
import unicodedata
from typing import Optional, Dict, Any


def _normalize_string(text: str) -> str:
    """Normalize text removing accents, punctuation and excess whitespace."""
    text = text.lower().strip()
    # Remove accents/diacritics
    nfkd = unicodedata.normalize("NFKD", text)
    text = "".join([c for c in nfkd if not unicodedata.combining(c)])
    # Remove punctuation
    text = re.sub(r"[^\w\s]", " ", text)
    # Collapse whitespace
    return re.sub(r"\s+", " ", text).strip()


class IntentRouter:
    """
    Ultra-fast, zero-latency local intent router.
    Detects greetings, disinterest/rejection, gratitude, farewells, inappropriate inputs,
    and explicit human requests in < 1 ms without consuming LLM API tokens.
    """

    # Rejection, disinterest, refusal of advice (Must be precise to avoid matching prepositions like 'para')
    DISINTEREST_PATTERNS = [
        r"^(no\s*quiero\s*(que\s*me\s*asesores|ayuda|asesoria|nada|hablar|saber|informacion|cursos?|estudiar)?(\s*gracias)?)$",
        r"^(no\s*me\s*(interesa|asesores|ayudes|sirve|importa|gusta)(\s*(nada|mas|gracias|por\s*ahora))?)$",
        r"^(no\s*necesito\s*(ayuda|asesor|nada|informacion)(\s*gracias)?)$",
        r"^(no\s*deseo\s*(nada|ayuda|asesoria|informacion)(\s*gracias)?)$",
        r"^(dejame\s*en\s*paz|dejame\s*tranquilo|no\s*molestes|vete|callate|basta|detente|para\s*ya|cancelar|no\s*gracias)$",
        r"^(i\s*don'?t\s*want\s*(help|advice|anything)|not\s*interested|leave\s*me\s*alone|no\s*thanks)$",
        r"\b(no\s*quiero\s*que\s*me\s*asesores|no\s*me\s*interesa|no\s*quiero\s*ninguna\s*ayuda|dejame\s*en\s*paz)\b",
    ]

    GREETING_PATTERNS = [
        r"^(o+la|h+o+la|h+o+l+a+s|h+e+y|h+e+l+l+o|h+i)$",
        r"^(o+la|h+o+la|h+o+l+a+s)?\s*(buenos?\s*dias?|buenas?\s*tardes?|buenas?\s*noches?|buenas?)$",
        r"^(o+la|h+o+la|h+o+l+a+s)?\s*(que\s*tal|como\s*estas?|como\s*te\s*va|saludos?)$",
        r"^(good\s*morning|good\s*afternoon|good\s*evening)$",
    ]


    FAREWELL_PATTERNS = [
        r"^(chao|adios|hasta\s*luego|hasta\s*pronto|nos\s*vemos|bye|bye\s*bye|chao\s*chao)$",
        r"^(que\s*tengas?\s*buen\s*dia|feliz\s*tarde|feliz\s*noche)$",
    ]

    GRATITUDE_PATTERNS = [
        r"^(gracias|muchas\s*gracias|mil\s*gracias|grax|ty|thank\s*you|thanks)$",
        r"^(perfecto\s*gracias|excelente\s*gracias|muy\s*amable|entendido\s*gracias)$",
        r"^(ok|vale|listo|entendido|perfecto|de\s*acuerdo|okey|okay)$",
    ]

    # Inappropriate, profanity, vulgarity, sexual content or trolling
    INAPPROPRIATE_PATTERNS = [
        r"\b(pene|vagina|sexo|porno|porn|puta|puto|mierda|hijueputa|gonorrea|malparido|chimba|marica|verga|culo|tetas|estupido|idiota|tonto|imbecil|fuck|shit|bitch|dick|pussy|ass)\b",
    ]

    # Off-topic / Jokes / Generic non-academic queries
    OFFTOPIC_PATTERNS = [
        r"^(cuentame\s*un\s*chiste|dime\s*un\s*chiste|un\s*chiste|hazme\s*una\s*receta|como\s*hacer\s*una\s*pizza|haz\s*mi\s*tarea|quien\s*es\s*el\s*presidente)$",
    ]

    EXPLICIT_HUMAN_PATTERNS = [
        r"(quiero|necesito|deseo|solicito)\s*(hablar|comunicarme|contactar)\s*(con|a)\s*(un|una)?\s*(asesor|humano|persona|agente|operador)",
        r"(pasame|comunicame|transfiereme|conectame)\s*(con|a)\s*(un|una)?\s*(asesor|humano|persona|agente|soporte)",
        r"^(hablar\s*con\s*un\s*asesor|asesor\s*humano|atencion\s*humana|agente\s*humano|atencion\s*al\s*cliente)$",
        r"(i\s*want|i\s*need)\s*to\s*(talk|speak)\s*to\s*(a\s*)?(human|agent|representative|advisor)",
    ]

    @classmethod
    def classify(cls, query: str) -> Optional[Dict[str, Any]]:
        """
        Classify query. If it matches a deterministic intent, returns a structured response.
        Otherwise returns None to proceed with standard RAG pipeline.
        """
        norm = _normalize_string(query)
        if not norm:
            return {
                "intent": "empty",
                "answer": "¡Hola! Por favor escribe tu consulta sobre nuestros programas de idiomas, precios en COP, horarios o dudas de matrícula en Language Academy.",
                "escalated": False,
                "sources": [],
                "cached": True,
                "latency_ms": 0.5,
            }

        # 1. Check Disinterest / Negative / Rejection (DO NOT ESCALATE TO SUPPORT!)
        for pattern in cls.DISINTEREST_PATTERNS:
            if re.search(pattern, norm):
                return {
                    "intent": "disinterest_rejection",
                    "answer": (
                        "Entendido, no hay ningún problema. Si en algún momento necesitas información sobre los programas de idiomas, "
                        "horarios o tarifas de **Language Academy**, aquí estaré a tu disposición. ¡Que tengas un excelente día!"
                    ),
                    "escalated": False,
                    "sources": ["asistente_respetuoso"],
                    "cached": True,
                    "latency_ms": 0.6,
                }

        # 2. Inappropriate / Profanity / Vulgarity / Trolling (No human escalation!)
        for pattern in cls.INAPPROPRIATE_PATTERNS:
            if re.search(pattern, norm):
                return {
                    "intent": "inappropriate",
                    "answer": (
                        "No puedo ayudarte con ese tipo de solicitudes. Como asistente virtual de **Language Academy**, "
                        "mi función es orientarte exclusivamente sobre nuestros programas de idiomas (Inglés, Francés, Alemán, Italiano y Portugués), "
                        "tarifas oficiales en COP, horarios y procesos de matrícula.\n\n"
                        "¿Tienes alguna pregunta sobre nuestros cursos o sedes?"
                    ),
                    "escalated": False,
                    "sources": ["politica_de_uso"],
                    "cached": True,
                    "latency_ms": 0.7,
                }

        # 3. Check Explicit Human Advisor Request (Legitimate Escalation)
        for pattern in cls.EXPLICIT_HUMAN_PATTERNS:
            if re.search(pattern, norm):
                return {
                    "intent": "explicit_human_request",
                    "answer": (
                        "¡Con mucho gusto! Te pongo en contacto directo con nuestro equipo de admisiones de **Language Academy**:\n\n"
                        "👩‍💼 **Canales Oficiales de Atención:**\n"
                        "- 📱 **WhatsApp / Teléfono:** [+57 (300) 123-4567](https://wa.me/573001234567)\n"
                        "- 📧 **Correo de Admisiones:** `admisiones@languageacademy.edu.co`\n"
                        "- ☎️ **PBX Bogotá:** +57 (601) 745-8900\n"
                        "- ⏰ **Horario de Atención:** Lunes a Viernes de 8:00 AM a 6:00 PM | Sábados de 8:00 AM a 1:00 PM (Hora Colombia)\n\n"
                        "Uno de nuestros asesores te responderá a la mayor brevedad."
                    ),
                    "escalated": True,
                    "sources": ["atencion_humana_directa"],
                    "cached": True,
                    "latency_ms": 0.8,
                }

        # 4. Check Greetings (Tolerant to "ola", "holas", "buenos dias", etc.)
        for pattern in cls.GREETING_PATTERNS:
            if re.match(pattern, norm):
                return {
                    "intent": "greeting",
                    "answer": (
                        "¡Hola! Te doy una cordial bienvenida a **Language Academy**. Estoy aquí para ayudarte a resolver todas tus dudas sobre:\n\n"
                        "- 🇬🇧 **Cursos de Idiomas:** Inglés General, Intensivo, Negocios, Francés, Alemán, Italiano y Portugués.\n"
                        "- 💰 **Tarifas en COP y Financiación:** Precios oficiales, cuotas mensuales y convenios con Cajas de Compensación (Compensar, Colsubsidio, Comfama hasta 20% de descuento).\n"
                        "- ⏰ **Horarios y Sedes:** Clases entre semana, sábados intensivos, sedes en Bogotá y Medellín o 100% online.\n"
                        "- 🛠️ **Soporte de Admisiones:** Métodos de pago PSE, acceso a clases virtuales o requisitos de matrícula.\n\n"
                        "¿En qué te puedo orientar hoy?"
                    ),
                    "escalated": False,
                    "sources": ["asistente_bienvenida"],
                    "cached": True,
                    "latency_ms": 1.0,
                }

        # 5. Check Off-topic / Jokes (No escalation!)
        for pattern in cls.OFFTOPIC_PATTERNS:
            if re.match(pattern, norm):
                return {
                    "intent": "offtopic",
                    "answer": (
                        "Como asistente virtual de **Language Academy**, mi especialidad es brindarte información sobre cursos de idiomas, precios, horarios y trámites de matrícula. ¿Te gustaría conocer nuestros programas de inglés, francés, alemán, italiano o portugués?"
                    ),
                    "escalated": False,
                    "sources": ["asistente_academico"],
                    "cached": True,
                    "latency_ms": 0.6,
                }

        # 6. Check Farewells
        for pattern in cls.FAREWELL_PATTERNS:
            if re.match(pattern, norm):
                return {
                    "intent": "farewell",
                    "answer": (
                        "¡Ha sido un placer orientarte! Si necesitas más información sobre nuestros programas o tu proceso de matrícula en **Language Academy**, aquí estaré para ayudarte. ¡Que tengas un excelente día!"
                    ),
                    "escalated": False,
                    "sources": ["asistente_despedida"],
                    "cached": True,
                    "latency_ms": 0.6,
                }

        # 7. Check Gratitude & Acknowledgment
        for pattern in cls.GRATITUDE_PATTERNS:
            if re.match(pattern, norm):
                return {
                    "intent": "gratitude",
                    "answer": (
                        "¡Con todo gusto! ¿Hay algo más en lo que pueda ayudarte respecto a programas, horarios, cotizaciones en COP o dudas de matrícula en Language Academy?"
                    ),
                    "escalated": False,
                    "sources": ["asistente_cortesia"],
                    "cached": True,
                    "latency_ms": 0.5,
                }

        return None
