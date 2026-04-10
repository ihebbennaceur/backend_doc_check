"""
Custom Exceptions for Fizbo Platform
Centralized exception handling for all modules
"""

from rest_framework import status


class FizboException(Exception):
    """Base exception for Fizbo platform"""

    def __init__(self, message: str, code: str = None, status_code: int = 400):
        self.message = message
        self.code = code or self.__class__.__name__
        self.status_code = status_code
        super().__init__(self.message)


class ValidationError(FizboException):
    """Validation error"""

    def __init__(self, message: str, field: str = None):
        self.field = field
        super().__init__(message, "VALIDATION_ERROR", status.HTTP_400_BAD_REQUEST)


class NotFoundError(FizboException):
    """Resource not found"""

    def __init__(self, resource: str, identifier: str = None):
        message = f"{resource} not found"
        if identifier:
            message += f": {identifier}"
        super().__init__(message, "NOT_FOUND", status.HTTP_404_NOT_FOUND)


class UnauthorizedError(FizboException):
    """Unauthorized access"""

    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, "UNAUTHORIZED", status.HTTP_401_UNAUTHORIZED)


class ForbiddenError(FizboException):
    """Forbidden access"""

    def __init__(self, message: str = "Forbidden"):
        super().__init__(message, "FORBIDDEN", status.HTTP_403_FORBIDDEN)


class PaymentError(FizboException):
    """Payment processing error"""

    def __init__(self, message: str, stripe_error: str = None):
        self.stripe_error = stripe_error
        super().__init__(message, "PAYMENT_ERROR", status.HTTP_402_PAYMENT_REQUIRED)


class DocumentError(FizboException):
    """Document processing error"""

    def __init__(self, message: str, document_id: str = None):
        self.document_id = document_id
        super().__init__(message, "DOCUMENT_ERROR", status.HTTP_400_BAD_REQUEST)


class OCRError(FizboException):
    """OCR processing error"""

    def __init__(self, message: str, file_name: str = None):
        self.file_name = file_name
        super().__init__(message, "OCR_ERROR", status.HTTP_400_BAD_REQUEST)


class ExternalServiceError(FizboException):
    """External service (Stripe, OCR API, etc.) error"""

    def __init__(self, service: str, message: str):
        full_message = f"{service} error: {message}"
        super().__init__(full_message, "EXTERNAL_SERVICE_ERROR", status.HTTP_502_BAD_GATEWAY)


class DuplicateError(FizboException):
    """Resource already exists"""

    def __init__(self, resource: str, identifier: str = None):
        message = f"{resource} already exists"
        if identifier:
            message += f": {identifier}"
        super().__init__(message, "DUPLICATE_ERROR", status.HTTP_409_CONFLICT)


class WorkflowError(FizboException):
    """Workflow step error"""

    def __init__(self, message: str, step: str = None):
        self.step = step
        super().__init__(message, "WORKFLOW_ERROR", status.HTTP_400_BAD_REQUEST)


class ConfigurationError(FizboException):
    """Configuration/environment error"""

    def __init__(self, message: str, key: str = None):
        self.key = key
        super().__init__(message, "CONFIGURATION_ERROR", status.HTTP_500_INTERNAL_SERVER_ERROR)
