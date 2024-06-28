from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm

from .models import Profile

class ProfileChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = Profile


class ProfileAdmin(UserAdmin):
    form = ProfileChangeForm
    date_hierarchy = 'date_joined'
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups', 'date_joined')
    list_display = ('username', 'first_name', 'last_name', 'email', 'is_active', 'is_staff')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    fieldsets = UserAdmin.fieldsets + (
            ("Location", {'fields': ('street_address','city', 'state', 'zipcode')}),
            ("Job search preferences", {'fields': ('linkedin_username','linkedin_password','keywords','workplace_type','level')}),
    )


admin.site.register(Profile, ProfileAdmin)

