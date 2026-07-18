"""Prompt templates for course generation, quizzes and the RAG chatbot."""
from __future__ import annotations

COURSE_SYSTEM_PROMPT = (
    "You are an expert instructional designer. You turn raw document text into a "
    "well-structured, pedagogically sound e-learning course. Always respond with "
    "valid JSON only, matching the requested schema exactly."
)

COURSE_STRUCTURE_TEMPLATE = """Using ONLY the document content below, design a course.

Return JSON with this exact schema:
{{
  "title": string,
  "description": string,
  "difficulty": "beginner" | "intermediate" | "advanced",
  "estimated_minutes": integer,
  "learning_objectives": string[],
  "prerequisites": string[],
  "tags": string[],
  "chapters": [
    {{
      "title": string,
      "summary": string,
      "lessons": [
        {{
          "title": string,
          "explanation": string,
          "examples": string,
          "important_notes": string,
          "summary": string,
          "key_takeaways": string[],
          "estimated_minutes": integer
        }}
      ]
    }}
  ]
}}

Constraints:
- Produce between 3 and {max_chapters} chapters, each with 2-5 lessons.
- "explanation" must be a thorough markdown explanation (150-400 words).
- Base everything strictly on the document; do not invent facts.
- Target difficulty: {difficulty}.

DOCUMENT CONTENT:
\"\"\"
{content}
\"\"\"
"""

QUIZ_SYSTEM_PROMPT = (
    "You are an assessment designer. You write fair, unambiguous quiz questions "
    "grounded strictly in the provided material. Respond with valid JSON only."
)

QUIZ_TEMPLATE = """Create a quiz based ONLY on the material below.

Return JSON with this exact schema:
{{
  "title": string,
  "description": string,
  "questions": [
    {{
      "question_type": "mcq" | "true_false" | "short_answer",
      "question": string,
      "options": string[],
      "correct_answer": string,
      "explanation": string
    }}
  ]
}}

Constraints:
- Generate exactly {num_questions} questions.
- Allowed question types: {question_types}.
- For "mcq": provide 4 options; "correct_answer" must exactly match one option.
- For "true_false": options must be ["True", "False"].
- For "short_answer": options must be an empty array.
- Every question must include a concise "explanation".

MATERIAL:
\"\"\"
{content}
\"\"\"
"""

RAG_SYSTEM_PROMPT = (
    "You are a helpful study assistant for a specific document. "
    "Answer questions using ONLY the provided context from the document. "
    "If the answer is not contained in the context, say you cannot find it in the "
    "document. Be clear and educational. When helpful, cite page numbers like [p.N]."
)

RAG_USER_TEMPLATE = """Context from the document:
{context}

Conversation so far:
{history}

Question: {question}

Answer using only the context above."""


def format_context(chunks: list[dict]) -> str:
    parts = []
    for chunk in chunks:
        page = chunk.get("page_number")
        marker = f"[p.{page}]" if page else ""
        parts.append(f"{marker} {chunk['content']}".strip())
    return "\n\n---\n\n".join(parts) if parts else "(no relevant context found)"


def format_history(messages: list[dict], limit: int = 6) -> str:
    recent = messages[-limit:]
    if not recent:
        return "(no prior messages)"
    return "\n".join(f"{m['role'].capitalize()}: {m['content']}" for m in recent)
