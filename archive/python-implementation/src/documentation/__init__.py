"""
Documentation Module

Provides automatic documentation generation and maintenance.
Keeps documentation synchronized with code changes.
"""

from .auto_documenter import (
    AutoDocumenter,
    DocumentationType,
    DocumentationUpdate,
    CodeAnalysis,
)

__all__ = [
    "AutoDocumenter",
    "DocumentationType",
    "DocumentationUpdate",
    "CodeAnalysis",
]

__version__ = "0.1.0"
