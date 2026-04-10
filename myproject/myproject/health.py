from django.http import JsonResponse
from django.urls import get_resolver
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@api_view(['GET'])
def api_root(request):
    """Root API endpoint that lists all available endpoints."""
    return JsonResponse({
        'service': 'Seller Platform Backend API',
        'version': '1.0.0',
        'status': 'running',
        'documentation': {
            'swagger_ui': 'https://backenddoccheck-production.up.railway.app/api/docs/',
            'redoc': 'https://backenddoccheck-production.up.railway.app/api/redoc/',
            'openapi_schema': 'https://backenddoccheck-production.up.railway.app/api/schema/'
        },
        'endpoints': {
            'authentication': {
                'obtain_token': '/api/token/',
                'refresh_token': '/api/token/refresh/'
            },
            'accounts': {
                'users': '/api/user/',
                'profile': '/api/accounts/'
            },
            'documents': {
                'list': '/api/documents/',
                'upload': '/api/documents/upload/'
            },
            'verification': {
                'doccheck': '/api/doccheck/'
            },
            'orders': {
                'orders': '/api/orders/'
            },
            'payments': {
                'payments': '/api/payments/'
            },
            'admin_panel': '/admin/'
        },
        'health': {
            'health_check': '/health/',
            'ready_check': '/ready/'
        }
    })

@csrf_exempt
@api_view(['GET'])
def health_check(request):
    """Health check endpoint that doesn't require database access."""
    return JsonResponse({
        'status': 'ok',
        'message': 'Backend is running',
        'service': 'backend_doc_check'
    })

@csrf_exempt
@api_view(['GET'])
def ready_check(request):
    """Readiness check - verifies database connection."""
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return JsonResponse({'ready': True, 'database': 'connected'})
    except Exception as e:
        return JsonResponse({
            'ready': False,
            'database': 'disconnected',
            'error': str(e)
        }, status=503)
