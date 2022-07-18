import logging

from odoo import models, fields, api

class Address(models.Model):
    _inherit = 'kw.address'
    _description = 'Address'

    partner_id = fields.Many2many('res.partner', 'res_partner_kw_address_rel', 'kw_address_id',
                                         'partner_id', string="Socio")
    street_number = fields.Char(
        'Casa')
    street_number2 = fields.Char(
        'Puerta')
    comment = fields.Text(string='Notas')
