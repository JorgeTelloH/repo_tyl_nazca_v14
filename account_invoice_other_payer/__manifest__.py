# -*- coding: utf-8 -*-
{
    'name': "Factura pagado por otro socio",
    'summary': """
        Factura de Cliente y Proveedor pagado por otro socio""",
    'description': """
        Factura de Cliente y Proveedor pagado por otro socio.
    """,

    'author': "Eficent,Odoo Community Association (OCA), TH",
    'website': "http://www.cabalcon.com",

    'category': 'Accounting',
    'version': '1.1',

    # any module necessary for this one to work correctly
    'depends': ['account', 'account_pe'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/account_move_views.xml',
    ],

}
