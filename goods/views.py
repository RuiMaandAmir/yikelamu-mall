from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import Category, Goods
from .serializers import (
    CategorySerializer,
    GoodsListSerializer,
    GoodsDetailSerializer
)

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """商品分类视图集"""
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    pagination_class = None

class GoodsViewSet(viewsets.ReadOnlyModelViewSet):
    """商品视图集"""
    serializer_class = GoodsListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'sales', 'created_at']
    filterset_fields = ['category', 'is_on_sale']

    def get_queryset(self):
        queryset = Goods.objects.filter(is_on_sale=True)
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
            
        return queryset

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return GoodsDetailSerializer
        return GoodsListSerializer

    @action(detail=False, methods=['get'])
    def hot(self, request):
        """热销商品"""
        queryset = self.get_queryset().order_by('-sales')[:10]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def new(self, request):
        """新品上架"""
        queryset = self.get_queryset().order_by('-created_at')[:10]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def recommend(self, request):
        """推荐商品"""
        # 这里可以根据用户的浏览历史、购买记录等进行个性化推荐
        queryset = self.get_queryset().order_by('?')[:10]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def similar(self, request, pk=None):
        """相似商品"""
        goods = self.get_object()
        queryset = self.get_queryset().filter(
            Q(category=goods.category) & ~Q(id=goods.id)
        )[:5]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)