# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    date_order_not_change = fields.Boolean(string="F.Pedido es igual a F.Presupuesto", default=False, copy=False,
    	help="Activar el check si se desea usar la Fecha de Presupuesto como Fecha de Pedido.")


    def _prepare_confirmation_values(self):
        if self.date_order_not_change and self.date_order: 
            v_date = self.date_order
        else:
            v_date = fields.Datetime.now()

        return {
            'state': 'sale',
            'date_order': v_date
        }