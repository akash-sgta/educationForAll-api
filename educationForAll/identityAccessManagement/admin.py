from django.contrib import admin
from django.utils.html import format_html

from identityAccessManagement.models import (
    Identity,
    ActiveToken,
    BlacklistToken,
    Access,
    Group,
    AccessGroup,
    App,
    Table,
)

from utilities.pool import epochms2datetime
from utilities.constant import CRED

## ============================================================================= ##


@admin.register(Identity)
class IdentityAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "created", "is_active", "is_logged")
    ordering = ("username", "is_active")
    search_fields = ["username"]
    empty_value_display = "NULL"
    list_per_page = 25

    def created(self, obj):
        dt = epochms2datetime(obj.created_on).strftime("%Y%m%d %H:%M:%S")
        return dt

    def is_logged(self, obj):
        count = len(ActiveToken.objects.filter(identity=obj.id))
        return format_html(f"<a href='/django-admin/identityAccessManagement/activetoken/?q={obj.id}'>{count}</a>")


@admin.register(ActiveToken)
class ActiveTokenAdmin(admin.ModelAdmin):
    list_display = ("id", "identity", "device", "unique_id", "logged_on")
    ordering = ("identity", "unique_id")
    search_fields = ["identity"]
    empty_value_display = "NULL"
    list_per_page = 25

    def logged_on(self, obj):
        dt = epochms2datetime(obj.last_logged).strftime("%Y%m%d %H:%M:%S")
        return dt


@admin.register(BlacklistToken)
class BlacklistTokenAdmin(admin.ModelAdmin):
    list_display = ("identity", "created_on")
    ordering = ["identity"]
    # search_fields = ["identity"]
    empty_value_display = "NULL"
    list_per_page = 25

    def created_on(self, obj):
        dt = epochms2datetime(obj.created_on).strftime("%Y%m%d")
        return dt


## ============================================================================= ##


@admin.register(App)
class AppAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "table")
    ordering = ["name"]
    search_fields = ["id"]
    empty_value_display = "NULL"
    list_per_page = 10

    def table(self, obj):
        count = len(Table.objects.filter(app=obj.id))
        if count == 0:
            return None
        else:
            return format_html(f"<a href='/django-admin/identityAccessManagement/table/?q={obj.name}'>{count}</a>")


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "app")
    ordering = ["id", "name"]
    search_fields = ["id", "app__name"]
    empty_value_display = "NULL"
    list_per_page = 10

    def app(self, obj):
        appLink = App.objects.get(id=obj.app.id)
        return format_html(f"<a href='/django-admin/identityAccessManagement/app/?q={appLink.id}'>{appLink.name}</a>")


## ============================================================================= ##


@admin.register(Access)
class AccessAdmin(admin.ModelAdmin):
    list_display = ("id", "app_model", "action")
    ordering = ["id"]
    search_fields = ["id", "app_model__name"]
    empty_value_display = "NULL"
    list_per_page = 24


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "access")
    ordering = ["name"]
    search_fields = ["id", "name"]
    empty_value_display = "NULL"
    list_per_page = 25

    def access(self, obj):
        o2m = AccessGroup.objects.filter(group=obj.id)
        html = "<p>"
        for one in o2m:
            html += f"<a href='/django-admin/identityAccessManagement/access/?q={one.access.id}'>{one.access.app_model} | {CRED[one.access.action]}</a><br>"
        html += "</p><hr><p><a href='/django-admin/identityAccessManagement/accessgroup/add/'>CREATE NEW PERMISSION</a></p>"
        return format_html(html)


@admin.register(AccessGroup)
class AccessGroupAdmin(admin.ModelAdmin):
    list_display = ("id", "group", "defination")
    ordering = ["group"]
    search_fields = ["id", "group__name"]
    empty_value_display = "NULL"
    list_per_page = 24

    def defination(self, obj):
        data = f"{obj.access.app_model} | {obj.access.action}"
        return format_html(f"<a href='/django-admin/identityAccessManagement/group/?q={obj.group.id}'>{data}</a>")
