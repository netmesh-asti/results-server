from rest_framework import generics, permissions
from mobile.serializers import MobileResultsSerializer
from rest_framework.authentication import TokenAuthentication


from core.models import MobileResult


class CreateAndroidResView(generics.ListCreateAPIView):
    serializer_class = MobileResultsSerializer
    queryset = MobileResult.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
