from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
import random
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from .models import Expense
from django.contrib.auth.decorators import login_required

# --- NEW IMPORTS (Cache for OTP, DRF for Tokens) ---
from django.core.cache import cache
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
import datetime 
from .models import Expense, UserProfile

# --- 👇 1. IMPORT YOUR NEW SERIALIZERS ---
from .serializers import ExpenseSerializer, UserProfileSerializer


# --- This view remains the same ---
@csrf_exempt
def signup_view(request):
    if request.method == 'POST':
        data = {}
        
        if 'application/json' in request.headers.get('Content-Type', ''):
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({'message': 'Invalid JSON'}, status=400)
        else:
            data = request.POST
        
        email = data.get('email')
        password = data.get('password')
        display_name = data.get('display_name') 

        if not email or not password or not display_name:
            return JsonResponse({'message': 'Email, password, and display name are required'}, status=400)

        if User.objects.filter(username=email).exists():
            return JsonResponse({'message': 'An account with this email already exists.'}, status=409)

        otp = random.randint(100000, 999999)
        subject = 'Your Account Verification OTP'
        message = f'Your OTP is: {otp}. It is valid for 10 minutes.'
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
        except Exception as e:
            return JsonResponse({'message': f'Failed to send OTP email. Error: {e}'}, status=500)

        cache.set(f'signup_data_for_{email}', {
            'email': email, 
            'password': password, 
            'display_name': display_name 
        }, timeout=600)
        cache.set(f'signup_otp_for_{email}', otp, timeout=600)
        
        return JsonResponse({'message': 'An OTP has been sent to your email.'}, status=200)

    return render(request, 'signup.html')


# --- 👇 2. VIEW UPDATED WITH SERIALIZER ---
@api_view(['GET', 'POST'])
@authentication_classes([TokenAuthentication]) 
@permission_classes([IsAuthenticated]) 
def expense_view(request):
    
    if request.method == 'GET':
        expenses = Expense.objects.filter(owner=request.user).order_by('-date')
        # Use the serializer to convert the list of objects to JSON
        serializer = ExpenseSerializer(expenses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == 'POST':
        # Use the serializer to validate incoming JSON data
        serializer = ExpenseSerializer(data=request.data)
        
        # serializer.is_valid() checks for required fields and data types
        if serializer.is_valid():
            # Save the new expense, linking it to the logged-in user
            serializer.save(owner=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        # If data is invalid, send back the errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# --- This view remains the same ---
@csrf_exempt
def verify_otp_view(request):
    if request.method == 'POST':
        data = {}
        if 'application/json' in request.headers.get('Content-Type', ''):
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({'message': 'Invalid JSON'}, status=400)
        else:
            data = request.POST
        
        email = data.get('email')
        submitted_otp = data.get('otp')
        
        if not email:
            return JsonResponse({'message': 'Email missing.'}, status=400)
        
        signup_otp = cache.get(f'signup_otp_for_{email}')
        signup_data = cache.get(f'signup_data_for_{email}')

        if not signup_otp or not signup_data:
            return JsonResponse({'message': 'Your verification session has expired.'}, status=400)

        if signup_data.get('email') != email:
             return JsonResponse({'message': 'Email mismatch. Please try again.'}, status=400)

        if str(signup_otp) == submitted_otp:
            user = User.objects.create_user(
                username=signup_data['email'],
                email=signup_data['email'],
                password=signup_data['password']
            )
            
            UserProfile.objects.create(
                user=user,
                display_name=signup_data.get('display_name') # Get name from cache
            )
            
            cache.delete(f'signup_data_for_{email}')
            cache.delete(f'signup_otp_for_{email}')
            
            token, created = Token.objects.get_or_create(user=user)
            
            return JsonResponse({
                'message': 'Account verified successfully!',
                'token': token.key, 
                'email': user.email
            }, status=200)
        else:
            return JsonResponse({'message': 'Invalid or expired OTP.'}, status=400)

    return render(request, 'verify_otp.html')


# This is a web-only view, so it's fine to leave as-is
def dashboard_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'dashboard.html')

# --- This view remains the same ---
@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        data = {}
        if 'application/json' in request.headers.get('Content-Type', ''):
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({'message': 'Invalid JSON'}, status=400)
        else:
            data = request.POST

        email = data.get('email')
        password = data.get('password')
        
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            
            return JsonResponse({
                'message': 'Login successful!',
                'token': token.key, 
                'email': user.email
            }, status=200)
        else:
            return JsonResponse({'message': 'Invalid email or password.'}, status=401)

    return render(request, 'login.html')

# --- This view remains the same ---
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        request.user.auth_token.delete()
        return Response({'message': 'Logged out successfully.'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

# --- 👇 3. DETAIL VIEW UPDATED WITH SERIALIZER ---
@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def expense_detail_view(request, pk):
    """
    Retrieve, update or delete an expense instance.
    """
    expense = get_object_or_404(Expense, pk=pk, owner=request.user)

    if request.method == 'GET':
        # Use the serializer to convert the single object to JSON
        serializer = ExpenseSerializer(expense)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        # Use the serializer to validate the incoming update data
        # We pass 'expense' as the first argument to update this specific instance
        serializer = ExpenseSerializer(expense, data=request.data, partial=True) # partial=True allows updating only some fields
        
        if serializer.is_valid():
            serializer.save() # No need to pass owner, it's already linked
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        try:
            expense.delete()
            return Response({'message': 'Expense deleted!'}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'message': f'Error: {e}'}, status=status.HTTP_400_BAD_REQUEST)

# --- This view remains the same ---
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def stats_view(request):
    """
    Calculate and return stats for the logged-in user.
    """
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    today = datetime.date.today()
    current_month = today.month
    current_year = today.year

    expenses = Expense.objects.filter(
        owner=request.user,
        date__month=current_month,
        date__year=current_year
    )

    total_spent = sum(expense.amount for expense in expenses)
    expense_count = expenses.count()
    month_name = today.strftime("%B") 

    data = {
        'total_spent': total_spent,
        'expense_count': expense_count,
        'month_name': month_name,
        'display_name': profile.display_name,
        'profile_pic_url': profile.profile_pic_url,
    }

    return Response(data, status=status.HTTP_200_OK)   

# --- 👇 4. PROFILE VIEW UPDATED WITH SERIALIZER ---
@api_view(['GET', 'PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def profile_view(request):
    """
    Retrieve or update the user's profile.
    """
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'GET':
        # Use the serializer to convert the profile object to JSON
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        # Use the serializer to validate and update the profile
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)