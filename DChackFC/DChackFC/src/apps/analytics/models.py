from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.users.models import VendorProfile
from apps.menu.models import MenuItem

class VendorAnalytics(models.Model):
    """Store vendor performance analytics."""
    vendor = models.ForeignKey(
        VendorProfile,
        on_delete=models.CASCADE,
        related_name='analytics'
    )
    date = models.DateField()
    total_orders = models.IntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2)
    average_order_value = models.DecimalField(max_digits=10, decimal_places=2)
    peak_hour_start = models.TimeField()
    peak_hour_end = models.TimeField()
    peak_hour_orders = models.IntegerField(default=0)
    customer_satisfaction = models.FloatField(default=0.0)
    average_preparation_time = models.IntegerField(help_text='Average preparation time in minutes')
    order_completion_rate = models.FloatField(default=0.0)
    
    class Meta:
        verbose_name = _('vendor analytics')
        verbose_name_plural = _('vendor analytics')
        unique_together = ['vendor', 'date']
        
    def __str__(self):
        return f"{self.vendor.business_name} - {self.date}"

class ItemAnalytics(models.Model):
    """Store menu item performance analytics."""
    menu_item = models.ForeignKey(
        MenuItem,
        on_delete=models.CASCADE,
        related_name='analytics'
    )
    date = models.DateField()
    orders_count = models.IntegerField(default=0)
    revenue = models.DecimalField(max_digits=10, decimal_places=2)
    average_rating = models.FloatField(default=0.0)
    preparation_time_avg = models.IntegerField(help_text='Average preparation time in minutes')
    waste_percentage = models.FloatField(default=0.0)
    profit_margin = models.FloatField(default=0.0)
    
    # AI-generated metrics
    demand_forecast = models.IntegerField(default=0)
    optimal_price = models.DecimalField(max_digits=10, decimal_places=2)
    recommendation_score = models.FloatField(default=0.0)
    
    class Meta:
        verbose_name = _('item analytics')
        verbose_name_plural = _('item analytics')
        unique_together = ['menu_item', 'date']
        
    def __str__(self):
        return f"{self.menu_item.name} - {self.date}"

class CustomerFeedback(models.Model):
    """Store and analyze customer feedback."""
    RATING_CHOICES = [
        (1, 'Very Poor'),
        (2, 'Poor'),
        (3, 'Average'),
        (4, 'Good'),
        (5, 'Excellent')
    ]
    
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name='feedback'
    )
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # AI-generated analysis
    sentiment_score = models.FloatField(null=True)
    feedback_categories = models.JSONField(default=dict)
    priority_level = models.IntegerField(default=0)
    requires_attention = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = _('customer feedback')
        verbose_name_plural = _('customer feedback')
        
    def __str__(self):
        return f"Feedback for Order {self.order.order_number}"

class PeakHourPrediction(models.Model):
    """Store predictions for peak hours and required resources."""
    vendor = models.ForeignKey(
        VendorProfile,
        on_delete=models.CASCADE,
        related_name='peak_predictions'
    )
    date = models.DateField()
    hour = models.IntegerField()
    predicted_orders = models.IntegerField()
    predicted_revenue = models.DecimalField(max_digits=10, decimal_places=2)
    confidence_score = models.FloatField()
    recommended_staff = models.IntegerField()
    
    # Weather and event factors
    temperature = models.FloatField(null=True)
    weather_condition = models.CharField(max_length=50, blank=True)
    is_special_event = models.BooleanField(default=False)
    event_description = models.CharField(max_length=200, blank=True)
    
    class Meta:
        verbose_name = _('peak hour prediction')
        verbose_name_plural = _('peak hour predictions')
        unique_together = ['vendor', 'date', 'hour']
        
    def __str__(self):
        return f"{self.vendor.business_name} - {self.date} Hour {self.hour}"

class InventoryPrediction(models.Model):
    """Store inventory requirement predictions."""
    menu_item = models.ForeignKey(
        MenuItem,
        on_delete=models.CASCADE,
        related_name='inventory_predictions'
    )
    date = models.DateField()
    predicted_demand = models.IntegerField()
    recommended_stock = models.IntegerField()
    min_stock_level = models.IntegerField()
    max_stock_level = models.IntegerField()
    confidence_score = models.FloatField()
    
    # Cost optimization
    optimal_order_quantity = models.IntegerField()
    estimated_wastage = models.FloatField()
    estimated_storage_cost = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = _('inventory prediction')
        verbose_name_plural = _('inventory predictions')
        unique_together = ['menu_item', 'date']
        
    def __str__(self):
        return f"{self.menu_item.name} - {self.date}"
