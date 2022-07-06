# -*- coding: utf-8 -*-

{
    'name': 'Herramientas para empleados',
    'version': '1.0',
    'author': "Cabalcon",
    'website': "www.cabalcon.com",
    'category': 'Human Resources',
    'summary': 'Administra las herramientas para los empleados.',
    'depends': ['hr', 'product', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_employee_tools_views.xml',
    ],
    'installable': True,
    'application': False,
}
