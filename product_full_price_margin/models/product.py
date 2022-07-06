# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.tools import float_is_zero


class ProductTemplate(models.Model):
    _inherit = "product.template"

    prd_margin = fields.Float(string="Margen",  default=0, digits="Product Price", readonly=True,
        help="Este Margen se calcula en base al Precio de venta / Costo")
    prd_full_price = fields.Float(string='Precio Full', default=0, digits='Product Price')


    @api.onchange('standard_price', 'list_price')
    def onchange_prd_margin(self):
        for product in self:
            precision = self.env['decimal.precision'].precision_get('Product Price')
            v_margen = 0
            if not float_is_zero(product.standard_price, precision):
                v_margen = product.list_price / product.standard_price
            else:
                v_margen = 0

            product.prd_margin = v_margen

