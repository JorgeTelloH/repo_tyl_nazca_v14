# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    
    country_id = fields.Many2one('res.country', string='Pais', ondelete='restrict')
    state_id = fields.Many2one("res.country.state", string='Dpto', ondelete='restrict', domain="[('country_id', '=?', country_id)]")
    city_id = fields.Many2one('res.city', string='Provincia')
    l10n_pe_district = fields.Many2one('l10n_pe.res.city.district', string='Distrito')
    street = fields.Char(string='Dirección Cédula', help='Dirección donde reside según cédula del Empleado')


    @api.onchange("state_id")
    def onchange_state_id(self):
        self.country_id = self.state_id.country_id.id

    @api.onchange("city_id")
    def onchange_city_id(self):
        self.state_id = self.city_id.state_id.id

    @api.onchange("l10n_pe_district")
    def onchange_l10n_pe_district(self):
        self.city_id = self.l10n_pe_district.city_id.id
