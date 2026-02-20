from __future__ import annotations


class SavdhaanError(Exception):
    """Base exception for all Savdhaan AI errors."""

    def __init__(self, message: str = "An unexpected error occurred", code: str = "INTERNAL_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


# --- Input Validation ---


class InvalidInputError(SavdhaanError):
    def __init__(self, message: str = "Invalid input"):
        super().__init__(message=message, code="INVALID_INPUT")


class PayloadTooLargeError(SavdhaanError):
    def __init__(self, message: str = "Payload too large"):
        super().__init__(message=message, code="PAYLOAD_TOO_LARGE")


class UnsupportedMediaTypeError(SavdhaanError):
    def __init__(self, message: str = "Unsupported media type"):
        super().__init__(message=message, code="UNSUPPORTED_MEDIA_TYPE")


# --- Auth ---


class UnauthorizedError(SavdhaanError):
    def __init__(self, message: str = "Missing or invalid API key"):
        super().__init__(message=message, code="UNAUTHORIZED")


class ForbiddenError(SavdhaanError):
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message=message, code="FORBIDDEN")


# --- Rate Limiting ---


class RateLimitExceededError(SavdhaanError):
    def __init__(self, message: str = "Rate limit exceeded", retry_after: int = 60):
        self.retry_after = retry_after
        super().__init__(message=message, code="RATE_LIMIT_EXCEEDED")


# --- Resource ---


class NotFoundError(SavdhaanError):
    def __init__(self, resource: str = "Resource", resource_id: str = ""):
        message = f"{resource} not found"
        if resource_id:
            message = f"{resource} '{resource_id}' not found"
        super().__init__(message=message, code="NOT_FOUND")


# --- External Services ---


class ExternalServiceError(SavdhaanError):
    """An external service (threat intel, LLM, OCR) failed."""

    def __init__(self, service: str, message: str = "Service unavailable"):
        self.service = service
        super().__init__(message=f"{service}: {message}", code="EXTERNAL_SERVICE_ERROR")


class LLMError(ExternalServiceError):
    def __init__(self, message: str = "LLM service unavailable"):
        super().__init__(service="claude", message=message)


class OCRError(ExternalServiceError):
    def __init__(self, message: str = "OCR service unavailable"):
        super().__init__(service="ocr", message=message)


class ThreatIntelError(ExternalServiceError):
    def __init__(self, source: str, message: str = "Threat intel source unavailable"):
        super().__init__(service=f"threat_intel:{source}", message=message)
