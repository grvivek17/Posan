from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """Custom user model for the food court system."""
    
    email = models.EmailField(_('email address'), unique=True)
    phone_number = models.CharField(max_length=15, blank=True)
    dietary_preferences = models.JSONField(default=dict, blank=True)
    is_vendor = models.BooleanField(default=False)
    is_employee = models.BooleanField(default=False)
    
    # Required for using email as username field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.email

class EmployeeProfile(models.Model):
    """Extended profile for employees."""
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='employee_profile'
    )
    employee_id = models.CharField(max_length=50, unique=True)
    department = models.CharField(max_length=100)
    meal_allowance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    allowance_reset_date = models.DateField()

    class Meta:
        verbose_name = _('employee profile')
        verbose_name_plural = _('employee profiles')

    def __str__(self):
        return f"{self.user.email} - {self.employee_id}"

class VendorProfile(models.Model):
    """Extended profile for food vendors."""
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='vendor_profile'
    )
    business_name = models.CharField(max_length=100)
    cuisine_type = models.CharField(max_length=50)
    tax_id = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00
    )
    opening_time = models.TimeField()
    closing_time = models.TimeField()

    class Meta:
        verbose_name = _('vendor profile')
        verbose_name_plural = _('vendor profiles')

    def __str__(self):
        return self.business_name
