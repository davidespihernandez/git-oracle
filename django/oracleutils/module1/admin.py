from django.contrib import admin

from module1.models import (
    Customer,
    Invoice,
    InvoiceLine,
)


# para cambiar el nombre de las tablas en el admin site se tiene que acceder
# a la clase meta. No puede hacerse en el modelo, ya que se sobrescribe cuando
# se regenera desde la base de datos
Customer._meta.verbose_name = 'Cliente'
Customer._meta.verbose_name_plural = 'Clientes'
Customer._meta.get_field('name').verbose_name = 'Nombre'
Customer._meta.get_field('customer_id').verbose_name = 'Id'


# funciones __str__ específicas, que no se pueden definir en el modelo
def customer_str(self):
    return self.name


setattr(Customer, '__str__', customer_str)


class InvoiceAdminInline(admin.TabularInline):
    model = Invoice
    fields = ('customer', 'invoice_id', 'date_created', 'total', )
    show_change_link = True


class InvoiceLineAdminInline(admin.TabularInline):
    model = InvoiceLine
    fields = ('invoice', 'invoice_line_id', 'detail', 'total', )
    show_change_link = True


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    search_fields = ('name', )
    list_display = ('customer_id', 'name', )
    list_display_links = ('name', )
    fields = ('customer_id', 'name', )
    inlines = (InvoiceAdminInline, )


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_select_related = ('customer', )
    inlines = (InvoiceLineAdminInline, )
    list_display = ('customer', 'invoice_id', 'date_created', 'total', )
    fields = ('clave_primaria', 'customer', 'date_created', 'total' )
    readonly_fields = ('clave_primaria', )

    def clave_primaria(self, obj):
        return obj.invoice_id


@admin.register(InvoiceLine)
class InvoiceLineAdmin(admin.ModelAdmin):
    list_select_related = ('invoice', )
    list_display = ('invoice', 'invoice_line_id', 'detail', 'total', )
    fields = ('invoice', 'invoice_line_id', 'detail', 'total', )
