from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions
from rest_framework.filters import SearchFilter, OrderingFilter
from core_models.permissions import IsOwnerOrReadOnly
from .models import Vacancy


class VacancyViewSet(viewsets.ModelViewSet):
    queryset = Vacancy.objects.select_related('owner', 'category').prefetch_related('skills')
    serializer_class = VacancySerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'experience_required', 'location', 'salary_min']
    search_fields = ['title', 'description', 'owner__username']
    ordering_fields = ['created_at', 'salary_min']

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
