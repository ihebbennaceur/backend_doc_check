"""
Admin endpoint to list all pending document submissions
"""
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import SellerDocumentSubmission
from .serializers import SellerDocumentSubmissionDetailSerializer


class AdminPropertyDocumentsListView(ListAPIView):
    """Admin endpoint to list all property document submissions for review"""
    serializer_class = SellerDocumentSubmissionDetailSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get_queryset(self):
        # Get filter from query params
        status = self.request.query_params.get('status', None)
        
        queryset = SellerDocumentSubmission.objects.all()
        
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset.order_by('-submitted_at')
