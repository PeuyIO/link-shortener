from django.db import transaction
from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404

from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from analytics.models import Click

from .models import Link
from .serializers import LinkSerializer


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

    def delete(self, request, pk):
        link = get_object_or_404(
            Link,
            id=pk,
            owner=request.user,
        )

        link.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RedirectView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request, short_code):
        link = get_object_or_404(
            Link,
            short_code=short_code,
        )

        if not link.is_active:
            return Response(
                {"detail": "Ссылка отключена."},
                status=status.HTTP_410_GONE,
            )

        with transaction.atomic():
            Click.objects.create(link=link)

            Link.objects.filter(pk=link.pk).update(
                clicks_count=F("clicks_count") + 1
            )

        return HttpResponseRedirect(link.original_url)