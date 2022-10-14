from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext as _
from django.contrib.auth.models import Group

from core import models
from core.group_admin import GroupAdminForm


class UserAdmin(BaseUserAdmin):
    ordering = ['id']
    list_display = ['email', 'first_name', 'last_name', 'registration']
    fieldsets = (
        (None, {'fields': ('email', 'nro', 'password')}),
        (_('Personal Info'), {'fields': ('first_name', 'last_name')}),
        (
            _('Permissions'),
            {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        (_('Affiliation'), {'fields': ('is_ntc',)}),
        (_('Important dates'), {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')
        }),
    )


class ServerAdmin(admin.ModelAdmin):
    ordering = ['id']
    list_display = ['id', 'nickname', 'ip_address']


# Unregister the original Group admin.
admin.site.unregister(Group)


# Create a new Group admin.
class GroupAdmin(admin.ModelAdmin):
    # Use our custom form.
    form = GroupAdminForm
    # Filter permissions horizontal as well.
    filter_horizontal = ['permissions']


class NroAdmin(admin.ModelAdmin):
    list_display = ['get_region_display']


# Register the new Group ModelAdmin.
admin.site.register(Group, GroupAdmin)

admin.site.register(models.NtcRegionalOffice, NroAdmin)
admin.site.register(models.User, UserAdmin)
admin.site.register(models.RfcDevice)
admin.site.register(models.MobileDevice)
admin.site.register(models.MobileResult)
admin.site.register(models.RfcResult)
admin.site.register(models.Server, ServerAdmin)
admin.site.register(models.PublicSpeedTest)
admin.site.register(models.NTCSpeedTest)
admin.site.register(models.RfcTest)
