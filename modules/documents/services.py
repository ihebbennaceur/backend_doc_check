"""
Documents Module - Services
Document lifecycle and storage management
"""

from datetime import timedelta
from django.utils.timezone import now
from shared.constants.theme import DOCUMENT_TYPES, DOCUMENT_STATUS
from shared.utils.helpers import FileUtils, IDGenerator, DateUtils
from shared.exceptions import DocumentError, OCRError, ValidationError
from .models import Document


class DocumentService:
    """Document management and processing"""

    @staticmethod
    def create_document(order_id: str, seller_email: str, document_type: str):
        """Create new document record"""
        doc_config = DOCUMENT_TYPES.get(document_type)
        if not doc_config:
            raise ValidationError("Invalid document type", "document_type")

        doc = Document.objects.create(
            id=IDGenerator.uuid(),
            order_id=order_id,
            seller_email=seller_email,
            document_type=document_type,
            status=DOCUMENT_STATUS["pending"],
        )
        return doc

    @staticmethod
    def upload_document(document_id: str, file_content: bytes, filename: str):
        """Process document upload"""
        if not FileUtils.is_valid_file_type(filename):
            raise ValidationError("Invalid file type", "file")

        if not FileUtils.is_valid_file_size(len(file_content)):
            raise ValidationError("File too large", "file")

        doc = Document.objects.get(id=document_id)
        storage_path = FileUtils.generate_storage_filename(filename, prefix=f"orders/{doc.order_id}")

        # TODO: Upload to Supabase Storage
        doc.file_path = storage_path
        doc.file_size_bytes = len(file_content)
        doc.status = DOCUMENT_STATUS["uploaded"]
        doc.save()

        return doc

    @staticmethod
    def process_ocr(document_id: str):
        """Extract data from document using OCR"""
        doc = Document.objects.get(id=document_id)

        if not doc.file_path:
            raise DocumentError("No file uploaded", document_id)

        try:
            # TODO: Call Mistral OCR API
            ocr_result = {
                "extracted_fields": {},
                "confidence_score": 0.95,
                "processed_at": DateUtils.now().isoformat(),
            }

            doc.ocr_data = ocr_result
            doc.status = DOCUMENT_STATUS["verified"]
            doc.save()

            return doc
        except Exception as e:
            raise OCRError(f"OCR processing failed: {str(e)}", doc.file_path)

    @staticmethod
    def verify_document(document_id: str, issue_date: str = None, expiry_date: str = None):
        """Manually verify document and set validity dates"""
        doc = Document.objects.get(id=document_id)

        if issue_date:
            doc.issue_date = issue_date
        if expiry_date:
            doc.expiry_date = expiry_date

        doc.status = DOCUMENT_STATUS["complete"]
        doc.verification_status = True
        doc.save()

        return doc

    @staticmethod
    def get_documents_by_order(order_id: str) -> list:
        """Retrieve all documents for an order"""
        return Document.objects.filter(order_id=order_id).all()

    @staticmethod
    def check_expiring_documents(days_threshold: int = 30):
        """Find documents expiring within threshold"""
        future_date = now() + timedelta(days=days_threshold)
        return Document.objects.filter(
            expiry_date__lt=future_date,
            expiry_date__gte=now(),
            status__ne=DOCUMENT_STATUS["expired"],
        )

    @staticmethod
    def mark_expired_documents():
        """Update status of expired documents (run via cron)"""
        expired = Document.objects.filter(expiry_date__lt=now(), status__ne=DOCUMENT_STATUS["expired"])
        for doc in expired:
            doc.mark_expired()
