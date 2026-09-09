from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser

admin.site.site_header= "SOKOPOINT MANAGEMENT"
admin.site.site_title ="SOKOPOINT MANAGEMENT"
admin.site.site_url="/"

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
	list_display = ('username', 'email', 'user_type', 'phone', 'location', 'is_staff', 'is_active')
	list_filter = ('user_type', 'is_staff', 'is_active', 'is_superuser')
	search_fields = ('username', 'email', 'phone', 'location')

	fieldsets = UserAdmin.fieldsets + (
		('Profile', {'fields': ('user_type', 'phone', 'location')}),
	)
	add_fieldsets = UserAdmin.add_fieldsets + (
		('Profile', {'fields': ('email', 'user_type', 'phone', 'location')}),
	)
