import logging

from odoo import models, fields, api

class OperationType(models.Model):
    _inherit = 'tms.route.operation.type'

    type = fields.Selection([
        ('transporte', 'Transporte'),
        ('custodia', 'Custodia'),
        ('estiba', 'Estiba'),
    ], 'Tipo', default='transporte', help='Tipo', required=True)