
import logging

from odoo import models, fields, api

class Address(models.Model):
    _inherit = 'tms.tracking'

    type_tracking = fields.Selection(selection_add=[('occurrence', 'Ocurrencia')], ondelete={'occurrence': 'set default'})