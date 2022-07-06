# -*- encoding: utf-8 -*-

{
    'name': 'Employee Contracts - Cabalcon',
    'version': '1.0',
    'category': 'Human Resources/Employee Contracts',
    'author': "Cabalcon",
    'website': "www.cabalcon.com",
    'sequence': 180,
    'summary': '',
    'depends': ['hr_contract', 'cabalcon_hr', 'base_automation'],
    'description': """
    Personalización del módulo de Contratos de empleado  
""",
    "data": [
        'security/ir.model.access.csv',
        'views/hr_employee_views.xml',
        'views/hr_contract_type_views.xml',
        'views/hr_contract_views.xml',
        'views/health_entity_views.xml',
        'views/hr_employee_departure_reason_views.xml',
        'views/res_company_view.xml',
        'views/res_config_settings_views.xml',
        'views/resource_views.xml',
        'report/report_withdrawal_letter_cts.xml',
        'report/report_work_certificates.xml',
        'data/hr_contract_cron_data.xml',
        'data/hr_contract_health_entity.xml',
        'data/hr_employee_departure_reason.xml',
        'data/email_template.xml',
        'wizard/work_certificates_wizard_views.xml',
        
    ],
    "demo": [
    ],
    'installable': True,
    'application': False,
    
}
