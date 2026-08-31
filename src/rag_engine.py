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

from src.config import (
    VECTOR_DB_DIR,
    LLM_PROVIDER,
    GOOGLE_API_KEY,
    GEMINI_MODEL_NAME,
    OPENAI_API_KEY,
    OPENAI_MODEL_NAME,
    HUMAN_SUPPORT_EMAIL,
    HUMAN_SUPPORT_PHONE,
)
from src.ingestion import get_embedding_function

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

SYSTEM_PROMPT_TEMPLATE = """You are "TechUni Admissions Advisor", the official AI Admissions Assistant for the technological university.

### Role & Personality:
- Professional, welcoming, encouraging, and brand-aligned.
- Provide clear, concise, and structured answers (using markdown bullet points where appropriate).
- Always maintain an informative and helpful tone.

### Grounding & Anti-Hallucination Rules:
1. ONLY answer questions using facts from the provided Context below.
2. DO NOT invent unlisted degrees, discounts, prerequisites, or policies.
3. When users ask for tuition in other currencies (like COP, EUR, MXN), provide the official tuition prices from the Context (which are in USD) and clarify that all university tuition rates are officially established in USD.
4. If a question is genuinely OUT OF SCOPE (e.g. medicine, culinary arts, fixing cars, personal advice, unlisted academic fields), you MUST respond ONLY with the exact fallback token: "[ESCALATE_TO_HUMAN]".
"""

FEW_SHOT_EXAMPLES = [
    # Few-shot Example 1: In-scope inquiry (Tuition & Currency)
    (
        "Human: How much does the AI Engineering Program cost in COP?\n\nContext: AI Engineering Program: Full Upfront Payment: $3,200 USD. Installment Plan: $850 USD/month for 4 months (Total: $3,400 USD).",
        "Our official tuition fees are established in **USD**. For the **AI Engineering Program**, the costs are:\n\n- **Upfront Payment**: $3,200 USD.\n- **Installment Plan**: 4 monthly payments of $850 USD (Total: $3,400 USD).\n- **Income Share Agreement (ISA)**: 12% of gross monthly salary once you secure a tech job earning at least $1,500 USD/month (capped at $4,500 USD).\n\nIf you are paying from Colombia (COP), local bank transfers and major credit cards are accepted, and the exchange rate will be calculated based on the payment date's official rate."
    ),
    # Few-shot Example 2: In-scope inquiry (Schedules & Modality)
    (
        "Human: Can I study while working full-time? What are the schedules?\n\nContext: Part-Time Evening Cohort: Monday to Thursday 6:00 PM - 9:30 PM, plus Saturday 9:00 AM - 1:00 PM (UTC-5). 100% Live Online (Remote) format.",
        "Yes, absolutely! We offer a **Part-Time Evening Cohort** specifically designed for working professionals:\n\n- **Schedule**: Monday through Thursday, 6:00 PM – 9:30 PM, and Saturday 9:00 AM – 1:00 PM (UTC-5).\n- **Modality**: 100% Live Online with interactive sessions and daily mentor office hours.\n\nThis schedule requires 18 live instructional hours and 7 project hours weekly, allowing you to balance work and learning."
    ),
    # Few-shot Example 3: Out-of-scope / Missing information -> Escalation
    (
        "Human: Do you offer a Bachelor's Degree in Dentistry or Medicine?\n\nContext: AI Engineering Program, Full-Stack Web Development Program, Data Science & Analytics Program, Cloud & Cybersecurity Program.",
        "[ESCALATE_TO_HUMAN]"
    ),
]


def _extract_text_content(content: Any) -> str:
    """Extract plain text from LLM response content (supports str and list of parts)."""
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
    def __init__(self):
        self.vector_store: Optional[Chroma] = None
        self.llm = None
        self._init_components()

    def _init_components(self):
        """Initialize Chroma vector store and LLM model (Gemini or OpenAI)."""
        try:
            embeddings = get_embedding_function()
            self.vector_store = Chroma(
                persist_directory=str(VECTOR_DB_DIR),
                embedding_function=embeddings,
            )

            if LLM_PROVIDER == "gemini" or GOOGLE_API_KEY:
                if not GOOGLE_API_KEY:
                    logger.warning("GOOGLE_API_KEY is not set. RAG engine will not function until key is configured.")
                    return
                from langchain_google_genai import ChatGoogleGenerativeAI
                model_to_use = GEMINI_MODEL_NAME if GEMINI_MODEL_NAME else "gemini-flash-latest"
                self.llm = ChatGoogleGenerativeAI(
                    model=model_to_use,
                    google_api_key=GOOGLE_API_KEY,
                    temperature=0.1,
                )
                logger.info(f"RAG Engine successfully initialized with Google Gemini ({model_to_use}).")
            else:
                if not OPENAI_API_KEY:
                    logger.warning("OPENAI_API_KEY is not set. RAG engine will not function until key is configured.")
                    return
                from langchain_openai import ChatOpenAI
                self.llm = ChatOpenAI(
                    openai_api_key=OPENAI_API_KEY,
                    model_name=OPENAI_MODEL_NAME,
                    temperature=0.1,
                )
                logger.info(f"RAG Engine successfully initialized with OpenAI ({OPENAI_MODEL_NAME}).")
        except Exception as e:
            logger.error(f"Error initializing RAG Engine: {e}")

    def _build_prompt_messages(self, query: str, context: str):
        """Assemble the chat prompt with System prompt, 3 Few-Shot examples, and current query."""
        messages = [
            SystemMessagePromptTemplate.from_template(SYSTEM_PROMPT_TEMPLATE)
        ]

        # Add Few-shot examples
        for user_ex, ai_ex in FEW_SHOT_EXAMPLES:
            messages.append(HumanMessagePromptTemplate.from_template(user_ex))
            messages.append(AIMessagePromptTemplate.from_template(ai_ex))

        # Add Current User Turn
        current_user_template = "Human: {query}\n\nContext:\n{context}"
        messages.append(HumanMessagePromptTemplate.from_template(current_user_template))

        return ChatPromptTemplate.from_messages(messages)

    def _format_human_escalation_message(self, reason: str = "out_of_scope") -> str:
        """Standard brand-aligned response when inquiry requires human staff escalation."""
        return (
            "I'm sorry, but I don't have enough specific information in our official records "
            "to answer that accurately. To make sure you get the best guidance, I have escalated "
            "your inquiry to our human admissions team.\n\n"
            "👩‍💼 **Admissions Support Contact:**\n"
            f"📧 Email: `{HUMAN_SUPPORT_EMAIL}`\n"
            f"📞 Phone/WhatsApp: `{HUMAN_SUPPORT_PHONE}`\n"
            "⏰ Hours: Monday - Friday, 8:00 AM - 6:00 PM (UTC-5)\n\n"
            "An admissions specialist will be happy to assist you directly!"
        )

    def query(self, user_query: str) -> Dict[str, Any]:
        """
        Process a user query through the RAG pipeline.
        Returns:
            dict containing 'answer', 'escalated' (bool), and 'sources' (list).
        """
        if not user_query or not user_query.strip():
            return {
                "answer": "Please ask a question about our admissions, programs, schedules, or pricing.",
                "escalated": False,
                "sources": [],
            }

        if not self.vector_store or not self.llm:
            self._init_components()
            if not self.vector_store or not self.llm:
                return {
                    "answer": self._format_human_escalation_message(),
                    "escalated": True,
                    "sources": [],
                }

        try:
            # Semantic search to retrieve relevant context chunks
            relevant_docs = self.vector_store.similarity_search(user_query, k=4)

            sources = []
            for doc in relevant_docs:
                src = doc.metadata.get("source", "Knowledge Base")
                if src not in sources:
                    sources.append(src)

            # If vector store is empty, escalate
            if not relevant_docs:
                logger.info(f"No documents found for query: '{user_query}'. Escalating.")
                return {
                    "answer": self._format_human_escalation_message(),
                    "escalated": True,
                    "sources": [],
                }

            # Build context string from retrieved chunks
            context_text = "\n\n---\n\n".join([doc.page_content for doc in relevant_docs])

            # Prepare Prompt
            prompt_template = self._build_prompt_messages(user_query, context_text)
            formatted_messages = prompt_template.format_messages(
                query=user_query, context=context_text
            )

            # Generate response from LLM
            response = self.llm.invoke(formatted_messages)
            raw_answer = _extract_text_content(response.content)

            # Check for escalation token from LLM
            if "[ESCALATE_TO_HUMAN]" in raw_answer:
                logger.info(f"LLM indicated question is out of scope for query: '{user_query}'. Escalating.")
                return {
                    "answer": self._format_human_escalation_message(),
                    "escalated": True,
                    "sources": sources,
                }

            return {
                "answer": raw_answer,
                "escalated": False,
                "sources": sources,
            }

        except Exception as e:
            logger.error(f"Error during RAG query execution: {e}")
            return {
                "answer": self._format_human_escalation_message(),
                "escalated": True,
                "sources": [],
            }


# Singleton instance for application reuse
rag_engine = RAGEngine()
