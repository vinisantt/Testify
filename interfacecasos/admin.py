from django.contrib import admin
from .models import *

@admin.register(Cargo, Profile,Feature,Componentes,Case,Precondition,Expected,Notification)
class Administration(admin.ModelAdmin):
    pass


# Register your models here.
