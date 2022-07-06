# -*- coding: utf-8 -*-
from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = "sale.order"

    invoiced_amount = fields.Monetary(string="Facturado", compute="_compute_invoice_amount", store=True,)
    uninvoiced_amount = fields.Monetary(string="A Facturar", compute="_compute_invoice_amount", store=True,)

    @api.depends("state", "invoice_ids", "invoice_ids.amount_total_signed", "amount_total", "invoice_ids.state")
    def _compute_invoice_amount(self):
        for rec in self:
            if rec.state != "cancel" and rec.invoice_ids:
                rec.invoiced_amount = 0.0
                for invoice in rec.invoice_ids:
                    if invoice.state != "cancel":
                        rec.invoiced_amount += invoice.amount_total_signed
                rec.uninvoiced_amount = max(0, rec.amount_total - rec.invoiced_amount)
            else:
                rec.invoiced_amount = 0.0
                if rec.state in ["draft", "sent", "cancel"]:
                    rec.uninvoiced_amount = 0.0
                else:
                    rec.uninvoiced_amount = rec.amount_total
