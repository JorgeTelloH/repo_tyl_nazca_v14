# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CatalogsSunat(models.Model):
    _name = 'catalogs.sunat.guia'

    @api.model
    def _get_type(self):
        catalog = []
        for x in range(1, 25):
            catalog.append(('%d' % x, 'catalogo%d' % x))
        return catalog

    code = fields.Char(string='Code', size=4, required=True)
    name = fields.Char(string='Nombre', required=True)
    type_catalog = fields.Selection('_get_type', string='Tipo', required=True)
    is_usually = fields.Boolean(string='Is usually')

    _sql_constraints = [
        ('code_uniq', 'unique(code, type_catalog)',
         'Code unique to catalog')
    ]
