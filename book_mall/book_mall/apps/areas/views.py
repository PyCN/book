from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework_extensions.cache.mixins import CacheResponseMixin

from .models import Area
from .serializers import AreasSerializer, SubAreaSerializer


class AreasViewSet(CacheResponseMixin, ReadOnlyModelViewSet):
    pagination_class = None

    def get_serializer_class(self):
        if self.action == 'list':
            return AreasSerializer
        else:
            return SubAreaSerializer

    def get_queryset(self):
        if self.action == 'list':
            return Area.objects.filter(parent=None).all()
        else:
            return Area.objects.all()