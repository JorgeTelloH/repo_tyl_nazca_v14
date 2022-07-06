# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Recruitment',
    'version': '1.0',
    'category': 'Human Resources/Recruitment',
    'sequence': 90,
    'summary': '',
    'description': "",
    'website': '',
    'depends': [
        'hr_recruitment', 'cabalcon_hr_contract', 'cabalcon_hr_employee_medical_information', 'cabalcon_hr_employee_family'
    ],
    'data': [
        'security/hr_recruitment_security.xml',
        'security/ir.model.access.csv',
        'data/email_template.xml',
        'views/res_company_view.xml',
        'views/hr_request_job.xml',
        'views/hr_recruitment_views.xml',
        
    ],
    'demo': [
        
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
