"""
AI Company - Configuration Settings
"""
import os
from dotenv import load_dotenv
from google.adk.models.lite_llm import LiteLlm

load_dotenv()

# Server Configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "9000"))

# =============================================================================
# Model Configuration - LiteLLM Multi-Provider Support
# =============================================================================
# Set the desired provider in .env: MODEL_PROVIDER=anthropic|openai|google

MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "google")

# Model name mappings per provider
MODEL_NAMES = {
    "anthropic": {
        "default": "anthropic/claude-sonnet-4-20250514",
        "fast": "anthropic/claude-3-5-haiku-20241022",
        "powerful": "anthropic/claude-opus-4-20250514",
    },
    "openai": {
        "default": "openai/gpt-4o",
        "fast": "openai/gpt-4o-mini",
        "powerful": "openai/o1",
    },
    "google": {
        "default": "gemini/gemini-2.0-flash",
        "fast": "gemini/gemini-2.0-flash",
        "powerful": "gemini/gemini-1.5-pro",
    },
}

# Get model names for current provider
_provider_models = MODEL_NAMES.get(MODEL_PROVIDER, MODEL_NAMES["google"])

# LiteLLM Model instances
DEFAULT_MODEL = LiteLlm(model=os.getenv("DEFAULT_MODEL", _provider_models["default"]))
FAST_MODEL = LiteLlm(model=os.getenv("FAST_MODEL", _provider_models["fast"]))
POWERFUL_MODEL = LiteLlm(model=os.getenv("POWERFUL_MODEL", _provider_models["powerful"]))

# Legacy: Keep string version for reference
DEFAULT_MODEL_NAME = os.getenv("DEFAULT_MODEL", _provider_models["default"])

# =============================================================================
# API Keys - Required based on MODEL_PROVIDER
# =============================================================================
# Anthropic: ANTHROPIC_API_KEY
# OpenAI: OPENAI_API_KEY
# Google: GOOGLE_API_KEY

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Validate API key for selected provider
def _validate_api_key():
    required_keys = {
        "anthropic": ("ANTHROPIC_API_KEY", ANTHROPIC_API_KEY),
        "openai": ("OPENAI_API_KEY", OPENAI_API_KEY),
        "google": ("GOOGLE_API_KEY", GOOGLE_API_KEY),
    }
    key_name, key_value = required_keys.get(MODEL_PROVIDER, ("GOOGLE_API_KEY", GOOGLE_API_KEY))
    if not key_value:
        raise RuntimeError(
            f"{key_name} is not set. Add it to your .env file for {MODEL_PROVIDER} provider."
        )

_validate_api_key()

# Agent Registry - maps agent names to their ports
AGENT_PORTS = {
    "ceo_agent": 9000,
    "developer_agent": 9001,
    "marketing_agent": 9002,
    "hr_agent": 9003,
}
