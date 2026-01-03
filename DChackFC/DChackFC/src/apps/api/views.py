from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q
from django.core.cache import cache

from apps.menu.models import MenuItem, Category, SpecialOffer
from apps.orders.models import Order, OrderItem
from .serializers import (
    MenuItemSerializer,
    CategorySerializer,
    OrderSerializer,
    OrderCreateSerializer
)
from core.ml.menu_recommender import MenuRecommender

class MenuItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing menu items.
    """
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Cache key based on query parameters
        cache_key = f'menu_items_{self.request.query_params}'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        # Filter by vendor
        vendor_id = self.request.query_params.get('vendor_id')
        if vendor_id:
            queryset = queryset.filter(vendor_id=vendor_id)
            
        # Filter by category
        category_id = self.request.query_params.get('category_id')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
            
        # Filter by dietary preferences
        if self.request.query_params.get('vegetarian'):
            queryset = queryset.filter(is_vegetarian=True)
        if self.request.query_params.get('vegan'):
            queryset = queryset.filter(is_vegan=True)
        if self.request.query_params.get('gluten_free'):
            queryset = queryset.filter(is_gluten_free=True)
            
        # Filter by availability
        if self.request.query_params.get('available'):
            queryset = queryset.filter(is_available=True)
            
        # Cache the results for 5 minutes
        cache.set(cache_key, queryset, 300)
        return queryset
        
    @action(detail=False, methods=['get'])
    def recommendations(self, request):
        """Get personalized menu recommendations."""
        user = request.user
        if not user.is_authenticated:
            return Response(
                {"error": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED
            )
            
        try:
            recommender = MenuRecommender()
            recommendations = recommender.get_recommendations(
                user_id=user.id,
                user_preferences=user.dietary_preferences,
                current_time=timezone.now(),
                available_items=self.get_queryset().filter(is_available=True)
            )
            
            serializer = self.get_serializer(recommendations, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing orders.
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.is_vendor:
            return Order.objects.filter(vendor=user.vendor_profile)
        return Order.objects.filter(user=user)
    
    def perform_create(self, serializer):
        # Calculate order details
        items_data = self.request.data.get('items', [])
        total_amount = 0
        for item in items_data:
            menu_item = MenuItem.objects.get(id=item['menu_item_id'])
            quantity = item['quantity']
            total_amount += menu_item.price * quantity
            
        # Apply employee benefits if applicable
        if self.request.data.get('use_employee_benefit'):
            employee = self.request.user.employee_profile
            if employee.meal_allowance > 0:
                benefit_amount = min(employee.meal_allowance, total_amount)
                total_amount -= benefit_amount
                employee.meal_allowance -= benefit_amount
                employee.save()
                
        # Create order
        order = serializer.save(
            user=self.request.user,
            total_amount=total_amount
        )
        
        # Create order items
        for item in items_data:
            menu_item = MenuItem.objects.get(id=item['menu_item_id'])
            OrderItem.objects.create(
                order=order,
                menu_item=menu_item,
                quantity=item['quantity'],
                unit_price=menu_item.price,
                total_price=menu_item.price * item['quantity'],
                special_instructions=item.get('special_instructions', '')
            )
            
        return order
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update order status."""
        order = self.get_object()
        new_status = request.data.get('status')
        if not new_status:
            return Response(
                {"error": "Status not provided"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        order.status = new_status
        order.save()
        
        # Update order history
        order.history.create(
            status=new_status,
            notes=request.data.get('notes', '')
        )
        
        return Response(self.get_serializer(order).data)
    
    @action(detail=True, methods=['get'])
    def queue_status(self, request, pk=None):
        """Get order's position in queue and estimated wait time."""
        order = self.get_object()
        queue_position = Order.objects.filter(
            vendor=order.vendor,
            created_at__lt=order.created_at,
            status__in=['pending', 'confirmed', 'preparing']
        ).count() + 1
        
        # Estimate wait time based on queue position and item preparation times
        total_prep_time = sum(
            item.menu_item.preparation_time * item.quantity
            for item in order.items.all()
        )
        
        estimated_wait = total_prep_time + (queue_position * 5)  # 5 min buffer per order
        
        return Response({
            'queue_position': queue_position,
            'estimated_wait_time': estimated_wait,
            'status': order.status
        })
