# -*- encoding: utf-8 -*-

{
    'name': 'Employee work certificates ANC',
    'version': '1.0',
    'category': 'Human Resources/Employee',
    'author': "Cabalcon",
    'website': "www.cabalcon.com",
    'sequence': 180,
    'summary': '',
    'depends': ['hr_contract', 'cabalcon_hr'],
    'description': """
    Personalización del modelo certificado de trabajo   
""",
    "data": [
        'security/ir.model.access.csv',
        'views/hr_employee_views.xml',
        'report/report_work_certificates_anc.xml',

    ],
    "demo": [
    ],
    'installable': True,
    'application': False,
    
}
