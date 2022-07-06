from rest_framework import generics, permissions
from results.serializers import AndroidResultsSerializer

from core.models import AndroidResult


class CreateAndroidResView(generics.CreateAPIView):
    serializer_class = AndroidResultsSerializer
    permission_classes = (permissions.IsAuthenticated,)
    queryset = AndroidResult.objects.all()


class ListAndroidResView(generics.ListAPIView):
    serializer_class = AndroidResultsSerializer
    authentication_classes = []
    queryset = AndroidResult.objects.all()
