from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Link
from .serializers import LinkSerializer

from django.shortcuts import render, get_object_or_404


class LinkListView(generics.ListCreateAPIView):
    serializer_class = LinkSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Link.objects.filter(
            owner=self.request.user
        ).order_by("-created_at")


class LinkDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        link = get_object_or_404(
            Link,
            id=pk,
            owner=request.user,
        )

        serializer = LinkSerializer(
            link,
            context={"request": request},
        )

        return Response(serializer.data)