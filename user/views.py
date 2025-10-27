from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import UserSignupSerializer

class SignupView(generics.CreateAPIView):
    serializer_class = UserSignupSerializer
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        data = serializer.data
        data['access'] = str(refresh.access_token)
        data['refresh'] = str(refresh)
        headers = self.get_success_headers(serializer.data)
        # return response with CORS headers (lightweight fix)
        resp = Response(data, status=status.HTTP_201_CREATED, headers=headers)
        resp['Access-Control-Allow-Origin'] = '*'
        resp['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        resp['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return resp

    def options(self, request, *args, **kwargs):
        # Handle preflight CORS request
        resp = Response(status=status.HTTP_200_OK)
        resp['Access-Control-Allow-Origin'] = '*'
        resp['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        resp['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return resp
