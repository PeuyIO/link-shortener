from django.urls import path

from .views import LinkDetailView, LinkListView, LinkStatsView, LinkClicksView, LinkTopView


urlpatterns = [
    path("top/", LinkTopView.as_view(), name="link-top"),
    path("", LinkListView.as_view(), name="link-list"),
    path("<int:pk>/stats/", LinkStatsView.as_view(), name="link-stats"),
    path("<int:pk>/clicks/", LinkClicksView.as_view(), name="link-clicks"),
    path("<int:pk>/", LinkDetailView.as_view(), name="link-detail"),
]