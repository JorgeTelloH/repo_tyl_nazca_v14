from odoo import fields, models, api
from odoo.exceptions import ValidationError


class Payslip(models.Model):
    _inherit = 'hr.payslip'

    # función para obtener el eps desde el payslip y se pueda utilizar en las reglas
    def get_eps_credit(self):
        eps = self.env['hr.calculate.eps'].search([('company_id', '=', self.company_id.id)], limit=1, order='year_eps, month_eps DESC')
        if eps:
            return eps.amount_eps
        else:
            return 0

    def action_payslip_done(self):
        for slip in self:
            if slip.struct_id and slip.struct_id.has_eps:
                month_eps = slip.date_from.month
                year_eps = slip.date_from.year
                eps = self.env['hr.calculate.eps'].search([('month_eps', '=', month_eps),
                                                           ('year_eps', '=', year_eps),
                                                           ('state', '=', 'posted')])
                if not eps:
                    raise ValidationError("No esta permitido cerrar la nómina hasta que el cálculo del EPS este terminado")
                else:
                    break

        return super(Payslip, self).action_payslip_done()

