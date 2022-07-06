# -*- coding: utf-8 -*-

from odoo import models, fields, _, api
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError
from odoo.osv import expression


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    time_work = fields.Char('Tiempo de Servicio', compute="_compute_time_work")
    departure_reason = fields.Many2one('hr.employee.departure.reason', 'Departure reason')

    # campos para la seguridad social
    has_social_security = fields.Selection([('Y', 'Si'), ('N', 'No')], string='Seguro Social')


    # campos para la EPS
    eps = fields.Boolean(string='Tiene EPS', default=False)
    social_security_id = fields.Many2one('hr.employee.health.entity', string='Aseguradora de salud')
    eps_amount_plan = fields.Float(string='Plan EPS')
    eps_amount = fields.Float(string='Importe EPS')
    eps_credit = fields.Integer(string='Cantidad de credito EPS')
    eps_credit_employer = fields.Integer(string='Creditos asumidos por el empleador')
    eps_amount_employee = fields.Float(string='Aporte del empleado')
    eps_amount_employer = fields.Float(string='Aporte del empleador')

    @api.depends('first_contract_date', 'departure_date')
    def _compute_time_work(self):
        for record in self:
            if record.first_contract_date and record.departure_date:
                departure_date = record.departure_date or record.contract_id.date_end
                years = relativedelta(departure_date,  record.first_contract_date).years
                months = relativedelta(departure_date,  record.first_contract_date).months
                days = relativedelta(departure_date,  record.first_contract_date).days
                record.time_work = "{} Año(s) {} Mes(es) {} Día(s)".format(years, months, days)
            else:
                record.time_work = ""

    def get_date_to_report(self, date):
        months = ("Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre",
                  "Noviembre", "Diciembre")
        _date = ''
        if date:
            month = months[date.month - 1]
            _date = "{} de {} del {}".format(date.day, month, date.year)

        return _date

    @api.onchange('eps')
    def _onchange_eps(self):
        if not self.eps:
            self.eps_amount = 0
            self.eps_credit = 0

    def _get_contracts(self, date_from, date_to, states=['open', 'near_expire'], kanban_state=False):
        """
        Returns the contracts of the employee between date_from and date_to
        """
        state_domain = [('state', 'in', states)]
        if kanban_state:
            state_domain = expression.AND([state_domain, [('kanban_state', 'in', kanban_state)]])

        return self.env['hr.contract'].search(
            expression.AND([[('employee_id', 'in', self.ids)],
            state_domain,
            [('date_start', '<=', date_to),
                '|',
                    ('date_end', '=', False),
                    ('date_end', '>=', date_from)]]))

    def _get_first_contracts(self):
        self.ensure_one()
        return self.sudo().with_context(active_test=False).contract_ids.filtered(lambda c: c.state != 'cancel')

    def print_work_certificates(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Certificado de trabajo',
            'res_model': 'hr.work.certificate.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'active_id': self.id, 'opinion': self.opinion},
            'views': [[False, 'form']]
        }

    def print_work_certificates_anc(self):
        return self.env.ref('cabalcon_hr_contract.action_work_certificates_anc').report_action(self)

    def print_withdrawal_letter_cts(self):
        return self.env.ref('cabalcon_hr_contract.action_withdrawal_letter').report_action(self)


class DepartureReason(models.Model):
    _name = "hr.employee.departure.reason"
    _description = 'Motivos de salida de la entidad'

    code = fields.Char(string='Código', required="True")
    name = fields.Char(string='Nombre corto', required=True)
    desc = fields.Char(string='Descripción', required="True")
    active = fields.Boolean(string='Active',  default=True)

    def unlink(self):
        for reason in self:
            contracts = self.env['hr.employee'].search([('departure_reason', '=', reason.id)])
            if len(contracts) > 0:
                raise ValidationError('No puedes eliminar este motivo de salidad porque está siendo usado')
        return super(DepartureReason, self).unlink()


class HrDepartureWizard(models.TransientModel):
    _inherit = 'hr.departure.wizard'

    departure_reason = fields.Many2one('hr.employee.departure.reason', 'Departure reason', required=True)