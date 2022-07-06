# -*- coding: utf-8 -*-
{
    'name': "Dirección Actual de Empleado",
    'summary': """
        Agrega Direccion Actual del empleado
    """,
    'description': 
    """
        Agrega Direccion Actual del empleado en Sección Privada / Ciudadanía
        Agrega Nro Identificación en Sección Privada / Contacto Privado :: dentro de Direccion 
    """
    ,

    'author': "TH",
    'website': "http://www.cabalcon.com.pe",

    'category': 'Human Resources/Employees',
    'version': '1.1',

    # any module necessary for this one to work correctly
    'depends': ['hr', 'contacts', 'l10n_latam_base', 'l10n_pe'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/hr_employee_view.xml',
    ],
}
