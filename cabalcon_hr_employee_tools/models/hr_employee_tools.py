# -*- coding:utf-8 -*-

from datetime import date
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    can_be_tools = fields.Boolean(string="Herramienta asignada ")


class HrEmployeeTools(models.Model):
    _name = 'hr.employee.tools'
    _description = 'Employee Tools'

    product_id = fields.Many2one('product.product', 'Product', required=True)
    default_code = fields.Char(related='product_id.default_code', string="Inventory number")
    serie = fields.Many2one('stock.production.lot', string='Serie', required=True)
    employee_id = fields.Many2one('hr.employee', 'Employee', required=True)
    department_id = fields.Many2one(
        'hr.department', related='employee_id.department_id', string='Department', store=True)
    state = fields.Selection([('asign', 'Asignado'), ('release', 'Liberado')], String="Estado", index=True,
                            default='asign')
    date_asign = fields.Date(string='Fecha de asignación', required=True, default=fields.Date.today())
    date_release = fields.Date(string='Fecha de devolución')

    @api.model
    def create(self, vals):
        employee_tools = super(HrEmployeeTools, self).create(vals)
        employee = self.env['hr.employee'].browse(employee_tools.employee_id.id)
        employee.message_post(body=_("Asset: %s, loaned in the date: %s", employee_tools.product_id.name, date.today()))
        return employee_tools

    def unlink(self):
        for employee_tool in self:
            employee = self.env['hr.employee'].browse(employee_tool.employee_id.id)
            employee.message_post(body=_("Asset: %s, returned in the date: %s", employee_tool.product_id.name, date.today()))
        return super(HrEmployeeTools, self).unlink()

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            tools = self.env['hr.employee.tools'].search([('state', '=', 'asign'),
                                                           ('product_id', '=', self.product_id.id)])
            series_use = tools.mapped('serie').ids

            series = self.env['stock.production.lot'].search([('id', 'not in', series_use),
                                                  ('product_id', '=', self.product_id.id)])
            return {'domain': {'serie': [('id', 'in', series.ids)]}, }



    @api.onchange('date_release')
    def onchange_date_release(self):
        if self.date_release:
            self.state = 'release'

    @api.onchange('state')
    def onchange_state(self):
        if self.state == 'asign':
            self.date_release = False

    @api.constrains('product_id', 'serie', 'employee_id', 'state')
    def _check_product_id(self):
        for record in self:
            if record.product_id and record.employee_id:
                tool = self.env['hr.employee.tools'].search([('state', '=', 'asign'),
                                                             ('product_id', '=', record.product_id.id),
                                                             ('serie', '=', record.serie.id),
                                                             ('employee_id', '!=', record.employee_id.id)])
                if tool:
                    raise ValidationError("El activo ya esta asignado a otro empleado")


class Employee(models.Model):
    _inherit = "hr.employee"

    tools_count = fields.Integer(compute='_compute_tools_count', string='Tools Count')

    def _compute_tools_count(self):
        tools_data = self.env['hr.employee.tools'].sudo().read_group([('employee_id', 'in', self.ids)], ['employee_id'], ['employee_id'])
        result = dict((data['employee_id'][0], data['employee_id_count']) for data in tools_data)
        for employee in self:
            employee.tools_count = result.get(employee.id, 0)



