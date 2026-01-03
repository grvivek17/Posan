from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from apps.menu.models import MenuItem, MenuItemVariant
from apps.users.models import VendorProfile

class Order(models.Model):
    """Order model for food court orders."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('preparing', 'Preparing'),
        ('ready', 'Ready for Pickup'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded')
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='orders'
    )
    vendor = models.ForeignKey(
        VendorProfile,
        on_delete=models.SET_NULL,
        null=True,
        related_name='orders'
    )
    
    # Order details
    order_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    special_instructions = models.TextField(blank=True)
    is_preorder = models.BooleanField(default=False)
    scheduled_for = models.DateTimeField(null=True, blank=True)
    
    # Queue management
    queue_number = models.IntegerField(null=True, blank=True)
    estimated_waiting_time = models.IntegerField(
        help_text='Estimated waiting time in minutes',
        null=True,
        blank=True
    )
    
    # Payment information
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending'
    )
    payment_method = models.CharField(max_length=50)
    payment_id = models.CharField(max_length=100, blank=True)
    
    # Employee benefit tracking
    employee_benefit_used = models.BooleanField(default=False)
    benefit_amount_used = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # AI/ML related fields
    priority_score = models.FloatField(default=0.0)
    complexity_score = models.FloatField(default=0.0)
    
    class Meta:
        verbose_name = _('order')
        verbose_name_plural = _('orders')
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Order {self.order_number} - {self.user.email}"

class OrderItem(models.Model):
    """Individual items within an order."""
    
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    menu_item = models.ForeignKey(
        MenuItem,
        on_delete=models.SET_NULL,
        null=True,
        related_name='order_items'
    )
    variant = models.ForeignKey(
        MenuItemVariant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='order_items'
    )
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    special_instructions = models.TextField(blank=True)
    
    # Preparation tracking
    is_prepared = models.BooleanField(default=False)
    preparation_started_at = models.DateTimeField(null=True, blank=True)
    preparation_completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = _('order item')
        verbose_name_plural = _('order items')
        
    def __str__(self):
        return f"{self.quantity}x {self.menu_item.name}"

class OrderHistory(models.Model):
    """Track order status changes for analysis."""
    
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='history'
    )
    status = models.CharField(max_length=20, choices=Order.STATUS_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        verbose_name = _('order history')
        verbose_name_plural = _('order histories')
        ordering = ['-timestamp']
        
    def __str__(self):
        return f"{self.order.order_number} - {self.status}"
