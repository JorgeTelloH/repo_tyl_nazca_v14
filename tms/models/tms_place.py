# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class TmsPlace(models.Model):
    _name = 'tms.place'
    _description = 'Lugares'

    name = fields.Char(string='Lugar', compute='_compute_complete_name', store=True)
    direction = fields.Char(string='Dirección', size=100)
    district_id = fields.Many2one('l10n_pe.res.city.district', string='Distrito', required=True)
    province_id = fields.Many2one('res.city', string='Provincia', required=True)
    state_id = fields.Many2one('res.country.state', string='Departamento', required=True)
    country_id = fields.Many2one('res.country', string='País', required=True)

    _sql_constraints = [ ('001_name_place', 'unique(name)', 'El registro ya existe') ] # Se agregó esta validación

    @api.onchange('district_id')
    def _onchange_district_id(self):
        for rec in self:
            rec.province_id = rec.district_id.city_id

    @api.onchange('province_id')
    def _onchange_province_id(self):
        for rec in self:
            rec.state_id = rec.province_id.state_id

    @api.onchange('state_id')
    def _onchange_state_id(self):
        for rec in self:
            rec.country_id = rec.state_id.country_id

    @api.depends('state_id','district_id','province_id','country_id','direction')
    def _compute_complete_name(self):
        for rec in self:
            if rec.direction and rec.district_id and rec.state_id:
                rec.name = rec.direction + ', ' + rec.district_id.name  + ', ' + rec.state_id.name
            elif rec.direction and rec.province_id:
                rec.name = rec.direction + ', ' + rec.province_id.name  + ', ' + rec.state_id.name
            else:
                rec.name = rec.district_id.name + ', ' + rec.province_id.name  + ', ' + rec.state_id.name
