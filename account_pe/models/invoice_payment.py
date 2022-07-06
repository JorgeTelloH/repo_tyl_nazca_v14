# -*- coding: utf-8 -*-

import io
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

import logging
_logger = logging.getLogger(__name__)

class invoicePayment(models.Model):
    _name = 'invoice.payment'

    date  = fields.Date(string='Fecha', required=True, help="Keep empty to use the current date", copy=False)
    amount = fields.Monetary(string='Monto', required=True)
    currency_id = fields.Many2one('res.currency', string='Moneda', required=True)
    move_id = fields.Many2one('account.move', string='Factura', required=True)
