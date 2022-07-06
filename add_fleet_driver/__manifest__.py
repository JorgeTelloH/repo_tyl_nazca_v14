# -*- coding: utf-8 -*-
{
    'name': "Agregar atributos de conductor a flota",

    'summary': """
        Adiciona datos de conductor y otros datos a flota""",

    'description': """
        Adiciona atributos de Conductor a flota, si es vehículo tercerizado, seguros, certificados, entre otros.
    """,

    'author': "TH",
    'website': "http://www.cabalcon.com.pe",

    'category': 'fleet',
    'version': '1.1',

    # any module necessary for this one to work correctly
    'depends': ['base','fleet','add_employee_driver','partner_is_customer_vendor'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/fleet_vehicle_view.xml',
    ],

}