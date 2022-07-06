# -*- encoding: utf-8 -*-

{
    'name': 'Ausencias - Cabalcon',
    'category': 'Human Resources',
    'author': 'Cabalcon',
    'website': '',
    'depends': ['hr_holidays', 'hr_work_entry_contract', 'cabalcon_hr'],
    'version': '1.0',
    'active': True,
    'data': ['views/import_error_view.xml',
             'views/hr_leave_allocation_views.xml',
             'views/hr_employee_views.xml',
             'views/hr_leave_view.xml',
             'wizard/wizard_import_vacations_view.xml',
             'wizard/wizard_holidays_report_view.xml',
             'security/ir.model.access.csv',
             'data/hr_holidays_data.xml',
             'data/hr_holidays_cron.xml',
             'data/email_template.xml',
             'reports/holidays_template.xml',
    ],
    'css': [],
    'test': [

    ],

    'installable': True
}
