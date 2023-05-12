from django.db import models

class Transaction(models.Model):
    companyName = models.CharField(max_length=50)
    bookingID = models.CharField(max_length=50)
    date = models.DateField(auto_now_add=True)
    amount = models.FloatField()
    status = models.BooleanField()

    def __str__(self):
        return self.name

class Account(models.Model):
    companyName = models.CharField(max_length=50)
    balance = models.FloatField()

    def __str__(self):
        return self.name
