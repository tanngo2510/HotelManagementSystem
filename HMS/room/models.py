from django.db import models
from django.utils import timezone

from accounts.models import Guest
# Create your models here.


class Room(models.Model):
    ROOM_TYPES = (
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
    )

    number = models.IntegerField(primary_key=True)
    capacity = models.SmallIntegerField()
    numberOfBeds = models.SmallIntegerField()
    roomType = models.CharField(max_length=20, choices=ROOM_TYPES)

    price = models.FloatField() 
    statusStartDate = models.DateField(null=True)
    statusEndDate = models.DateField(null=True)

    def __str__(self):
        return str(self.number)


class Booking(models.Model):
    roomNumber = models.ForeignKey(Room, on_delete=models.CASCADE)
    guest = models.ForeignKey(Guest, null=True, on_delete=models.CASCADE)
    dateOfReservation = models.DateField(default=timezone.now)
    startDate = models.DateField()
    endDate = models.DateField()

    def numOfDep(self):
        return Dependees.objects.filter(booking=self).count()

    def __str__(self):
        return str(self.roomNumber) + " " + str(self.guest)


class Dependees(models.Model):
    booking = models.ForeignKey(Booking,   null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def str(self):
        return str(self.booking) + " " + str(self.name)