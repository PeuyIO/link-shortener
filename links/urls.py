from django.urls import path

from .views import LinkDetailView, LinkListView


urlpatterns = [
    path("", LinkListView.as_view(), name="link-list"),
    path("<int:pk>/", LinkDetailView.as_view(), name="link-detail"),
]