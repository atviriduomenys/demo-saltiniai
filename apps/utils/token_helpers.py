from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken, Token


def get_token(user: User) -> Token:
    return RefreshToken.for_user(user)
