import base64
from odoo import fields, models, api, _
from odoo.modules.module import get_module_resource
from odoo.exceptions import UserError


class Applicant(models.Model):
    _name = 'hr.applicant'
    _inherit = ['hr.applicant', 'image.mixin']

    @api.model
    def _default_image(self):
        image_path = get_module_resource('hr', 'static/src/img', 'default_image.png')
        return base64.b64encode(open(image_path, 'rb').read())

    name = fields.Char('Cliente interno', required=False)
    image_1920 = fields.Image(default=_default_image)

    firstname = fields.Char('Nombres', required=True)
    lastname = fields.Char('Apellido paterno', required=True)
    lastname2 = fields.Char('Apellido materno')

    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], string='Sexo')
    document_type = fields.Many2one('hr.employee.document.type', string='Tipo de documento', help="Tipo de documento",
                                    domain=[('identity', '=', 'True')])
    identification_id = fields.Char(string='Identificación No')
    birthday = fields.Date('Fecha de nacimiento')
    country_id = fields.Many2one('res.country', 'Nacionalidad (País)')
    marital = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('cohabitant', 'Legal Cohabitant'),
        ('widower', 'Widower'),
        ('divorced', 'Divorced')
    ], string='Estado civil', default='single')
    children = fields.Integer(string='Números de hijos')
    blood_name = fields.Selection([("A", "A"), ("B", "B"), ("O", "O"), ("AB", "AB")], "Tipo de sangre")
    blood_type = fields.Selection([("+", "+"), ("-", "-")], "Factor")
    #  Direccion
    street = fields.Char('Calle')
    street_number = fields.Char('Casa')
    street_number2 = fields.Char('Puerta')
    l10n_pe_district = fields.Many2one('l10n_pe.res.city.district', string='Districto', help='Districts are part of a province or city.')
    city_id = fields.Many2one('res.city', string='Provincia')
    addres_country_id = fields.Many2one('res.country', string='País', ondelete='restrict')
    state_id = fields.Many2one("res.country.state", string='Estado', ondelete='restrict',
                               domain="[('country_id', '=?', addres_country_id)]")
    zip = fields.Char('CP')

    type_vehicle = fields.Char(string='Tipo de vehículo que maneja')
    # Contactos en caso de emergencia
    contact_name1 = fields.Char(string='Nombre y Aapellidos')
    contact_relation1 = fields.Char(string='Parestesco')
    contact_mobile1 = fields.Char(string='Movil')

    contact_name2 = fields.Char(string='Nombre y Aapellidos')
    contact_relation2 = fields.Char(string='Parestesco')
    contact_mobile2 = fields.Char(string='Movil')

    # Información del banco
    bank_id = fields.Many2one('res.bank', string='Banco')
    bank_account = fields.Char('Cuenta')
    cci = fields.Char(string='CCI')
    number_ruc = fields.Char(string='Número de RUC')

    # Datos familiares
    family_ids = fields.One2many('hr.employee.family', 'applicant_id', string='Familiares')
    
    has_family = fields.Boolean(string='¿Tiene familiares (padres, hermanos, hijos, tíos, primos, esposo (a), cuñados) laborando en esta empresa?')
    family_name = fields.Char('Nombre del familiar')
    department = fields.Char('Área de trabajo')

    #  informacion sobre el vehiculo
    vehicular_plate = fields.Char(string='Placa vehicular')
    year_of_manufacture = fields.Char(string='Año de fabricación del vehículo')
    model_vehicle = fields.Char(string='Modelo del vehículo')
    mark_of_vehicle = fields.Char(string='Marca del vehículo')
    color_of_vehicle = fields.Char(string='Color del vehículo')
    proprietor = fields.Selection(string='Propietario del vehículo',
                                  selection=[('01', 'Vehículo propio'),
                                             ('02', 'Vehículo alquilado'),
                                             ('03', 'Vehículo de un familiar')])

    expiration_date = fields.Date(string='Vencimiento de licencia de conducir')
    category_of_license = fields.Char(string='Categoría de la Licencia de conducir')
    driver_license = fields.Char(string='N° de Licencia de conducir')
    soat_expiration = fields.Date(string='Vencimiento del SOAT')

    @api.model
    def _get_full_name(self, lastname, firstname, lastname2=None):
        names = list()
        if firstname:
            names.append(firstname)
        if lastname:
            names.append(lastname)
        if lastname2:
            names.append(lastname2)
        return " ".join(names)

    @api.model
    def create(self, vals):
        vals['partner_name'] = self._get_full_name(vals['firstname'], vals['lastname'], vals.get('lastname2', False) or '')
        if not vals.get('name', False):
            vals['name'] = vals['partner_name']
        return super(Applicant, self).create(vals)

    def write(self, vals):
        if 'firstname' in vals or 'lastname' in vals or 'lastname2' in vals:
            firstname = vals.get('firstname', False) or self.firstname
            lastname = vals.get('lastname', False) or self.lastname
            lastname2 = vals.get('lastname2', False) or self.lastname2
            vals['partner_name'] = self._get_full_name(firstname, lastname, lastname2)
        return super(Applicant, self).write(vals)

    def create_employee_from_applicant(self):
        res = super(Applicant, self).create_employee_from_applicant()
        data_dict = res.get("context")
        address_home = self.env['res.partner'].browse(data_dict.get("address_home_id"))
        address_home.write({
            'street': self.street,
            'street_number': self.street_number,
            'street_number2': self.street_number2,
            'l10n_pe_district': self.l10n_pe_district.id,
            'city_id': self.city_id.id,
            'state_id': self.state_id.id,
            'zip': self.zip,
            'country_id': self.addres_country_id.id
        })
        bank_account_id = False
        if self.bank_id and self.bank_account:
            bank_account = self.env['res.partner.bank'].create({'partner': address_home.id,
                                                                'acc_number': self.bank_account,
                                                                'type': '2',
                                                                'bank_id': self.bank_id.id,
                                                                'cci': self.cci})
            bank_account_id = bank_account.id

        record_emp = self.env['hr.employee'].create({
            'name': data_dict.get("default_name"),
            'job_id': data_dict.get("default_job_id"),
            'job_title': data_dict.get("default_job_title"),
            'address_home_id': data_dict.get("address_home_id"),
            'department_id': data_dict.get("default_department_id"),
            'address_id': data_dict.get("default_address_id"),
            'work_email': data_dict.get("default_work_email"),
            'work_phone': data_dict.get("default_work_phone"),
            'firstname': self.firstname,
            'lastname': self.lastname,
            'lastname2': self.lastname2,
            'gender': self.gender,
            'document_type': self.document_type.id,
            'identification_id': self.identification_id,
            'birthday': self.birthday,
            'country_id': self.country_id.id,
            'marital': self.marital,
            'children': self.children,
            'bank_account_id': bank_account_id,
            'blood_name': self.blood_name,
            'blood_type': self.blood_type,
            'emergency_contact': self.contact_name1,
            'emergency_phone': self.contact_mobile1,
            'driver_license': self.driver_license,
            'license_expiration': self.expiration_date,
            'license_type': self.category_of_license,
        })
        record_emp.image_1920 = self.image_1920
        res["res_id"] = record_emp.id
        self.family_ids.write({'employee_id': record_emp.id})
        return res


class ApplicantContact(models.Model):
    _name = 'hr.applicant.contact'
    _description = 'Contactos en caso de emergencia'

    name = fields.Char(string='Nombre y Aapellidos', required=True)
    relation = fields.Char(string='Parestesco', required=True)
    mobile = fields.Char(string='Movil', required=True)
    applicant_id = fields.Many2one('hr.applicant', string='Applicant')


class HrEmployeeFamilyInfo(models.Model):
    _inherit = 'hr.employee.family'

    applicant_id = fields.Many2one('hr.applicant', string='Applicant')
