# -*- coding: utf-8 -*-
{
    'name': "Fecha de recepcion en Factura",

    'summary': """
        Permite seleccionar la fecha de recepción de facturas de proveedores.
    """,

    'description': """
        Agrega campos de fecha en facturas de proveedores y modifica el cálculo de la fecha de vencimiento.
    """,

    'author': "Cabalcon",
    'website': "www.cabalcon.com",

    'category': 'Invoice',
    'version': '1.0',

    'depends': ['base', 'account_pe'],

    'data': [
        'views/account_move_views.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
