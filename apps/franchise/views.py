"""
Franchise application views
"""
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from apps.franchise.models import FranchiseApplication
from .serializers import (
    FranchiseApplicationSerializer,
    FranchiseApplicationCreateSerializer,
    FranchiseApplicationListSerializer
)
from .permissions import FranchiseApplicationPermission


class FranchiseApplicationCreateView(generics.CreateAPIView):
    """
    Public endpoint for creating franchise applications
    Anyone can submit an application
    """
    queryset = FranchiseApplication.objects.all()
    serializer_class = FranchiseApplicationCreateSerializer
    permission_classes = [FranchiseApplicationPermission]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        application = serializer.save()
        
        # Return success response with application ID
        return Response({
            'message': 'Franchise application submitted successfully',
            'application_id': application.id,
            'status': 'pending'
        }, status=status.HTTP_201_CREATED)


class FranchiseApplicationListView(generics.ListAPIView):
    """
    Admin-only endpoint for listing all franchise applications
    """
    queryset = FranchiseApplication.objects.all()
    serializer_class = FranchiseApplicationListSerializer
    permission_classes = [FranchiseApplicationPermission]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    
    # Filtering options
    filterset_fields = ['status', 'city']
    search_fields = ['full_name', 'phone', 'email', 'city']
    ordering_fields = ['created_at', 'updated_at', 'investment_amount', 'full_name']
    ordering = ['-created_at']

    def get_queryset(self):
        """Optionally filter by status or other parameters"""
        queryset = FranchiseApplication.objects.all()
        
        # Additional filtering logic can be added here
        return queryset


class FranchiseApplicationDetailView(generics.RetrieveAPIView):
    """
    Admin-only endpoint for viewing franchise application details
    """
    queryset = FranchiseApplication.objects.all()
    serializer_class = FranchiseApplicationSerializer
    permission_classes = [FranchiseApplicationPermission]
    lookup_field = 'id'


class FranchiseApplicationUpdateView(generics.UpdateAPIView):
    """
    Admin-only endpoint for updating franchise applications
    Typically used for changing status
    """
    queryset = FranchiseApplication.objects.all()
    serializer_class = FranchiseApplicationSerializer
    permission_classes = [FranchiseApplicationPermission]
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        # Log status changes
        old_status = instance.status
        self.perform_update(serializer)
        new_status = serializer.instance.status
        
        response_data = serializer.data
        if old_status != new_status:
            response_data['message'] = f'Application status changed from {old_status} to {new_status}'
        
        return Response(response_data)


class FranchiseApplicationDeleteView(generics.DestroyAPIView):
    """
    Admin-only endpoint for deleting franchise applications
    """
    queryset = FranchiseApplication.objects.all()
    permission_classes = [FranchiseApplicationPermission]
    lookup_field = 'id'

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        application_id = instance.id
        self.perform_destroy(instance)
        
        return Response({
            'message': f'Franchise application {application_id} deleted successfully'
        }, status=status.HTTP_200_OK)
