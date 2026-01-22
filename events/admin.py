from django.contrib import admin
from django.db.models import Sum
from .models import Venue, EventType, MenuCategory, MenuItem, Booking, BookingMenu


# ==================== Venue Admin ====================
@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'capacity', 'price_per_chair', 'is_active')
    list_filter = ('is_active', 'capacity')
    search_fields = ('name', 'location', 'description')
    list_editable = ('is_active',)
    list_per_page = 20
    
    fieldsets = (
        ('Venue Information', {
            'fields': ('name', 'location', 'description')
        }),
        ('Venue Image', {
            'fields': ('image',),
        }),
        ('Capacity & Pricing', {
            'fields': ('capacity', 'price_per_chair'),
        }),
        ('Status', {
            'fields': ('is_active',),
        }),
    )
    



# ==================== Event Type Admin ====================
@admin.register(EventType)
class EventTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'base_price',)
    search_fields = ('name',)
    list_per_page = 20
    



# ==================== Menu Category Admin ====================
@admin.register(MenuCategory)
class MenuCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
  



# ==================== Menu Item Admin ====================
@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'menu_category', 'price_per_head', 'is_available')
    list_filter = ('is_available', 'menu_category')
    search_fields = ('name', 'menu_category__name')
    list_editable = ('is_available',)
    list_per_page = 25
    
    fieldsets = (
        ('Item Details', {
            'fields': ('menu_category', 'name')
        }),
        ('Pricing & Availability', {
            'fields': ('price_per_head', 'is_available'),
        }),
    )
    



# ==================== Booking Menu Inline ====================
class BookingMenuInline(admin.TabularInline):
    model = BookingMenu
    extra = 1
    verbose_name = 'Menu Item'
    verbose_name_plural = 'Selected Menu Items'


# ==================== Booking Admin ====================
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'customer_name', 'venue', 'event_type', 
        'event_date', 'guests_count', 'status', 'total_cost'
    )
    list_filter = ('status', 'event_date', 'venue', 'event_type')
    search_fields = ('customer_name', 'customer_email', 'venue__name')
    date_hierarchy = 'event_date'
    list_per_page = 25
    inlines = [BookingMenuInline]
    
    fieldsets = (
        ('Customer Information', {
            'fields': ('customer_name', 'customer_email'),
        }),
        ('Event Details', {
            'fields': ('venue', 'event_type', 'event_date', 'event_time', 'guests_count'),
        }),
        ('Cost Breakdown', {
            'fields': ('chairs_cost', 'food_cost', 'event_cost', 'total_cost'),
        }),
        ('Booking Status', {
            'fields': ('status',),
        }),
    )
    
    readonly_fields = ('chairs_cost', 'food_cost', 'event_cost', 'total_cost')
    
    actions = ['approve_bookings', 'reject_bookings', 'mark_as_pending']
    
    def save_related(self, request, form, formsets, change):
        """Override to recalculate costs after menu items are saved"""
        super().save_related(request, form, formsets, change)
        # Recalculate and save booking costs after inline menu items are saved
        booking = form.instance
        booking.cal_food_cost()
        booking.cal_total_cost()
        booking.save()
    
    # Custom Actions
    def approve_bookings(self, request, queryset):
        updated = queryset.update(status='Active')
        self.message_user(request, f'{updated} booking(s) approved successfully.')
    approve_bookings.short_description = 'Approve selected bookings'
    
    def reject_bookings(self, request, queryset):
        updated = queryset.update(status='Rejected')
        self.message_user(request, f'{updated} booking(s) rejected.')
    reject_bookings.short_description = 'Reject selected bookings'
    
    def mark_as_pending(self, request, queryset):
        updated = queryset.update(status='Pending')
        self.message_user(request, f'{updated} booking(s) marked as pending.')
    mark_as_pending.short_description = 'Mark as pending'


# ==================== Booking Menu Admin ====================
@admin.register(BookingMenu)
class BookingMenuAdmin(admin.ModelAdmin):
    list_display = ('get_booking_id', 'get_customer', 'menu_item', 'get_category', 'get_item_price')
    list_filter = ('menu_item__menu_category', 'booking__status')
    search_fields = ('booking__customer_name', 'menu_item__name')
    list_per_page = 30
    
    def get_booking_id(self, obj):
        return f'#{obj.booking.id}'
    get_booking_id.short_description = 'Booking ID'
    
    def get_customer(self, obj):
        return obj.booking.customer_name
    get_customer.short_description = 'Customer'
    
    def get_category(self, obj):
        return obj.menu_item.menu_category.name
    get_category.short_description = 'Category'
    
    def get_item_price(self, obj):
        return f'₨ {obj.menu_item.price_per_head:,}/head'
    get_item_price.short_description = 'Price'


# ==================== Admin Site Customization ====================
admin.site.site_header = "EventHub Administration"
admin.site.site_title = "EventHub Admin Portal"
admin.site.index_title = "Welcome to EventHub Management System"
