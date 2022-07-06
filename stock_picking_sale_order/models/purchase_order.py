# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class purchase_order(models.Model):

    _inherit = "purchase.order"

    def _prepare_sale_order_data(self, name, partner, company, direct_delivery_address):
        res = super(purchase_order, self)._prepare_sale_order_data(name, partner, company, direct_delivery_address)
        sale = self.env['sale.order'].search([('name','=',self.origin)])
        if sale and sale.team_id:
            team = sale.team_id
            if not team.company_id:
                res['team_id'] = team.id
        return res