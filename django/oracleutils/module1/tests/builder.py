from functools import reduce

from module1.factories.customer import CustomerFactory
from module1.factories.invoice import InvoiceFactory
from module1.factories.invoice_line import InvoiceLineFactory


class Builder:
    def customer(self, **kwargs):
        return CustomerFactory(**kwargs)

    def customer_with_name(self, name, **kwargs):
        return CustomerFactory(name=name, **kwargs)

    def invoice(self, **kwargs):
        return InvoiceFactory(**kwargs)

    def invoice_with_lines(self, totals=None, details=None, **kwargs):
        assert totals
        total = kwargs.pop('total', None)
        if not total:
            total = reduce((lambda x, y: x + y), totals)
        invoice = InvoiceFactory(total=total, **kwargs)
        grand_total = 0
        for idx, total in enumerate(totals):
            line_params = {
                'invoice': invoice,
                'total': total,
            }
            if details and idx <= len(details):
                line_params['detail'] = details[idx]
            InvoiceLineFactory(**line_params)
            grand_total += total
        invoice.total = grand_total
        invoice.save()
        return invoice
