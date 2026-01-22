from rest_framework import generics
from rest_framework import status
from .serializers import *
from events.models import *



# Create your views here.

#To show all Venues
class VenueView(generics.ListAPIView):
    queryset = Venue.objects.filter(is_active = True)
    serializer_class = VenueSerializer


#To Select type of Event
class EventTypeView(generics.ListAPIView):
    queryset = EventType.objects.all()
    serializer_class = EventTypeSerializer

#To select Menu Category
class MenuCategoryView(generics.ListAPIView):
    queryset = MenuCategory.objects.all()
    serializer_class = MenuCategorySerializer



#To Select Menu Category Item 
class MenuItemView(generics.ListAPIView):
    serializer_class = MenuItemSerializer
    def get_queryset(self):
        return MenuItem.objects.select_related('menu_category')
    


#Booking View
class BookingView(generics.ListCreateAPIView):
    serializer_class = BookingSerializer
    def get_queryset(self):
        return Booking.objects.select_related('venue', 'event_type').prefetch_related('bookingmenu_set__menu_item')
    


#BookingMenu View
class BookingMenuView(generics.ListAPIView):
    serializer_class = BookingMenuSerializer
    def get_queryset(self):
      return BookingMenu.objects.select_related('booking', 'menu_item')