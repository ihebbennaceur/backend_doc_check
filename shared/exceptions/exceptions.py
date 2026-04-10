"""Shared exceptions - __init__"""

from . import (
    FizboException,
    ValidationError,
    NotFoundError,
    UnauthorizedError,
    ForbiddenError,
    PaymentError,
    DocumentError,
    OCRError,
    ExternalServiceError,
    DuplicateError,
    WorkflowError,
)

__all__ = [
    "FizboException",
    "ValidationError",
    "NotFoundError",
    "UnauthorizedError",
    "ForbiddenError",
    "PaymentError",
    "DocumentError",
    "OCRError",
    "ExternalServiceError",
    "DuplicateError",
    "WorkflowError",
]
