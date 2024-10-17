from django.contrib.auth import authenticate

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserRegistrationSerializer, UserLoginSerializer
from .models import User
from django.core.mail import send_mail
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError,InvalidToken
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.reverse import reverse
from django.conf import settings
import jwt
from rest_framework.permissions import AllowAny

class UserRegistrationView(APIView):
    authentication_classes = []  # no authentication
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            token=RefreshToken.for_user(serializer.instance)
            link=reverse('verify', args=[str(token.access_token)],request=request)
            subject="Welcome to fundoo notes"
            message=f"Hi {serializer.data['first_name']} {serializer.data['last_name']}, thank you for registering.\n Click:\n{link}"
            from_email='vinitbhamare2002@gmail.com'
            to_email=serializer.data['email']
            send_mail(subject, message, from_email, [to_email])
            return Response({'message': 'Registration successful','data':{'refresh': str(token), 'access': str(token.access_token), 'link': link,'data':serializer.data}}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    authentication_classes = []  # No authentication required
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
            # user = authenticate(request, email=serializer.validated_data['email'], password=serializer.validated_data['password'])
            # if user:
        serializer.save()
        token=RefreshToken.for_user(serializer.instance)
        return Response({'message': 'Login successful','data':{'refresh': str(token), 'access': str(token.access_token)}}, status=status.HTTP_200_OK)
    

@api_view(["GET"])
@permission_classes([AllowAny])
def verify_registered_user(request, token):
    try:
        decoded_token = AccessToken(token)
        print(decoded_token)

        # payload=jwt.decode(token,settings.SECRET_KEY,algorithms=["HS256"])
        user=User.objects.get(id=decoded_token['user_id'])
        user.is_verified=True
        user.save()
        return Response({
            'message': 'Token decoded successfully',
            'decoded_token': decoded_token.payload
        }, status=200)
    
    except InvalidToken as e:
        return Response({
            'error': 'Invalid token',
            'details': str(e)
        }, status=400)
    except TokenError:
        return Response({
            'error': 'Token error or expired'
        }, status=400)