from __future__ import annotations

from typing import Type, TypeVar

from openai import OpenAI
from pydantic import BaseModel

from .config import Settings
from .prompts import system_guardrails

SchemaT = TypeVar("SchemaT", bound=BaseModel)


class LLMClient:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings()
        self.client = OpenAI(api_key=self.settings.openai_api_key)

    def parse(self, schema: Type[SchemaT], user_prompt: str, system_prompt: str | None = None) -> SchemaT:
        final_system_prompt = (system_prompt or "").strip()
        if final_system_prompt:
            final_system_prompt = system_guardrails() + "\n\n" + final_system_prompt
        else:
            final_system_prompt = system_guardrails()

        # Preferred path: Responses API structured parsing
        try:
            response = self.client.responses.parse(
                model=self.settings.openai_model,
                input=[
                    {"role": "system", "content": final_system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                text_format=schema,
            )
            parsed = getattr(response, "output_parsed", None)
            if parsed is not None:
                return parsed
        except Exception:
            pass

        # Fallback path: Chat Completions structured parsing
        completion = self.client.chat.completions.parse(
            model=self.settings.openai_model,
            messages=[
                {"role": "system", "content": final_system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format=schema,
        )
        parsed = completion.choices[0].message.parsed
        if parsed is None:
            refusal = getattr(completion.choices[0].message, "refusal", None)
            raise ValueError(f"Model did not return parsed structured output. Refusal={refusal!r}")
        return parsed
