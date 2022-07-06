# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class SaleOrderConfirm(models.Model):
    _inherit = 'sale.order'

    def action_multi_confirm(self):
        for order in self.env['sale.order'].browse(self.env.context.get('active_ids')).filtered(
                lambda o: o.state in ['draft', 'sent']):
            order.action_confirm()

    def action_multi_cancel(self):
        for order in self.env['sale.order'].browse(self.env.context.get('active_ids')):
            order.action_cancel()
