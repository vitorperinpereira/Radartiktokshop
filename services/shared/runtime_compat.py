"""Runtime compatibility shims for third-party dependencies."""

from __future__ import annotations

import sys
import warnings

_LANGCHAIN_PYDANTIC_V1_WARNING = (
    r"Core Pydantic V1 functionality isn't compatible with Python 3\.14 or greater\."
)
_LANGGRAPH_ASYNCIO_WARNING = (
    r"'asyncio\.iscoroutinefunction' is deprecated and slated for removal in Python 3\.16; "
    r"use inspect\.iscoroutinefunction\(\) instead"
)


def install_python314_warning_filters() -> None:
    """Suppress known upstream warnings until LangChain and LangGraph resolve them."""

    if sys.version_info < (3, 14):
        return

    warnings.filterwarnings(
        "ignore",
        message=_LANGCHAIN_PYDANTIC_V1_WARNING,
        category=UserWarning,
        module=r"langchain_core\._api\.deprecation",
    )
    warnings.filterwarnings(
        "ignore",
        message=_LANGGRAPH_ASYNCIO_WARNING,
        category=DeprecationWarning,
        module=r"langgraph\._internal\._runnable",
    )
