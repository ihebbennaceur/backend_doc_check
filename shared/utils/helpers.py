"""
Utility functions and helpers for Fizbo platform
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class DateUtils:
    """Date and time utilities"""

    @staticmethod
    def now() -> datetime:
        """Get current datetime in UTC"""
        return datetime.utcnow()

    @staticmethod
    def add_months(date: datetime, months: int) -> datetime:
        """Add months to a date"""
        month = date.month - 1 + months
        year = date.year + month // 12
        month = month % 12 + 1
        day = min(date.day, [31, 29 if year % 4 == 0 else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])
        return date.replace(year=year, month=month, day=day)

    @staticmethod
    def is_expired(expiry_date: datetime) -> bool:
        """Check if a date has expired"""
        return datetime.utcnow() > expiry_date

    @staticmethod
    def days_until_expiry(expiry_date: datetime) -> int:
        """Get number of days until expiry"""
        delta = expiry_date - datetime.utcnow()
        return max(0, delta.days)


class IDGenerator:
    """ID generation utilities"""

    @staticmethod
    def uuid() -> str:
        """Generate UUID"""
        return str(uuid.uuid4())

    @staticmethod
    def short_id() -> str:
        """Generate short alphanumeric ID (12 chars)"""
        return str(uuid.uuid4()).replace("-", "")[:12]

    @staticmethod
    def order_id() -> str:
        """Generate order ID (FIZ-TIMESTAMP-SHORT)"""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        short = IDGenerator.short_id()[:6]
        return f"FIZ-{timestamp}-{short}"


class ResponseUtils:
    """API response utilities"""

    @staticmethod
    def success(data: Any = None, message: str = "Success", status_code: int = 200) -> Dict:
        """Success response"""
        return {
            "status": "success",
            "code": status_code,
            "message": message,
            "data": data,
        }

    @staticmethod
    def error(message: str, code: str = None, status_code: int = 400, details: Dict = None) -> Dict:
        """Error response"""
        return {
            "status": "error",
            "code": status_code,
            "error_code": code,
            "message": message,
            "details": details or {},
        }

    @staticmethod
    def paginated(items: list, total: int, page: int, page_size: int) -> Dict:
        """Paginated response"""
        total_pages = (total + page_size - 1) // page_size
        return {
            "items": items,
            "pagination": {
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1,
            },
        }


class ValidationUtils:
    """Input validation utilities"""

    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        import re

        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(pattern, email) is not None

    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate Portuguese phone number"""
        import re

        # Portuguese phone: +351 or 0, followed by 9 digits
        pattern = r"^(\+351|0)?9[1-9]\d{7}$"
        return re.match(pattern, phone.replace(" ", "").replace("-", "")) is not None

    @staticmethod
    def validate_nif(nif: str) -> bool:
        """Validate Portuguese NIF (VAT number)"""
        import re

        if not re.match(r"^\d{9}$", nif):
            return False

        weights = [9, 8, 7, 6, 5, 4, 3, 2]
        total = sum(int(nif[i]) * weights[i] for i in range(8))
        check = (10 - (total % 10)) % 10
        return int(nif[8]) == check

    @staticmethod
    def sanitize_string(value: str, max_length: int = None) -> str:
        """Sanitize string input"""
        value = value.strip()
        if max_length:
            value = value[:max_length]
        return value


class FileUtils:
    """File handling utilities"""

    ALLOWED_DOCUMENT_TYPES = {"pdf", "jpg", "jpeg", "png"}
    MAX_FILE_SIZE_MB = 25

    @staticmethod
    def is_valid_file_type(filename: str) -> bool:
        """Check if file type is allowed"""
        ext = filename.rsplit(".", 1)[1].lower() if "." in filename else ""
        return ext in FileUtils.ALLOWED_DOCUMENT_TYPES

    @staticmethod
    def is_valid_file_size(file_size_bytes: int) -> bool:
        """Check if file size is within limit"""
        max_bytes = FileUtils.MAX_FILE_SIZE_MB * 1024 * 1024
        return file_size_bytes <= max_bytes

    @staticmethod
    def get_file_extension(filename: str) -> str:
        """Get file extension"""
        return filename.rsplit(".", 1)[1].lower() if "." in filename else ""

    @staticmethod
    def generate_storage_filename(original_filename: str, prefix: str = "") -> str:
        """Generate unique storage filename"""
        ext = FileUtils.get_file_extension(original_filename)
        unique_id = IDGenerator.short_id()
        if prefix:
            return f"{prefix}/{unique_id}.{ext}"
        return f"{unique_id}.{ext}"


class LoggingUtils:
    """Logging utilities"""

    @staticmethod
    def log_action(action: str, user_id: str = None, details: Dict = None):
        """Log platform action"""
        log_data = {
            "action": action,
            "timestamp": DateUtils.now().isoformat(),
            "user_id": user_id,
            "details": details or {},
        }
        logger.info(f"ACTION: {log_data}")

    @staticmethod
    def log_error(error: Exception, context: Dict = None):
        """Log error with context"""
        logger.error(
            f"ERROR: {str(error)}",
            extra={"error": str(error), "context": context or {}},
            exc_info=True,
        )
