from django.contrib import admin
from .models import SolenoidState, DataCollection, FlowRate, WaterUsage, Configuration, StatusFertil , ConfigFertil, StoricFertil, TimeFerti

admin.site.register(SolenoidState)
admin.site.register(DataCollection)
admin.site.register(FlowRate)
admin.site.register(WaterUsage)
admin.site.register(Configuration)
admin.site.register(StatusFertil)
admin.site.register(ConfigFertil)
admin.site.register(StoricFertil)
admin.site.register(TimeFerti)