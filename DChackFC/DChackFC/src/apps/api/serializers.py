from rest_framework import serializers
from apps.menu.models import MenuItem, Category, MenuItemVariant, SpecialOffer
from apps.orders.models import Order, OrderItem
from apps.users.models import VendorProfile

class MenuItemVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItemVariant
        fields = ['id', 'name', 'price_adjustment', 'is_available']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'image', 'is_active']

class MenuItemSerializer(serializers.ModelSerializer):
    variants = MenuItemVariantSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    vendor_name = serializers.CharField(source='vendor.business_name', read_only=True)
    
    class Meta:
        model = MenuItem
        fields = [
            'id', 'name', 'description', 'price', 'image', 'is_available',
            'preparation_time', 'is_vegetarian', 'is_vegan', 'is_gluten_free',
            'contains_nuts', 'spice_level', 'popularity_score', 
            'recommendation_score', 'category_name', 'vendor_name', 'variants'
        ]

class OrderItemSerializer(serializers.ModelSerializer):
    menu_item_name = serializers.CharField(source='menu_item.name', read_only=True)
    variant_name = serializers.CharField(source='variant.name', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'menu_item', 'menu_item_name', 'variant', 'variant_name',
            'quantity', 'unit_price', 'total_price', 'special_instructions',
            'is_prepared', 'preparation_started_at', 'preparation_completed_at'
        ]

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    vendor_name = serializers.CharField(source='vendor.business_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'user', 'user_email', 'vendor', 'vendor_name',
            'status', 'total_amount', 'special_instructions', 'is_preorder',
            'scheduled_for', 'queue_number', 'estimated_waiting_time',
            'payment_status', 'payment_method', 'payment_id',
            'employee_benefit_used', 'benefit_amount_used', 'items',
            'created_at', 'updated_at', 'completed_at'
        ]
        read_only_fields = [
            'order_number', 'user', 'total_amount', 'queue_number',
            'estimated_waiting_time', 'payment_status', 'payment_id',
            'employee_benefit_used', 'benefit_amount_used',
            'created_at', 'updated_at', 'completed_at'
        ]

class OrderItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = [
            'menu_item', 'variant', 'quantity', 'special_instructions'
        ]

class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemCreateSerializer(many=True)
    use_employee_benefit = serializers.BooleanField(default=False)
    
    class Meta:
        model = Order
        fields = [
            'vendor', 'items', 'special_instructions', 'is_preorder',
            'scheduled_for', 'payment_method', 'use_employee_benefit'
        ]
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        use_employee_benefit = validated_data.pop('use_employee_benefit', False)
        
        # Create order
        order = Order.objects.create(**validated_data)
        
        # Create order items
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
        
        return order

class SpecialOfferSerializer(serializers.ModelSerializer):
    vendor_name = serializers.CharField(source='vendor.business_name', read_only=True)
    menu_items = MenuItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = SpecialOffer
        fields = [
            'id', 'vendor', 'vendor_name', 'menu_items', 'name', 'description',
            'discount_percentage', 'discount_amount', 'start_date', 'end_date',
            'is_active', 'effectiveness_score', 'times_used'
        ]
