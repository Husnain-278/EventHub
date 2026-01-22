from django.db import models

# Create your models here.

class Venue(models.Model):
    name = models.CharField(max_length=120)
    location = models.CharField(max_length=200)
    capacity = models.PositiveIntegerField()
    price_per_chair = models.PositiveIntegerField()
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to='venues/', blank=True, null=True) 

    def __str__(self):
        return self.name




class EventType(models.Model):
    name = models.CharField(max_length=200)
    base_price = models.PositiveIntegerField()

    def __str__(self):
        return self.name
    



class MenuCategory(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name



class MenuItem(models.Model):
    menu_category = models.ForeignKey(MenuCategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    price_per_head = models.PositiveIntegerField()
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.name




class Booking(models.Model):

    CHOICES = (
        ('Pending','Pending'),
        ('Active','Active'),
        ('Rejected', 'Rejected')
    )

    venue = models.ForeignKey(Venue, on_delete=models.CASCADE)
    event_type = models.ForeignKey(EventType, on_delete=models.CASCADE)
    
    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField()
    event_date = models.DateField()
    event_time = models.TimeField()
    guests_count = models.PositiveIntegerField()

    chairs_cost = models.DecimalField(max_digits=10, decimal_places=2, blank= True, default=0)
    food_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0)
    event_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0)

    status = models.CharField(max_length=30, choices=CHOICES, default='Pending')
    
    #Calculate Chair Cost
    def cal_chair_cost(self):
        self.chairs_cost = self.guests_count * self.venue.price_per_chair

    #Calculate Food Cost
    def cal_food_cost(self):
       if self.pk:
          items = self.bookingmenu_set.all()
          if items:
             self.food_cost = self.guests_count * sum(item.menu_item.price_per_head for item in items)
          else:
             self.food_cost = 0
       else:
          self.food_cost = 0


    #Calculate Event Cost
    def cal_event_cost(self):
        self.event_cost = self.event_type.base_price

    #Calculate Total Cost 
    def cal_total_cost(self):
        self.total_cost = self.chairs_cost + self.food_cost + self.event_cost
    
    def __str__(self):
        return f"{self.customer_name} booked {self.venue} for {self.event_type.name}"
    

    def save(self, *args, **kwargs):
       self.cal_chair_cost()
       self.cal_food_cost()
       self.cal_event_cost()
       self.cal_total_cost()
       super().save(*args, **kwargs)

class BookingMenu(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    class Meta:
      unique_together = ('booking', 'menu_item')
    
    def __str__(self):
      return f"{self.menu_item.name} for {self.booking.customer_name}"
