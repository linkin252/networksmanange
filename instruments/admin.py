from django.contrib import admin
from .models import National,Company,Sensor_base,Sensor_info,AD_Sensor

# Register your models here.
class NationalAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,{'fields':['Name','ChnName']}),
        ("图片链接",{'fields':['Icon32','Icon64','Icon128']}),
    ]
    list_display = ('Name','ChnName','Icon32','Icon64','Icon128')

admin.site.register(National, NationalAdmin)
admin.site.register(Company)
admin.site.register(Sensor_base)
admin.site.register(Sensor_info)
admin.site.register(AD_Sensor)

