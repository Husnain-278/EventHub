from events.models import *
from rest_framework import serializers
from django.db import transaction


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

        return booking



class BookingMenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingMenu
        fields = '__all__'