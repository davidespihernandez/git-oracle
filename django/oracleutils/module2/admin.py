from django.contrib import admin

from module2.models import (
    Person,
    Thing,
    Car,
    House,
    ThingType,
)


# para cambiar el nombre de las tablas en el admin site se tiene que acceder
# a la clase meta. No puede hacerse en el modelo, ya que se sobrescribe cuando
# se regenera desde la base de datos
Person._meta.verbose_name = 'Persona'
Person._meta.verbose_name_plural = 'Personas'
Person._meta.get_field('name').verbose_name = 'Nombre'
Person._meta.get_field('person_id').verbose_name = 'Id'


# funciones __str__ específicas, que no se pueden definir en el modelo
def persona_str(self):
    return self.name


setattr(Person, '__str__', persona_str)


def thing_type_str(self):
    return self.name


setattr(ThingType, '__str__', thing_type_str)


class ThingAdminInline(admin.TabularInline):
    model = Thing
    fields = ('thing_id', 'date_created', 'person', 'thing_type_code', )
    show_change_link = True


class CarAdminInline(admin.StackedInline):
    model = Car
    fields = ('detail', )
    show_change_link = True
    extra = 1
    max_num = 1


class HouseAdminInline(admin.StackedInline):
    model = House
    fields = ('detail', )
    show_change_link = True
    extra = 1
    max_num = 1


class PersonAdmin(admin.ModelAdmin):
    search_fields = ('name', )
    list_display = ('person_id', 'name', '_numero_cosas', )
    list_display_links = ('name', )
    fields = ('person_id', 'name', )
    inlines = (ThingAdminInline, )

    def _numero_cosas(self, obj):
        return obj.thing_set.count()


class ThingAdmin(admin.ModelAdmin):
    inlines = (CarAdminInline, HouseAdminInline, )
    list_display = ('thing_id', 'date_created', 'thing_type_code', )
    fields = ('thing_id', 'date_created', 'person', 'thing_type_code', )

    def get_formsets_with_inlines(self, request, obj=None):
        for inline in self.get_inline_instances(request, obj):
            has = False
            if inline.__class__ == CarAdminInline:
                has = Car.objects.filter(thing=obj).exists()
            if inline.__class__ == HouseAdminInline:
                has = House.objects.filter(thing=obj).exists()
            if has:
                yield inline.get_formset(request, obj), inline


class CarAdmin(admin.ModelAdmin):
    list_display = ('thing', 'detail', )
    fields = ('thing', 'detail', )


class HouseAdmin(admin.ModelAdmin):
    list_display = ('thing', 'detail', )
    fields = ('thing', 'detail', )


admin.site.register(Person, PersonAdmin)
admin.site.register(Thing, ThingAdmin)
admin.site.register(Car, CarAdmin)
admin.site.register(House, HouseAdmin)
