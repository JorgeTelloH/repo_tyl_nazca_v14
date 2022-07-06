

{
    "name": "Hide Menu, Submenu, Fields and Reports",

    "version": "14.0.0.3",
    "category": "Extra Tools",
    "depends": ['base'],
    "author": "Techspawn Solutions",

    "summary": """ Quickly  Hide any Menu, Submenu, Fields, Reports for any Users and Groups with just one click. """,

    "description": """
        Hide any menu, sub menu, fields, report for any users and groups
    """,

    'license': "OPL-1",
    "website": "http://www.techspawn.com",

    "data": [
        'security/ir.model.access.csv',
        'views/user_res.xml',
        'views/group_res.xml',
        'views/report_ir_actions.xml',
        'views/ir_model_fields_view.xml',
    ],


    "auto_install": False,
    "installable": True,
    "images": ['static/description/main.gif'],
}

