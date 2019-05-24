from django.contrib import admin

from module2.models import (
    Person,
    Thing,
)


class ThingAdminInline(admin.TabularInline):
    model = Thing
    fields = ('thing_id', 'date_created', 'person', 'thing_type_code', )
    show_change_link = True


class PersonAdmin(admin.ModelAdmin):
    search_fields = ('name', )
    list_display = ('person_id', '_nombre', '_numero_cosas', )
    list_display_links = ('_nombre', )
    fields = ('person_id', 'name', )
    inlines = (ThingAdminInline, )

    def _nombre(self, obj):
        return obj.name

    def _numero_cosas(self, obj):
        return obj.thing_set.count()


class ThingAdmin(admin.ModelAdmin):
    list_display = ('thing_id', 'date_created', 'thing_type_code', )
    fields = ('thing_id', 'date_created', 'person', 'thing_type_code', )


admin.site.register(Person, PersonAdmin)
admin.site.register(Thing, ThingAdmin)
