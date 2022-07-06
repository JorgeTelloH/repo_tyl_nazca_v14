from odoo import models, fields, api, exceptions


class SaleAdvancePaymentInvInherit(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    merge_invoices = fields.Boolean(string="Unir facturas",default=False)

    def create_invoices(self):
        if self.merge_invoices :
            return super(SaleAdvancePaymentInvInherit, self).create_invoices()
        else:
            return super(SaleAdvancePaymentInvInherit, self.with_context(flag_merge_invoices=True)).create_invoices()

