from django.contrib import admin
from .models import Network,Station,Channel,Sta_ADSensor,Day_data

admin.site.register([Network, Station, Channel, Sta_ADSensor, Day_data])
# Register your models here.
