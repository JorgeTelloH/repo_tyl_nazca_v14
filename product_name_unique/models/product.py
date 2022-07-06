# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.onchange('name')
    def name_uppercase_product(self):
        self.name = self.name.upper() if self.name else False

    @api.constrains('name')
    def _check_unique_constraint(self):
        record = self.search([('name', '=ilike', self.name), ('id', '!=', self.id)])
        if record:
            raise ValidationError(_('El registro ya existe con el mismo nombre!'))

    @api.model
    def create(self, vals):
        res = super(ProductProduct, self).create(vals)
        res.name = res.name.rstrip().lstrip()
        return res

    def write(self, vals):
        if 'name' in vals:
            vals['name'] = vals['name'].rstrip().lstrip()
        return super(ProductProduct, self).write(vals)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.onchange('name')
    def name_uppercase_templete(self):
        self.name = self.name.upper() if self.name else False

    @api.constrains('name')
    def _check_unique_constraint(self):
        record = self.search([('name', '=ilike', self.name), ('id', '!=', self.id)])
        if record:
            raise ValidationError(_('El registro ya existe con el mismo nombre!'))

    @api.model
    def create(self, vals):
        res = super(ProductTemplate, self).create(vals)
        res.name = res.name.rstrip().lstrip()
        return res

    def write(self, vals):
        if 'name' in vals:
            vals['name'] = vals['name'].rstrip().lstrip()
        return super(ProductTemplate, self).write(vals)
