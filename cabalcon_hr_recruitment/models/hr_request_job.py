
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class RequestJob(models.Model):
    _name = "hr.request.job"
    _description = 'Solicitudes de nuevos puestos de trabajo'
    _rec_name = 'job_id'

    employee_id = fields.Many2one('hr.employee', string="Solicitante",
                                  default=lambda self: self.env.user.employee_id, required=True)
    department_id = fields.Many2one(
        'hr.department', "Departmento", compute='_compute_department_and_company', store=True, readonly=False,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", required=True)

    job_id = fields.Many2one('hr.job', "Puesto a poner en convocatoria", required=True,
                             domain="['|', ('company_id', '=', False), ('company_id', '=', company_id),"
                                    "('department_id', '=', department_id)]")
    quantity = fields.Integer(string='Cantidad de puestos', default=1, required=True)

    note = fields.Text(string="Nota")
    state = fields.Selection(string='Estado',
                             selection=[('draft', 'Borrador'),
                                        ('open', 'Solicitado'),
                                        ('done', 'Ejecutado')],
                             default='draft')
    company_id = fields.Many2one('res.company', "Company", compute='_compute_department_and_company', store=True,
                                 readonly=False)

    @api.depends('employee_id')
    def _compute_department_and_company(self):
        for req in self:
            req.department_id = req.employee_id.department_id
            req.company_id = req.employee_id.company_id

    def action_draft(self):
        self.write({'state': 'draft'})

    def action_open(self):
        template = self.env.ref('cabalcon_hr_recruitment.email_template_notification_request_job')
        users = self.company_id.notification_request_job_ids
        if not users:
            raise ValidationError(
                "No se ha configurado el/los empleado de HHRR al que se le notificara la solicitud de nuevos puestos de trabajo")
        for user in users:
            if user.work_email:
                template.write({'email_to': user.work_email})
                template.send_mail(self.id, force_send=True)
        self.write({'state': 'open'})

    def action_done(self):
        self.write({'state': 'done'})
