# -*- coding: utf-8 -*-
{
    'name': "Vehiculos de Empleados Extendido",
    'summary': """
        Mejora al obtener datos de vehiculos del Empleado""",
    'description': """
        Se aplican mejoras al obtener datos de vehiculos del Empleado:\n
        - Visualizar siempre el botón de vehículos desde Empleados.
        """,
    'author': "TH",
    'website': "http://www.cabalcon.com.pe",
    
    'category': 'Human Resources',
    'version': '1.1',
    
    # any module necessary for this one to work correctly
    'depends': ['hr', 'hr_fleet'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/hr_employee_views.xml',
    ],
    
}
