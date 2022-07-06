# -*- coding:utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Contract(models.Model):
    _inherit = "hr.contract"

    name = fields.Char(readonly=1, required=False)

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('hr.contract.code') or '/'
        res = super(Contract, self).create(vals)
        return res


   
