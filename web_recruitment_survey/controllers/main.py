# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request
import werkzeug
import base64


class WebsiteHrRecruitment(http.Controller):

    @http.route('/survey/start', type='http', methods=['POST'], auth="public", website=True, csrf=False)
    def test_path(self, **kw):
        job = kw.get('job_id')
        survey = request.env['hr.job'].sudo().search([('id', '=', job)], limit=1)
        if kw.get('partner_name'):
            name = ('%s\'s Application' % kw.get('partner_name'))
        vals = {
            'name': name,
            'partner_name': kw.get('partner_name'),
            'email_from': kw.get('email_from'),
            'partner_phone': kw.get('partner_phone'),
            'description': kw.get('description'),
            'job_id': survey.id,
            'department_id': survey.department_id.id,
        }
        new_ticket = request.env['hr.applicant'].sudo().create(vals)
        #url = survey.survey_id.action_start_survey()
        url = new_ticket.action_start_survey()
        if kw.get('resume'):
            for c_file in request.httprequest.files.getlist('resume'):
                data = c_file.read()
                if c_file.filename:
                    request.env['ir.attachment'].sudo().create({
                        'name': c_file.filename,
                        'datas': base64.b64encode(data),
                        'res_model': 'hr.applicant',
                        'res_id': new_ticket.id
                    })
        return werkzeug.utils.redirect(url['url'])







