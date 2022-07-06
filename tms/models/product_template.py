# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    type = fields.Selection(selection_add=[('product', 'Producto')],
        string='Tipo de Producto', ondelete={'product': 'set default'})
    tms_product = fields.Boolean(string='Es Producto TMS?', help='Activar si es un Producto asignable\n por la parte operativa')
    tms_product_type = fields.Many2one('tms.route.operation.type', string="Tipo Producto TMS")
    is_travel = fields.Boolean(string='Es un Viaje?', help='Activar si es un Viaje a planificar\n por la parte operativa')
    vehicle_type_id = fields.Many2one('fleet.vehicle.type', string='Tipo de vehículo')
    load_capacity_id = fields.Many2one('fleet.vehicle.capacity', string='Capacidad')
    orig_district = fields.Many2one('l10n_pe.res.city.district', string='Dist Origen')
    orig_province = fields.Many2one('res.city', string='Prov Origen')
    orig_state = fields.Many2one('res.country.state', string='Dpto Origen')
    orig_country = fields.Many2one('res.country', string='País Origen')
    orig_place = fields.Char(string='Lugar Origen', compute='_compute_orig_place', store=True)
    dest_district = fields.Many2one('l10n_pe.res.city.district', 'Dist Destino')
    dest_province = fields.Many2one('res.city', 'Prov Destino')
    dest_state = fields.Many2one('res.country.state', string='Dpto Destino')
    dest_country = fields.Many2one('res.country', string='País Destino')
    dest_place = fields.Char(string='Lugar Destino', compute='_compute_dest_place', store=True)

    @api.onchange('type')
    def _change_type(self):
        self.is_travel = False
        self.tms_product = False
        self.tms_product_type = False

    #================== INI BUSCAR ORIGEN ==================
    @api.onchange('orig_district')
    def _onchange_orig_district(self):
        for rec in self:
            rec.orig_province = rec.orig_district.city_id

    @api.onchange('orig_province')
    def _onchange_orig_province(self):
        for rec in self:
            rec.orig_state = rec.orig_province.state_id

    @api.onchange('orig_state')
    def _onchange_orig_state(self):
        for rec in self:
            rec.orig_country = rec.orig_state.country_id
    #================== FIN BUSCAR ORIGEN ==================
    #================== INI BUSCAR DESTINO ==================
    @api.onchange('dest_district')
    def _onchange_dest_district(self):
        for rec in self:
            rec.dest_province = rec.dest_district.city_id

    @api.onchange('dest_province')
    def _onchange_dest_province(self):
        for rec in self:
            rec.dest_state = rec.dest_province.state_id

    @api.onchange('dest_state')
    def _onchange_dest_state(self):
        for rec in self:
            rec.dest_country = rec.dest_state.country_id
    #================== FIN BUSCAR ORIGEN ==================

    #================== INI OBTENER PROV Y DIST ORIGEN/DESTINO ==================
    @api.depends('orig_state')
    def _compute_orig_place(self):
        for rec in self:
            if rec.orig_district and rec.orig_state:
                rec.orig_place = rec.orig_district.name  + ', ' + rec.orig_province.name
            else:
                rec.orig_place = rec.orig_province.name

    @api.depends('dest_state')
    def _compute_dest_place(self):
        for rec in self:
            if rec.dest_district and rec.dest_state:
                rec.dest_place = rec.dest_district.name  + ', ' + rec.dest_province.name
            else:
                rec.dest_place = rec.dest_province.name
    #================== FIN OBTENER PROV Y DIST ORIGEN/DESTINO ==================
    