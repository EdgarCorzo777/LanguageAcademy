# AI, RAG & Prompt Engineering Design

## 1. Cross-Lingual Semantic Retrieval

### 1.1 The Cross-Lingual Embedding Space
Multilingual embedding models such as `gemini-embedding-001` project multilingual text into a unified high-dimensional vector space. Phrases carrying equivalent semantic intent across languages (such as "¿Cuáles son los horarios de clase?" in Spanish and "What is the class schedule?" in English) reside in close vector proximity.

```
       [Spanish: Horarios y jornadas]
                    ^
                    | (High Cosine Similarity > 0.85)
                    v
       [English: Schedules and Shifts]
```

### 1.2 Prompt Engineering Strategy
The system prompt explicitly commands the LLM to:
1. Detect the user's input language and formulate the response in that identical language.
2. Extract and ground facts solely from the retrieved context chunks regardless of their source language.
3. Proactively resolve operational friction (PSE banking limits, missing class links, module freezing, and placement tests).
4. Politely establish scope boundaries for non-language topics without escalating to human support.

---

## 2. Anti-Hallucination & Grounding Guardrails

### 2.1 Guardrail Directives
- **Zero Extrapolation**: The model is forbidden from inventing unlisted languages (e.g. Japanese, Russian), fictional discounts, or arbitrary prices.
- **Currency Enforcement**: Official tuition prices are strictly framed in Colombian Pesos (COP).
- **Disinterest & Rejection Handling**: When a user states they do not want advice or assistance, the assistant responds politely without creating support tickets.
- **Controlled Escalation**: The LLM outputs `[ESCALATE_TO_HUMAN]` exclusively for critical accounting disputes or explicit human advisor requests.

### 2.2 Few-Shot Demonstration Structure
1. **Sample 1 (Spanish In-Scope)**: COP tuition rates, installment plans, and Compensar discounts.
2. **Sample 2 (Operational Troubleshooting)**: Step-by-step resolution for PSE payment declined issues.
3. **Sample 3 (Off-Topic Inquiries)**: Polite explanation of specialization exclusively in languages.
4. **Sample 4 (Legitimate Escalation)**: Explicit human contact request generating `[ESCALATE_TO_HUMAN]`.

---

## 3. Financial & Token Telemetry

- Input Token Rate: $0.075 USD per 1M tokens.
- Output Token Rate: $0.30 USD per 1M tokens.
- Total Cost Calculation:
  $$\text{Cost} = \left(\frac{\text{Prompt Tokens}}{1,000,000} \times 0.075\right) + \left(\frac{\text{Completion Tokens}}{1,000,000} \times 0.30\right)$$
