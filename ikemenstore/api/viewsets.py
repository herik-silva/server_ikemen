from rest_framework import viewsets
from ikemenstore.api import serializers
from ikemenstore import models

from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.response import Response
from rest_framework import status

from rest_framework.views import APIView
from rest_framework.permissions import BasePermission

class CustomSearchFilter(SearchFilter):

    def get_search_terms(self, request):
        """
        Search terms are set by a ?search=... query parameter,
        and may be comma delimited.
        """
        params = request.query_params.get(self.search_param, '')
        params = params.replace('\x00', '')

        return params.split(',')


class IsOwnerOrReadOnly(BasePermission):
    """
    Custom permission to only allow owners of an object to view it.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True

        return obj.user == request.user

class UserClientViewSet(viewsets.ModelViewSet):
    queryset = models.UserClient.objects.all()
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'update':
            return serializers.UserClientUpdateSerializer
        elif self.action == 'destroy':
            return serializers.UserClientDeleteSerializer
        else:
            return serializers.GetUserClientSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        userClientDeleteSerializer = self.get_serializer_class()(instance)

        userClientDeleteSerializer.delete(instance)

        return Response({"message": "conta excluído com sucesso!"}, status=status.HTTP_204_NO_CONTENT)
    
    
class UserRegistrationViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.UserClientSerializer
    queryset = models.UserClient.objects.none()
    permission_classes = [AllowAny]

class CharactersViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.CharactersSerializer
    queryset = models.Characters.objects.all()

    filter_backends = [DjangoFilterBackend, CustomSearchFilter, OrderingFilter]
    filterset_fields = {
        'creator':['exact'],
    }
    search_fields = ['^name']
    ordering_fields = ['name']

    
class ImageViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.Image
    queryset = models.Image.objects.all()

class SaleViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.SaleSerializer
    queryset = models.Sale.objects.all()
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    # Consulta apenas as vendas do usuário que requisitou.
    def get_queryset(self):
        return self.queryset.filter(buyer__user=self.request.user)
    
    # Listar apenas vendas completas Rota: /sales/completed_sales/
    @action(detail=False, methods=['GET'])
    def completed_sales(self, request):
        completed_sales = self.queryset.filter(payment_done=True, buyer__user=request.user)
        serializer = self.get_serializer(completed_sales, many=True)
        
        return Response(serializer.data)