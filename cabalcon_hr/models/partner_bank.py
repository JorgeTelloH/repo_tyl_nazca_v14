from odoo import fields, models, api


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    cci = fields.Char(string='CCI', size=20)
    type = fields.Selection(string='Tipo de cuenta',
                            selection=[('1', 'CTS'),
                                       ('2', 'Haberes')],
                            required=False, )
