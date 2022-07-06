# -*- coding:utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Employee(models.Model):
    _inherit = "hr.employee"

    @api.model
    def create(self, vals):
        vals['code'] = self.env['ir.sequence'].next_by_code('hr.employee.code') or '/'
        res = super(Employee, self).create(vals)
        return res


   
