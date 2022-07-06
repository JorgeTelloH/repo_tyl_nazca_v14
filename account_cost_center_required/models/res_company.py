# -*- coding: utf-8 -*-
from odoo import models, fields, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    account_cost_center_select = fields.Selection([
        ('never', 'Nunca'),
        ('always', 'Siempre'),
        ('posted', 'Solo Publicados')
    ], 'Centro de Costo requerido', default='never')