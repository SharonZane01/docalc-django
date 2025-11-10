# In brevo_app/models.py
from django.db import models
from django.contrib.auth.models import User

# ... your other models (if any) ...

class Expense(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="expenses")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'{self.owner.username} - {self.category} - {self.amount}'
    
class UserProfile(models.Model):
    # This links the profile to a specific User.
    # OneToOneField means one user can only have one profile.
    # on_delete=models.CASCADE means if the user is deleted, delete their profile too.
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # This is the name the user wants to be called
    display_name = models.CharField(max_length=100, blank=True, null=True)
    
    # We'll just store the URL to the image, not the image itself.
    profile_pic_url = models.URLField(max_length=500, blank=True, null=True)

    def __str__(self):
        # This is what will show up in the Django admin
        return f"{self.user.username}'s Profile"    