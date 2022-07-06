# -*- encoding: utf-8 -*-
{
    'name': 'Tipo de Encuesta',
    'summary': """
    	Tipo de Encuesta
    """,
    'version': '14.0',
    'category': 'Survey',
    'description': """
    Insercion tipo de encuesta        
    """,
    'author': 'Cabalcon S.A.C.',
    'website': 'www.cabalcon.com',
    'depends': ['survey'],
    'data': [
        'views/view_survey_type.xml',
        'security/ir.model.access.csv',
        'views/view_survey_survey.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}