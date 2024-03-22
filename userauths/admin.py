from django.contrib import admin
from userauths.models import User


class UserAdmin(admin.ModelAdmin):
  list_display=['username','email','phone_number']  

admin.site.register(User,UserAdmin)

