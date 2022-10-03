from django.db import models

# Create your models here.
class DataBase(models.Model):
    delivery_time = models.DateField(null=True, blank=True)
    rate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    order_cost = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    column_number = models.IntegerField(blank=True, null=True)
    order_number = models.IntegerField(blank=True, null=True)
    column_index = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.delivery_time}"

