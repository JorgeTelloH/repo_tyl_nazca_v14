# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class PurchaseOrderConfirm(models.Model):
    _inherit = 'purchase.order'

    def action_multi_confirm(self):
        for order in self.env['purchase.order'].browse(self.env.context.get('active_ids')).filtered(
                lambda o: o.state in ['draft', 'sent']):
            order.button_confirm()

    def action_multi_cancel(self):
        for order in self.env['purchase.order'].browse(self.env.context.get('active_ids')):
            order.button_cancel()
