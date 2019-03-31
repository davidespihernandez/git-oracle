# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class InvoiceLine(models.Model):
    invoice_line_id = models.BigIntegerField(primary_key=True)
    invoice = models.ForeignKey('Invoice', models.DO_NOTHING, blank=True, null=True)
    detail = models.CharField(max_length=4000)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'INVOICE_LINE'
