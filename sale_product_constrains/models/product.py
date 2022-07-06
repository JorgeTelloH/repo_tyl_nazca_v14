# -*- coding: utf-8 -*-
from odoo import _, api, exceptions, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    _sql_constraints = [('code_company_default_uniq', 'UNIQUE (default_code, company_id)','El Código del producto debe ser unico por Compañia!'),]
