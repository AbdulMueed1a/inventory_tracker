from rest_framework import generics
from rest_framework.permissions import AllowAny

from .serializers import UserSignupSerializer

class SignupView(generics.CreateAPIView):
    serializer_class = UserSignupSerializer
    permission_classes = (AllowAny,)