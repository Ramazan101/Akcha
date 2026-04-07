from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Финансы', {'fields': ('income',)}),
    )
    list_display = ['username', 'email', 'income', 'is_staff']