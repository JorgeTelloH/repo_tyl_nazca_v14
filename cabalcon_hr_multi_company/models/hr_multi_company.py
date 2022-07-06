# -*- coding: utf-8 -*-

from odoo import models, fields


class HrAttendanceMultiCompany(models.Model):
    _inherit = 'hr.attendance'

    company_id = fields.Many2one('res.company', 'Compañía', copy=False, help="Compañía",
                                 default=lambda self: self.env.user.company_id)


class HrPayrollStructureType(models.Model):
    _inherit = 'hr.payroll.structure.type'

    company_id = fields.Many2one('res.company', 'Compañía', copy=False, help="Compañía",
                             default=lambda self: self.env.user.company_id)


class HrPayrollStructure(models.Model):
    _inherit = 'hr.payroll.structure'

    company_id = fields.Many2one('res.company', 'Compañía', copy=False, help="Compañía",
                                 default=lambda self: self.env.user.company_id)


class HrSalaryCategoryMultiCompany(models.Model):
    _inherit = 'hr.salary.rule.category'

    company_id = fields.Many2one('res.company', 'Compañía', copy=False, help="Compañía",
                                 default=lambda self: self.env.user.company_id)


class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    company_id = fields.Many2one('res.company', 'Compañía', copy=False, help="Compañía",
                                 default=lambda self: self.env.user.company_id)
