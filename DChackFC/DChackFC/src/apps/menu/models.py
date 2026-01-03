from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.users.models import VendorProfile

class Category(models.Model):
    """Food category model."""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')
        
    def __str__(self):
        return self.name

class MenuItem(models.Model):
    """Menu item model."""
    vendor = models.ForeignKey(
        VendorProfile,
        on_delete=models.CASCADE,
        related_name='menu_items'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='items'
    )
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='menu_items/')
    is_available = models.BooleanField(default=True)
    preparation_time = models.IntegerField(help_text='Preparation time in minutes')
    
    # Dietary information
    is_vegetarian = models.BooleanField(default=False)
    is_vegan = models.BooleanField(default=False)
    is_gluten_free = models.BooleanField(default=False)
    contains_nuts = models.BooleanField(default=False)
    spice_level = models.IntegerField(
        choices=[
            (1, 'Mild'),
            (2, 'Medium'),
            (3, 'Spicy'),
            (4, 'Very Spicy'),
            (5, 'Extra Spicy')
        ],
        default=1
    )
    
    # AI/ML related fields
    popularity_score = models.FloatField(default=0.0)
    recommendation_score = models.FloatField(default=0.0)
    times_ordered = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('menu item')
        verbose_name_plural = _('menu items')
        
    def __str__(self):
        return f"{self.name} - {self.vendor.business_name}"

class MenuItemVariant(models.Model):
    """Model for menu item variations (e.g., size, extras)."""
    menu_item = models.ForeignKey(
        MenuItem,
        on_delete=models.CASCADE,
        related_name='variants'
    )
    name = models.CharField(max_length=100)
    price_adjustment = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    is_available = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = _('menu item variant')
        verbose_name_plural = _('menu item variants')
        
    def __str__(self):
        return f"{self.menu_item.name} - {self.name}"

class SpecialOffer(models.Model):
    """Model for special offers and promotions."""
    vendor = models.ForeignKey(
        VendorProfile,
        on_delete=models.CASCADE,
        related_name='special_offers'
    )
    menu_items = models.ManyToManyField(MenuItem, related_name='offers')
    name = models.CharField(max_length=200)
    description = models.TextField()
    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    # AI/ML related fields
    effectiveness_score = models.FloatField(default=0.0)
    times_used = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = _('special offer')
        verbose_name_plural = _('special offers')
        
    def __str__(self):
        return f"{self.name} - {self.vendor.business_name}"
