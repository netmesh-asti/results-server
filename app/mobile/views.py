from rest_framework import generics, permissions
from mobile.serializers import AndroidResultsSerializer
from rest_framework.authentication import TokenAuthentication


from core.models import AndroidResult


class CreateAndroidResView(generics.CreateAPIView):
    serializer_class = AndroidResultsSerializer
    permission_classes = (permissions.IsAuthenticated,)
    queryset = AndroidResult.objects.all()


class ListAndroidResView(generics.ListAPIView):
    serializer_class = AndroidResultsSerializer
    authentication_classes = (TokenAuthentication,)
    queryset = AndroidResult.objects.all()
