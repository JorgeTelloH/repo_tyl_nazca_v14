# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Hr Employee Medical Information",
    "summary": """
        Adds information about employee's medical Information""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "Cabalcon",
    "website": "www.cabalcon.com",
    "depends": ["cabalcon_hr"],
    "data": [
        "views/hr_employee_vaccination_views.xml",
        "views/immunizations.xml",
        "views/hr_employee_views.xml",
        "security/ir.model.access.csv",

    ],
}
