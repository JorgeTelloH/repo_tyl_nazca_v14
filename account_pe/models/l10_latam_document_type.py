# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models, api
from odoo.osv import expression


class L10nLatamDocumentType(models.Model):
    _inherit = 'l10n_latam.document.type'

    company_id = fields.Many2one('res.company', string='Empresa', default=lambda self: self.env.company)
    type = fields.Selection([
        ('sale', 'Venta'),
        ('purchase', 'Compra')
    ], required=True, default='sale', string='Tipo')


    def name_get(self):
        res = super().name_get()
        result = []
        for rec in self:
            name = rec.name
            type = rec.type or ""
            type_value =dict(self._fields['type'].selection).get(type) or ""
            if rec.code:
                name = '(%s) %s - %s' % (rec.code, name, type_value)
            result.append((rec.id, name))
        return result