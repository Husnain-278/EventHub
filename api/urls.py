from django.urls import path
from .views import *

urlpatterns = [
    path('venues/', VenueView.as_view()),
    path('event-types/', EventTypeView.as_view()),
    path('menu-categories/', MenuCategoryView.as_view()),
    path('menu-items/', MenuItemView.as_view()),
    path('booking/', BookingView.as_view(),),
    path('booking-menu/', BookingMenuView.as_view()),
    path('event-stats/', EventHubStatsView.as_view()),
]
