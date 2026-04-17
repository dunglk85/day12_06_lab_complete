from __future__ import annotations

from dataclasses import dataclass
import os
from dotenv import load_dotenv


@dataclass(frozen=True)
class AgentSettings:
    model_name: str = "gpt-4o-mini"



def load_settings() -> AgentSettings:
    """Load environment variables and build immutable agent settings."""
    load_dotenv()
    return AgentSettings(
        model_name=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
    )