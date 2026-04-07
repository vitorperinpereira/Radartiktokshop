"""Prompt templates for agent LLM integrations."""

from services.agents.prompts.accessibility_assessment import ACCESSIBILITY_PROMPT
from services.agents.prompts.content_angles import CONTENT_ANGLE_PROMPT
from services.agents.prompts.product_summary import PRODUCT_SUMMARY_PROMPT
from services.agents.prompts.saturation_params import SATURATION_PARAMS_PROMPT
from services.agents.prompts.viral_assessment import VIRAL_ASSESSMENT_PROMPT

__all__ = [
    "ACCESSIBILITY_PROMPT",
    "CONTENT_ANGLE_PROMPT",
    "PRODUCT_SUMMARY_PROMPT",
    "SATURATION_PARAMS_PROMPT",
    "VIRAL_ASSESSMENT_PROMPT",
]
