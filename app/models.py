from django.db import models

# Create your models here.
class DataBase(models.Model):
    delivery_time = models.DateField()
    rate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        ordering = ['-delivery_time']

    def __str__(self):
        return f"{self.rate}-{self.delivery_time}"



class DeliveryBase(models.Model):
    date_delivery = models.ForeignKey(DataBase, on_delete=models.CASCADE)
    order_cost = models.DecimalField(max_digits=10, decimal_places=2)
    column_number = models.IntegerField()
    order_number = models.IntegerField()


    @property
    def delivery(self):
        return self.date_delivery.delivery_time

    class Meta:
        ordering = ['-date_delivery']

    def __str__(self):
        return f"{self.delivery}-{self.order_number}"
