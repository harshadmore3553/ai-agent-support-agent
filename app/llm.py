from __future__ import annotations

import re

from .config import OPENAI_API_KEY, OPENAI_MODEL


class LLM:
    def __init__(self):
        self.model = OPENAI_MODEL
        self.client = None

        # Use OpenAI when an API key is available.
        if OPENAI_API_KEY:
            from openai import OpenAI
            self.client = OpenAI(api_key=OPENAI_API_KEY)

    def answer(self, system: str, user_input: str) -> str:
        # Normal OpenAI mode
        if self.client:
            response = self.client.responses.create(
                model=self.model,
                instructions=system,
                input=user_input,
            )
            return response.output_text.strip()

        # Offline demo mode
        return self.local_answer(user_input)

    def local_answer(self, user_input: str) -> str:
        """
        Offline fallback.

        It extracts the retrieved knowledge passages from the agent prompt
        and produces a grounded answer without requiring an API key.
        """

        text = user_input

        # Get the customer's actual question.
        question_match = re.search(
            r"Current customer message:\s*(.*?)\s*"
            r"Retrieved knowledge-base passages:",
            text,
            re.DOTALL | re.IGNORECASE,
        )

        question = (
            question_match.group(1).strip()
            if question_match
            else text.strip()
        )

        question_lower = question.lower()

        # Extract retrieved source blocks.
        passages = re.findall(
            r"\[SOURCE\]\s*"
            r"filename=(.*?)\s*"
            r"heading=(.*?)\s*"
            r"metadata=.*?\s*"
            r"content=(.*?)(?=\n\n\[SOURCE\]|\Z)",
            text,
            re.DOTALL | re.IGNORECASE,
        )

        if not passages:
            return (
                "The supplied information is insufficient for me to answer "
                "that reliably. I recommend confirming this with human support."
            )

        # Find the most relevant passage using simple keyword overlap.
        question_words = {
            w for w in re.findall(r"[a-zA-Z]{3,}", question_lower)
        }

        scored = []

        for filename, heading, content in passages:
            content_lower = content.lower()
            heading_lower = heading.lower()

            score = 0

            for word in question_words:
                if word in content_lower:
                    score += 1
                if word in heading_lower:
                    score += 2

            # Strong hints for common customer questions.
            if "return" in question_lower and "return" in content_lower:
                score += 8

            if "shipping" in question_lower and "shipping" in content_lower:
                score += 8

            if "warranty" in question_lower and "warranty" in content_lower:
                score += 8

            if "dishwasher" in question_lower and "dishwasher" in content_lower:
                score += 8

            if "trailplus" in question_lower and "trailplus" in content_lower:
                score += 8

            scored.append(
                (score, filename.strip(), heading.strip(), content.strip())
            )

        scored.sort(reverse=True, key=lambda x: x[0])

        best = scored[0]

        if best[0] <= 0:
            return (
                "The supplied information does not contain enough relevant "
                "information to answer that reliably. I recommend human support."
            )

        _, filename, heading, content = best

        # Extract useful sentences from the best passage.
        sentences = re.split(r"(?<=[.!?])\s+", content)

        useful = []

        for sentence in sentences:
            sentence = sentence.strip()

            if not sentence:
                continue

            sentence_lower = sentence.lower()

            relevant = any(
                word in sentence_lower
                for word in question_words
            )

            if relevant:
                useful.append(sentence)

        # If keyword matching found nothing, use the first few sentences.
        if not useful:
            useful = sentences[:3]

        # Keep the demo response concise.
        useful = useful[:4]

        answer = " ".join(useful).strip()

        if not answer:
            answer = (
                "The relevant information is available in the supplied "
                "knowledge base, but I cannot summarize it reliably offline."
            )

        return answer