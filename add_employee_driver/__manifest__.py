# -*- coding: utf-8 -*-
{
    'name': "Agregar atributos de conductor al personal",

    'summary': """
        Adiciona datos de conductor al personal""",

    'description': """
        Adiciona nuevos atributos de Conductor al personal: Datos de Conductor, si es Outsourcing, conductor en lista negra, entre otros.
    """,

    'author': "TH",
    'website': "http://www.cabalcon.com.pe",

    'category': 'Human Resources',
    'version': '1.1',

    # any module necessary for this one to work correctly
    'depends': ['hr'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'security/security.xml',
        'views/hr_employee_view.xml',
    ],

}