# -*- coding: utf-8 -*-
{
    'name': "Borrado masivo de facturas",

    'summary': """
        Borra las facturas validadas de forma masiva""",

    'description': """
        Borra las facturas validadas de forma masiva
    """,

    'author': "Oswaldo Lopez S. (Cabalcon)",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Tools',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/account_move.xml',
    ],

}
