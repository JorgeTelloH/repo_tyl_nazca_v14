# -*- coding: utf-8 -*-

from dateutil.relativedelta import relativedelta
from odoo import models, fields, _, api


class DocumentTypeFamily(models.Model):
    _name = 'hr.employee.document.family.type'
    _description = 'Tipos de documentos que sustentan el vínculo familiar'

    code = fields.Char(string='Código', required=True)
    name = fields.Char(string='Nombre', required=True)
    description = fields.Char(string='Descripción', required=False)


class HrEmployeeFamilyInfo(models.Model):
    _name = 'hr.employee.family'
    _description = 'Familia del empleado'

    employee_id = fields.Many2one('hr.employee', string="Employee", help='Select corresponding Employee',
                                  invisible=1)
    relation_id = fields.Many2one('hr.employee.relation', string="Parentesco", required=True, help="Relationship with the employee")
    name = fields.Char(string='Nombre')
    member_name = fields.Char(string='Nombres', required=True)
    first_name = fields.Char(string='Primer Apellido', required=True,)
    last_name = fields.Char(string='Segundo Apellido')
    document_type = fields.Many2one('hr.employee.document.type', string='Tipo de documento', help="Tipo de documento",
                                     domain=[('identity', '=', 'True')])
    member_id = fields.Char(string='N° del documento de identidad')
    gender = fields.Selection([
        ('male', 'Masculino'),
        ('female', 'Femenino'),
        ('other', 'Otro')
    ], string='Sexo')
    marital = fields.Selection([
        ('single', 'Soltero(a)'),
        ('married', 'Casado(a)'),
        ('cohabitant', 'Cohabitante legal'),
        ('widower', 'Viudo(a)'),
        ('divorced', 'Divorciado(a)')
    ], string='Estado civil', default='single')
    birth_date = fields.Date(string="Fecha de nacimiento", tracking=True)
    age = fields.Integer(compute="_compute_age")
    document_family_type_id = fields.Many2one('hr.employee.document.family.type', string='Documento que sustenta el vínculo ', help="Tipo de documento que sustenta el vínculo familiar")
    doc_attachment_id = fields.Many2many('ir.attachment', 'family_doc_attach_rel', 'famili_id', 'attach_id', string="Adjunto",
                                         help='You can attach the copy of your document', copy=False)
    is_child = fields.Boolean(string='Es un hijo', compute="_compute_is_child")
    is_university = fields.Boolean(string='Cursando estudios superiores')
    country_id = fields.Many2one('res.country', string='País emisor del documento')
    is_passport = fields.Boolean(string='Is passport', compute="_compute_is_passport")

    @api.depends("birth_date")
    def _compute_age(self):
        for record in self:
            age = 0
            if record.birth_date:
                age = relativedelta(fields.Date.today(), record.birth_date).years
            record.age = age

    @api.depends("relation_id")
    def _compute_is_child(self):
        for record in self:
            if record.relation_id:
                record.is_child = (record.relation_id == self.env.ref('cabalcon_hr_employee_family.employee_relationship_son'))
            else:
                record.is_child = False

    @api.depends("document_type")
    def _compute_is_passport(self):
        for record in self:
            if record.document_type:
                record.is_passport = (record.document_type == self.env.ref('cabalcon_hr_documents.document_type_PASSPORT'))
            else:
                record.is_passport = False


    @api.model
    def _get_name(self, name, firstname, lastname):
        return " ".join(p for p in (name, firstname, lastname) if p)

    @api.onchange("member_name", "first_name", "last_name")
    def _onchange_membername_firstname_lastname(self):
        if self.member_name or self.first_name or self.last_name:
            self.name = self._get_name(self.member_name, self.first_name, self.last_name)

    @api.model
    def create(self, vals):
        vals['name'] = self._get_name(vals['member_name'], vals['first_name'], vals['last_name'])
        res = super().create(vals)
        return res

    def write(self, vals):
        member_name = vals.get("member_name") or self.member_name
        first_name = vals.get("first_name") or self.first_name
        last_name = vals.get("last_name") or self.last_name
        vals['name'] = self._get_name(member_name, first_name, last_name)
        res = super().write(vals)

        return res



class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    family_ids = fields.One2many('hr.employee.family', 'employee_id', string='Family', help='Imformacizón d la familia')
    children = fields.Integer(compute='_compute_children')
    minor_children = fields.Integer(compute='_compute_children', string='Menores de edad')
    is_university = fields.Boolean(compute='_compute_children', string='Cursando estudios superiores')
    #Datos de Contactos Emergencia 01 y 02
    emergency_relation_id = fields.Many2one('hr.employee.relation', string="Parentesco", groups="hr.group_hr_user", help="Parentesco con el Empleado")
    emergency_contact_02 = fields.Char(string="2do Contacto de Emergencia", groups="hr.group_hr_user", tracking=True)
    emergency_phone_02 = fields.Char(string="2do Teléfono de Emergencia", groups="hr.group_hr_user", tracking=True)
    emergency_relation_02_id = fields.Many2one('hr.employee.relation', string="2do Parentesco", groups="hr.group_hr_user", required=False, help="Parentesco con el Empleado")

    @api.depends("family_ids", "family_ids.birth_date")
    def _compute_children(self):
        relation = self.env.ref('cabalcon_hr_employee_family.employee_relationship_son')
        for record in self:
            children = 0
            minor_children = 0
            is_university = 0
            if record.family_ids:
                children = len(record.family_ids.filtered(lambda l: l.relation_id == relation))
                minor_children = len(record.family_ids.filtered(lambda l: l.relation_id == relation and l.age < 18))
                is_university = len(record.family_ids.filtered(lambda l: l.relation_id == relation and l.age >= 18 and relation and l.age <= 24 and l.is_university))
            record.children = children
            record.minor_children = minor_children
            record.is_university = is_university > 0

    @api.onchange('spouse_complete_name', 'spouse_birthdate')
    def onchange_spouse(self):
        relation = self.env.ref('cabalcon_hr_employee_family.employee_relationship')
        lines_info = []
        if self.spouse_complete_name and self.spouse_birthdate:
            lines_info.append((0, 0, {
                'member_name': self.spouse_complete_name,
                'relation_id': relation.id,
                'birth_date': self.spouse_birthdate,
            })
                              )
            self.family_ids = lines_info


class EmployeeRelation(models.Model):
    _name = 'hr.employee.relation'
    _description = 'Parentesco con el empleado'

    name = fields.Char(string="Parentesco")
