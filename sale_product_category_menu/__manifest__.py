# -*- coding: utf-8 -*-
{
    "name": "Menu de Categoria de Productos en Ventas",
    "summary": "Mostrar menu de 'Categoria de Productos' en Ventas",
    'description': """
        Visualizar menu de 'Categoria de Productos' en Ventas / Configuración.
    """,
    "author": "TH",
    "website": "www.cabalcon.com.pe",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Product',
    'version': '1.1',

    # any module necessary for this one to work correctly
    "depends": ["sale"],

    # always loaded
    "data": ["views/sale_views.xml"],
}
