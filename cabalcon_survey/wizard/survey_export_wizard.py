import time
import datetime
from dateutil.relativedelta import relativedelta
from odoo import fields, models, api


class SurveyExport(models.TransientModel):
    _name = 'survey.export.wizard'
    _description = 'Exportar una encuesta'

    survey_id = fields.Many2one('survey.survey', string='Encuesta', domain="[('state', '!=', 'draft')]", required=True)
    date = fields.Date(string='Desde', default=time.strftime('%Y-%m-01'), required=True)
    date_to = fields.Date(string='Hasta', default=lambda self: datetime.date.today().replace(day=1) + relativedelta(months=+1, days=-1), required=True)

    def action_print(self):
        data = {'date': self.date, 'date_to': self.date_to}
        survey = self.env['survey.survey'].browse(self.survey_id.id)
        return self.env.ref('cabalcon_survey.action_survey_report_xlsx').report_action(survey, data=data)

