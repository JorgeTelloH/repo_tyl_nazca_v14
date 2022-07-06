# -*- coding: utf-8 -*-
{
    'name': "Activar Operativo para Cliente y si es Despachador en Empleados",

    'summary': """
        Activar personal Operativo para Cliente y si es Despachador en Empleados""",

    'description': """
        Agregar activación de personal Operativo para ser asignado a Cliente, si es Despachador,
        inhibir dirección de trabajo y su ubicación dentro de Información de contacto en Empleados.""",

    'author': "TH",
    'website': "http://www.cabalcon.com.pe",

    'category': 'Human Resources',
    'version': '1.1',

    # any module necessary for this one to work correctly
    'depends': ['hr'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/hr_employee_view.xml',
    ],

}