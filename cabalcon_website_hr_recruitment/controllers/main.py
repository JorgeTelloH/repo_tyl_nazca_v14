# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.addons.http_routing.models.ir_http import slug
from odoo.http import request
from werkzeug.exceptions import NotFound


class WebsiteHrRecruitment(http.Controller):

    @http.route('''/jobs/apply/<model("hr.job"):job>''', type='http', auth="public", website=True, sitemap=True)
    def jobs_apply(self, job, **kwargs):
        if not job.can_access_from_current_website():
            raise NotFound()

        error = {}
        default = {}
        if 'website_hr_recruitment_error' in request.session:
            error = request.session.pop('website_hr_recruitment_error')
            default = request.session.pop('website_hr_recruitment_default')

        document_types = request.env['hr.employee.document.type'].search([('identity', '=', 'True')])
        countries = request.env['res.country'].search([])
        districts = request.env['l10n_pe.res.city.district'].search([])
        cities = request.env['res.city'].search([])
        peru = request.env['res.country'].search([('code', '=', 'PE')], limit=1).id
        states = request.env['res.country.state'].search([('country_id', '=', peru)])
        banks = request.env['res.bank'].search([])

        return request.render("website_hr_recruitment.apply", {
            'job': job,
            'error': error,
            'default': default,
            'document_types': document_types,
            'countries': countries,
            'districts': districts,
            'cities': cities,
            'states': states,
            'banks': banks,
            'peru': peru,

        })
