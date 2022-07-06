# -*- coding: utf-8 -*-
{
    'name': "Envio masivo de Comprobantes a SUNAT",

    'summary': """
        Envio masivo de Comprobantes de Clientes a SUNAT""",

    'description': """
        Seleccionar varios Comprobantes de Cliente para envio masivo a SUNAT
    """,

    'author': "Oswaldo Lopez (Cabalcon)",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account_edi'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/account_move.xml',
    ],

}
