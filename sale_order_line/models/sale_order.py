# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class SaleOrderLine(models.Model):   
    _inherit = "sale.order.line"
    
    order_ref = fields.Char('Pedido',related='order_id.name')
    date_order = fields.Datetime(related='order_id.date_order', store=True, string='Fecha de Pedido')
