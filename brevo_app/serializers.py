from rest_framework import serializers
from .models import Expense, UserProfile
from django.contrib.auth.models import User

# This serializer will translate your UserProfile model
class UserProfileSerializer(serializers.ModelSerializer):
    # Get the email from the related User model
    email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = UserProfile
        # These are the fields that will be sent as JSON
        fields = ['display_name', 'profile_pic_url', 'email']
        # 'display_name' and 'profile_pic_url' can be updated by the app
        # 'email' is read-only
        read_only_fields = ['email']


# This serializer will translate your Expense model
class ExpenseSerializer(serializers.ModelSerializer):
    # We make 'owner' a read-only field.
    # It will be set automatically from the logged-in user in the view.
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Expense
        # These are the fields that will be sent as JSON
        # and that the serializer will look for in incoming JSON
        fields = ['id', 'owner', 'amount', 'category', 'description', 'date']