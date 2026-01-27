from events.models import *
from rest_framework import serializers
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings


class VenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venue
        fields = ['id', 'name','image', 'location', 'capacity', 'price_per_chair','description','is_active']




class EventTypeSerializer(serializers.ModelSerializer):
    class Meta: 
        model = EventType
        fields = '__all__'




class MenuCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuCategory
        fields = '__all__'




class MenuItemSerializer(serializers.ModelSerializer):
    menu_category_name = serializers.CharField(
        source = 'menu_category.name',
        read_only = True
    )
    #TODO  use select_related in view for optimized query
    class Meta:
        model = MenuItem
        fields = '__all__'






class BookingSerializer(serializers.ModelSerializer):
    menu_items = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )

    venue_name = serializers.CharField(source='venue.name', read_only=True)
    event_type_name = serializers.CharField(source='event_type.name', read_only=True)

    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = (
            'chairs_cost',
            'food_cost',
            'event_cost',
            'total_cost',
            'status'
        )

    @transaction.atomic
    def create(self, validated_data):
        menu_items = validated_data.pop('menu_items', [])

        # 1️⃣ Create booking
        booking = Booking.objects.create(**validated_data)

        # 2️⃣ Bulk create menu items (FAST)
        if menu_items:
            BookingMenu.objects.bulk_create([
                BookingMenu(
                    booking=booking,
                    menu_item_id=item_id
                )
                for item_id in menu_items
            ])

        # 3️⃣ Recalculate costs ONCE
        booking.save()

        # 4️⃣ Send confirmation email
        self._send_booking_email(booking)

        return booking

    def _send_booking_email(self, booking):
        """Send booking confirmation email to customer"""
        try:
            subject = f'Booking Confirmation - {booking.event_type.name} at {booking.venue.name}'
            message = f"""
Dear {booking.customer_name},

Thank you for booking with EventHub!

Your booking details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Venue: {booking.venue.name}
Event Type: {booking.event_type.name}
Date: {booking.event_date}
Time: {booking.event_time}
Number of Guests: {booking.guests_count}

Cost Breakdown:
- Chairs: ${booking.chairs_cost}
- Food: ${booking.food_cost}
- Event: ${booking.event_cost}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Cost: ${booking.total_cost}

Status: {booking.status}

We will notify you once your booking is confirmed.

Best regards,
EventHub Team
            """
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[booking.customer_email],
                fail_silently=False,
            )
        except Exception as e:
            # Log the error but don't fail the booking
            print(f"Failed to send email: {str(e)}")



class BookingMenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingMenu
        fields = '__all__'




class EventHubStatsSerializer(serializers.Serializer):
    """Serializer to display EventHub statistics"""
    total_venues = serializers.IntegerField(read_only=True)
    total_event_types = serializers.IntegerField(read_only=True)
    total_menu_items = serializers.IntegerField(read_only=True)
    confirmed_bookings = serializers.IntegerField(read_only=True)
