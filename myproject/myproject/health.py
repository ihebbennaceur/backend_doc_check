from django.http import JsonResponse
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt

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
