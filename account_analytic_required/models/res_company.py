# -*- coding: utf-8 -*-
from odoo import models, fields, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    account_analytic_select = fields.Selection([
        ('never', 'Nunca'),
        ('always', 'Siempre'),
        ('posted', 'Solo Publicados')
    ], 'Analítica requerido', default='never')