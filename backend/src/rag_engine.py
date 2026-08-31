import time
import logging
from typing import Dict, Any, List, Optional
from langchain_community.vectorstores import Chroma

try:
    from langchain_core.prompts import (
        ChatPromptTemplate,
        SystemMessagePromptTemplate,
        HumanMessagePromptTemplate,
        AIMessagePromptTemplate,
    )
except ImportError:
    from langchain.prompts import (
        ChatPromptTemplate,
        SystemMessagePromptTemplate,
        HumanMessagePromptTemplate,
        AIMessagePromptTemplate,
    )

try:
    from backend.src.config import (
        VECTOR_DB_DIR,
        LLM_PROVIDER,
        GOOGLE_API_KEY,
        GEMINI_MODEL_NAME,
        OPENAI_API_KEY,
        OPENAI_MODEL_NAME,
        ACADEMY_NAME,
        HUMAN_SUPPORT_EMAIL,
        HUMAN_SUPPORT_PHONE,
        HUMAN_SUPPORT_HOURS,
        SIMILARITY_THRESHOLD,
    )
    from backend.src.ingestion import get_embedding_function
    from backend.src.cache import response_cache
    from backend.src.metrics import metrics_collector
    from backend.src.intent_router import IntentRouter
except ImportError:
    from src.config import (
        VECTOR_DB_DIR,
        LLM_PROVIDER,
        GOOGLE_API_KEY,
        GEMINI_MODEL_NAME,
        OPENAI_API_KEY,
        OPENAI_MODEL_NAME,
        ACADEMY_NAME,
        HUMAN_SUPPORT_EMAIL,
        HUMAN_SUPPORT_PHONE,
        HUMAN_SUPPORT_HOURS,
        SIMILARITY_THRESHOLD,
    )
    from src.ingestion import get_embedding_function
    from src.cache import response_cache
    from src.metrics import metrics_collector
    from src.intent_router import IntentRouter


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

SYSTEM_PROMPT_TEMPLATE = """You are the official "Language Academy Admissions & Student Support Advisor", an AI academic assistant for Language Academy (Academia Colombiana de Idiomas).

### Role and Mission:
- Welcoming, highly resolutive, empathetic, and culturally attentive.
- Your goal is to AUTONOMOUSLY RESOLVE repetitive inquiries, friction, and daily operational questions from prospective and active students (programs, COP tuition, payment methods, bank transfer limits, class links, schedules, and policies).
- Provide structured, practical answers using clear Markdown formatting, bullet points, and step-by-step instructions.

### Grounding & Problem-Solving Guidelines:
1. STRICT TRUTH & GROUNDING: Ground your factual statements in the provided Context below. Do not invent non-existent languages or fictional discounts.
2. PROACTIVE TROUBLESHOOTING:
   - For payment issues (e.g. PSE declined, card errors, Nequi/Daviplata): Explain typical Colombian banking daily transfer limits, browser pop-up blockers, installment options ($395,000 COP/mo), or voucher upload steps via WhatsApp.
   - For class access: Explain how to check spam folders, direct access via the student campus portal (campus.languageacademy.edu.co), and cohort WhatsApp groups.
   - For admissions/documents: Explain ID requirements (CC, TI, CE, Passport), age limits (14+), and free placement test booking.
   - For schedule/freezing policies: Explain the 6-month freeze option and refund terms.
3. HANDLING OFF-TOPIC OR UNRELATED INQUIRIES (WITHOUT ESCALATING TO SUPPORT):
   - If the user asks about topics completely unrelated to a language academy (e.g., cooking recipes, aviation mechanics, veterinary medicine, jokes, general knowledge), politely decline and clarify your scope:
     Explain that Language Academy specializes exclusively in language programs (English, French, German, Italian, Portuguese) and invite them to explore language courses. DO NOT escalate these off-topic queries to human support.
4. LEGITIMATE HUMAN ESCALATION CRITERIA:
   - Only output the exact token "[ESCALATE_TO_HUMAN]" when:
     a) The user explicitly demands human assistance ("quiero hablar con un asesor", "comunícame con una persona", "un asesor por favor"), OR
     b) The user reports an unresolved critical operational issue requiring direct manual administrative intervention (e.g., duplicate billing chargeback reversal, customized enterprise agreements for over 50 employees).
5. MULTILINGUAL & CROSS-LINGUAL:
   - Always respond in the EXACT language used by the user (Spanish, English, French, Portuguese, German).
"""

FEW_SHOT_EXAMPLES = [
    # Few-shot Example 1: In-scope pricing & installment query (Spanish)
    (
        "Human: ¿Cuánto cuesta el curso de inglés y qué facilidades de pago tienen en pesos colombianos?\n\nContext: Standard Program: Single Module / Level (16 Weeks - 96 Total Hours): Full Upfront Payment: $1,450,000 COP per level. Monthly Installment Plan: 4 monthly payments of $395,000 COP (Total: $1,580,000 COP). Early Bird Discount (Pronto Pago): 15% discount when enrolling at least 15 days prior.",
        "¡Hola! Con gusto te comparto las opciones oficiales de inversión para nuestro **Programa Estándar de Inglés** en Pesos Colombianos (COP):\n\n- **Pago Único de Contado (1 Nivel / 16 semanas - 96 horas)**: $1,450,000 COP.\n- **Plan Financiado en Cuotas Mensuales**: 4 cuotas de $395,000 COP (Total: $1,580,000 COP sin intereses).\n\n💡 **Descuentos Disponibles**:\n- **Pronto Pago**: 15% de descuento al inscribirte 15 días antes del inicio.\n- **Cajas de Compensación (Compensar / Colsubsidio / Comfama)**: Hasta 20% de descuento para afiliados Categoría A.\n\nAceptamos PSE, tarjetas de crédito, Nequi y Daviplata."
    ),
    # Few-shot Example 2: Troubleshooting Payment Issue (Spanish)
    (
        "Human: Tengo un problema con el pago, intenté pagar por PSE y me salió transacción rechazada.\n\nContext: Payment Declined via PSE or Credit Card: 1. Daily Transfer Limit in Banking App: Most Colombian banks have default daily transfer limits ($1,000,000 - $1,500,000 COP). Temporarily raise your PSE limit in your banking app. 2. Verify available balance. 3. Alternative: Split into monthly installments of $395,000 COP or pay via Nequi/Daviplata. If money was debited without confirmation, send voucher to WhatsApp +57 (300) 123-4567.",
        "No te preocupes, los rechazos en la pasarela de PSE suelen ocurrir por tres motivos muy comunes con soluciones sencillas:\n\n1. **Topes diarios de transferencia en tu app bancaria:** En Colombia (Bancolombia, Davivienda, etc.), el límite diario por defecto para PSE suele ser de $1,000,000 COP. Como el nivel de contado es de $1,450,000 COP, ingresa a tu aplicación bancaria y sube temporalmente el tope de pagos PSE.\n2. **Fondos disponibles:** Verifica que tu saldo cubra el valor total.\n3. **Bloqueador de ventanas emergentes:** Asegúrate de permitir pop-ups en tu navegador o intenta en una pestaña de incógnito.\n\n💡 **Alternativas Inmediatas:**\n- Puedes elegir el **Plan en 4 Cuotas de $395,000 COP**, el cual pasa sin problemas por cualquier límite bancario.\n- O realizar transferencia directa mediante **Nequi / Daviplata**.\n\n*Nota: Si el dinero fue debitado de tu cuenta pero no viste la pantalla de confirmación, envíanos el comprobante con número CUS por WhatsApp al `+57 (300) 123-4567` para activar tu matrícula de inmediato.*"
    ),
    # Few-shot Example 3: Off-topic / Unrelated inquiry (No escalation!)
    (
        "Human: ¿Tienen cursos de mecánica de aviación o cirugía veterinaria?\n\nContext: Available Language Programs: General and Intensive English, Business English, French, German, Italian, and Portuguese.",
        "En **Language Academy** nos especializamos exclusivamente en la enseñanza de idiomas extranjeros (Inglés, Francés, Alemán, Italiano y Portugués), por lo que no contamos con cursos de mecánica o áreas veterinarias.\n\nSi estás interesado en aprender o certificar un segundo idioma para tu desarrollo profesional, con mucho gusto te brindo información sobre nuestros programas de idiomas. ¿Te gustaría conocer nuestras opciones?"
    ),
    # Few-shot Example 4: Explicit Human Request -> Legitimate Escalation
    (
        "Human: Por favor comunícame con un asesor humano, tengo un caso especial.\n\nContext: Human Support: admisiones@languageacademy.edu.co, WhatsApp +57 (300) 123-4567.",
        "[ESCALATE_TO_HUMAN]"
    ),
]


def _extract_text_content(content: Any) -> str:
    """Extract plain text from LLM response content."""
    if isinstance(content, str):
        return content.strip()
    elif isinstance(content, list):
        text_parts = []
        for part in content:
            if isinstance(part, dict) and "text" in part:
                text_parts.append(part["text"])
            elif isinstance(part, str):
                text_parts.append(part)
            elif hasattr(part, "text"):
                text_parts.append(part.text)
        return "\n".join(text_parts).strip()
    return str(content).strip()


class RAGEngine:
    """Production RAG Engine with Intent Routing, Caching, Anti-Hallucination, and Proactive FAQ Resolution."""

    def __init__(self):
        self.vector_store: Optional[Chroma] = None
        self.embeddings = None
        self.llm = None
        self._init_components()

    def _init_components(self):
        """Initialize Chroma vector store and LLM model."""
        try:
            self.embeddings = get_embedding_function()
            self.vector_store = Chroma(
                persist_directory=str(VECTOR_DB_DIR),
                embedding_function=self.embeddings,
            )

            if LLM_PROVIDER == "gemini" or GOOGLE_API_KEY:
                if not GOOGLE_API_KEY:
                    logger.warning("GOOGLE_API_KEY is not set. RAG engine will not execute queries.")
                    return
                from langchain_google_genai import ChatGoogleGenerativeAI
                model_to_use = GEMINI_MODEL_NAME if GEMINI_MODEL_NAME else "gemini-3.5-flash-lite"
                self.llm = ChatGoogleGenerativeAI(
                    model=model_to_use,
                    google_api_key=GOOGLE_API_KEY,
                    temperature=0.1,
                )
                logger.info(f"RAG Engine initialized with Google Gemini ({model_to_use}).")
            else:
                if not OPENAI_API_KEY:
                    logger.warning("OPENAI_API_KEY is not set.")
                    return
                from langchain_openai import ChatOpenAI
                self.llm = ChatOpenAI(
                    openai_api_key=OPENAI_API_KEY,
                    model_name=OPENAI_MODEL_NAME,
                    temperature=0.1,
                )
                logger.info(f"RAG Engine initialized with OpenAI ({OPENAI_MODEL_NAME}).")
        except Exception as e:
            logger.error(f"Error initializing RAG Engine components: {e}")

    def _build_prompt_messages(self, query: str, context: str):
        """Assemble chat prompt template with System instructions, few-shot examples, and context."""
        messages = [
            SystemMessagePromptTemplate.from_template(SYSTEM_PROMPT_TEMPLATE)
        ]

        # Add Few-shot examples
        for human_shot, ai_shot in FEW_SHOT_EXAMPLES:
            messages.append(HumanMessagePromptTemplate.from_template(human_shot))
            messages.append(AIMessagePromptTemplate.from_template(ai_shot))

        # Add current user query with retrieved knowledge context
        current_user_template = "Human: {query}\n\nContext:\n{context}"
        messages.append(HumanMessagePromptTemplate.from_template(current_user_template))

        return ChatPromptTemplate.from_messages(messages)

    def _format_escalation_response(self, user_query: str) -> str:
        """Standard human escalation format with contact details."""
        return (
            f"Para brindarte una atención personalizada con tu solicitud, he transferido tu consulta a nuestro equipo de admisiones de **{ACADEMY_NAME}**.\n\n"
            f"👩‍💼 **Canales Oficiales de Atención:**\n"
            f"- 📱 **WhatsApp / Teléfono Móvil:** [{HUMAN_SUPPORT_PHONE}](https://wa.me/573001234567)\n"
            f"- 📧 **Correo de Admisiones:** `{HUMAN_SUPPORT_EMAIL}`\n"
            f"- ☎️ **PBX Bogotá:** +57 (601) 745-8900\n"
            f"- ⏰ **Horario de Atención:** {HUMAN_SUPPORT_HOURS}\n\n"
            f"Uno de nuestros asesores te responderá a la mayor brevedad o puedes escribirnos directamente."
        )

    def query(self, user_query: str, channel: str = "web_form") -> Dict[str, Any]:
        """
        Process a user inquiry through the full intelligent pipeline:
        1. Fast Intent Router (Sub-millisecond greetings, thanks, farewells, inappropriate filters, explicit human requests).
        2. Dual-tier Exact/Semantic Cache.
        3. Vector similarity search in ChromaDB.
        4. LLM inference with proactive problem solving & scope boundaries.
        5. Smart escalation & telemetry recording.
        """
        start_time = time.time()
        cleaned_query = user_query.strip()

        if not cleaned_query:
            return {
                "answer": "Por favor escribe una consulta sobre nuestros programas de idiomas, precios, horarios o resolución de dudas en Language Academy.",
                "escalated": False,
                "sources": [],
                "cached": True,
                "latency_ms": 0.5,
            }

        # --- STEP 1: FAST INTENT ROUTER (< 2 ms, 0 API tokens) ---
        fast_intent = IntentRouter.classify(cleaned_query)
        if fast_intent:
            latency_ms = round((time.time() - start_time) * 1000, 2)
            fast_intent["latency_ms"] = latency_ms
            metrics_collector.record_query(
                query=cleaned_query,
                latency_ms=latency_ms,
                escalated=fast_intent.get("escalated", False),
                cached=True,
                prompt_tokens=0,
                completion_tokens=0,
                channel=channel,
            )
            return fast_intent

        # --- STEP 2: DUAL-TIER RESPONSE CACHE ---
        query_vector = None
        if self.embeddings:
            try:
                query_vector = self.embeddings.embed_query(cleaned_query)
            except Exception as e:
                logger.debug(f"Could not compute query vector for cache check: {e}")

        cached_entry = response_cache.get(cleaned_query, query_embedding=query_vector)
        if cached_entry:
            latency_ms = round((time.time() - start_time) * 1000, 2)
            metrics_collector.record_query(
                query=cleaned_query,
                latency_ms=latency_ms,
                escalated=cached_entry.get("escalated", False),
                cached=True,
                prompt_tokens=0,
                completion_tokens=0,
                channel=channel,
            )
            return {
                "answer": cached_entry["answer"],
                "escalated": cached_entry.get("escalated", False),
                "sources": cached_entry.get("sources", []),
                "cached": True,
                "latency_ms": latency_ms,
            }

        # --- STEP 3: VECTOR RETRIEVAL IN CHROMADB ---
        context_docs = []
        sources = []
        if self.vector_store:
            try:
                search_results = self.vector_store.similarity_search_with_score(cleaned_query, k=5)
                for doc, score in search_results:
                    context_docs.append(doc.page_content)
                    source_name = doc.metadata.get("source", "knowledge_base")
                    if source_name not in sources:
                        sources.append(source_name)
            except Exception as e:
                logger.error(f"Error during vector search: {e}")

        context_text = "\n\n---\n\n".join(context_docs) if context_docs else "No specific documents found."

        # Fallback if LLM is not configured
        if not self.llm:
            fallback_answer = self._format_escalation_response(cleaned_query)
            latency_ms = round((time.time() - start_time) * 1000, 2)
            metrics_collector.record_query(
                query=cleaned_query,
                latency_ms=latency_ms,
                escalated=True,
                cached=False,
                prompt_tokens=0,
                completion_tokens=0,
                channel=channel,
            )
            return {
                "answer": fallback_answer,
                "escalated": True,
                "sources": sources,
                "cached": False,
                "latency_ms": latency_ms,
            }

        # --- STEP 4: LLM INFERENCE ---
        prompt_chat = self._build_prompt_messages(cleaned_query, context_text)
        formatted_messages = prompt_chat.format_messages(query=cleaned_query, context=context_text)

        approx_prompt_tokens = sum(len(m.content.split()) for m in formatted_messages) * 2

        try:
            llm_response = self.llm.invoke(formatted_messages)
            raw_answer = _extract_text_content(llm_response.content)
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            raw_answer = "En Language Academy estamos especializados en cursos de idiomas (Inglés, Francés, Alemán, Italiano y Portugués). ¿En qué idioma te gustaría formarte?"

        approx_completion_tokens = len(raw_answer.split()) * 2

        # --- STEP 5: SMART ESCALATION & FORMATTING ---
        escalated = False
        if "[ESCALATE_TO_HUMAN]" in raw_answer:
            final_answer = self._format_escalation_response(cleaned_query)
            escalated = True
        else:
            final_answer = raw_answer.strip()

        latency_ms = round((time.time() - start_time) * 1000, 2)

        # Cache valid in-scope responses
        if not escalated:
            response_cache.set(
                query=cleaned_query,
                answer=final_answer,
                sources=sources,
                escalated=False,
                query_embedding=query_vector,
            )

        metrics_collector.record_query(
            query=cleaned_query,
            latency_ms=latency_ms,
            escalated=escalated,
            cached=False,
            prompt_tokens=approx_prompt_tokens,
            completion_tokens=approx_completion_tokens,
            channel=channel,
        )

        return {
            "answer": final_answer,
            "escalated": escalated,
            "sources": sources,
            "cached": False,
            "latency_ms": latency_ms,
        }


# Global Singleton RAG Engine Instance
rag_engine = RAGEngine()
