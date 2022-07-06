# -*- coding: utf-8 -*-
{
    'name': "Tipo de vehículo en flota",

    'summary': """
        Registro de Tipo de vehículo en flota""",

    'description': """
        Maestro de registro de Tipo de vehículo en flota y agrega el campo de tipo de vehiculo en flota.
    """,

    'author': "TH",
    'website': "http://www.cabalcon.com.pe",

    'category': 'fleet',
    'version': '1.1',

    # any module necessary for this one to work correctly
    'depends': ['fleet'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/fleet_vehicle_type_views.xml',
		'views/fleet_type_view.xml',
    ],
}