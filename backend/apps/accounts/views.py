from django.contrib.auth import login, logout
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import UserSerializer, LoginSerializer, RegisterSerializer
from .permissions import IsAdministrator

class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            errors = []
            for field, errs in serializer.errors.items():
                if isinstance(errs, list):
                    errors.append(f"{field.capitalize()}: {errs[0]}")
                else:
                    errors.append(f"{field.capitalize()}: {errs}")
            return Response({"detail": " | ".join(errors), "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()

        # Automatically log user in
        login(request, user)

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        refresh["role"] = user.role
        refresh["username"] = user.username

        return Response({
            "message": "Registration successful.",
            "user": UserSerializer(user).data,
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
        }, status=status.HTTP_201_CREATED)

class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        
        # Django session login for browser cookie auth
        login(request, user)

        # JWT tokens for REST API clients
        refresh = RefreshToken.for_user(user)
        refresh["role"] = user.role
        refresh["username"] = user.username

        return Response({
            "message": "Login successful.",
            "user": UserSerializer(user).data,
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
        }, status=status.HTTP_200_OK)

class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)

class CurrentUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

class UserListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdministrator]

    def get(self, request):
        users = User.objects.all().order_by("-created_at")
        return Response(UserSerializer(users, many=True).data)

    def post(self, request):
        username = request.data.get("username", "").strip()
        email = request.data.get("email", "").strip()
        password = request.data.get("password", "")
        role = request.data.get("role", User.Role.ENGINEER)

        if not username or not password:
            return Response({"detail": "Username and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({"detail": "A user with this username already exists."}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role=role
        )
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
