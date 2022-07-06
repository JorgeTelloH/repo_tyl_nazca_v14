# -*- coding: utf-8 -*-
{
    'name': "Generar Factura según el Tipo de Documento",

    'summary': """
        Crear Factura desde Pedido de Venta según el Tipo de Documento""",

    'description': """
        Crear Factura desde Pedido de Venta según la configuración del Tipo de Documento
    """,

    'author': "Oswaldo Lopez (Cabalcon)",

    'category': 'Sales',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['sale','account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
    ],
}
