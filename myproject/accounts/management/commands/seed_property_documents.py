"""
Django management command to seed property document templates
Usage: python manage.py seed_property_documents
"""
from django.core.management.base import BaseCommand
from accounts.models import PropertyDocumentTemplate


class Command(BaseCommand):
    help = 'Seed property document templates required for house sale'

    def handle(self, *args, **options):
        documents = [
            {
                'name': 'Property Deed',
                'description': 'Proof of ownership of the property',
                'category': PropertyDocumentTemplate.DocumentCategory.PROPERTY,
                'required': True,
                'required_fields': ['owner_name', 'property_address', 'deed_date', 'property_id'],
                'order': 1
            },
            {
                'name': 'Property Survey',
                'description': 'Latest property survey/blueprint showing property boundaries',
                'category': PropertyDocumentTemplate.DocumentCategory.PROPERTY,
                'required': True,
                'required_fields': ['survey_date', 'property_dimensions', 'surveyor_name'],
                'order': 2
            },
            {
                'name': 'Building Permit',
                'description': 'Original building permit and construction authorization',
                'category': PropertyDocumentTemplate.DocumentCategory.LEGAL,
                'required': True,
                'required_fields': ['permit_number', 'issue_date', 'completion_date'],
                'order': 3
            },
            {
                'name': 'Certificate of Occupancy',
                'description': 'Certificate confirming property is safe and ready for occupancy',
                'category': PropertyDocumentTemplate.DocumentCategory.LEGAL,
                'required': True,
                'required_fields': ['certificate_number', 'issue_date'],
                'order': 4
            },
            {
                'name': 'Property Tax Documents',
                'description': 'Latest property tax assessment and payment records',
                'category': PropertyDocumentTemplate.DocumentCategory.TAX,
                'required': True,
                'required_fields': ['tax_id', 'assessed_value', 'last_payment_date'],
                'order': 5
            },
            {
                'name': 'Mortgage Documents',
                'description': 'Current mortgage statements (if applicable)',
                'category': PropertyDocumentTemplate.DocumentCategory.FINANCIAL,
                'required': False,
                'required_fields': ['loan_number', 'lender_name', 'remaining_balance'],
                'order': 6
            },
            {
                'name': 'Home Inspection Report',
                'description': 'Recent home inspection report (if available)',
                'category': PropertyDocumentTemplate.DocumentCategory.INSPECTION,
                'required': False,
                'required_fields': ['inspection_date', 'inspector_name', 'property_condition'],
                'order': 7
            },
            {
                'name': 'Utility Statements',
                'description': 'Recent utility bills (electric, water, gas)',
                'category': PropertyDocumentTemplate.DocumentCategory.PROPERTY,
                'required': False,
                'required_fields': ['account_numbers', 'monthly_costs'],
                'order': 8
            },
            {
                'name': 'HOA Documents',
                'description': 'HOA bylaws and fee statements (if applicable)',
                'category': PropertyDocumentTemplate.DocumentCategory.LEGAL,
                'required': False,
                'required_fields': ['hoa_name', 'monthly_fees'],
                'order': 9
            },
            {
                'name': 'Insurance Documents',
                'description': 'Current homeowners insurance policy',
                'category': PropertyDocumentTemplate.DocumentCategory.FINANCIAL,
                'required': False,
                'required_fields': ['policy_number', 'coverage_amount', 'insurance_company'],
                'order': 10
            },
        ]
        
        created_count = 0
        for doc in documents:
            obj, created = PropertyDocumentTemplate.objects.get_or_create(
                name=doc['name'],
                defaults={
                    'description': doc['description'],
                    'category': doc['category'],
                    'required': doc['required'],
                    'required_fields': doc['required_fields'],
                    'order': doc['order']
                }
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created: {doc["name"]}')
                )
            else:
                self.stdout.write(f'- Already exists: {doc["name"]}')
        
        self.stdout.write(
            self.style.SUCCESS(f'\n✅ Successfully created {created_count} property document templates')
        )
