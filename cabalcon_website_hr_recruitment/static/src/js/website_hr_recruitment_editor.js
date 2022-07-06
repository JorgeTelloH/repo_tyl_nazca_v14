odoo.define('cabalcon_website_hr_recruitment.form', function (require) {
'use strict';

var core = require('web.core');
var FormEditorRegistry = require('website_form.form_editor_registry');

var _t = core._t;

FormEditorRegistry.add('apply_job', {
    formFields: [{
        type: 'char',
        modelRequired: false,
        name: 'partner_name',
        string: 'Your Name',
    }, {
        type: 'char',
        modelRequired: true,
        name: 'firstname',
        string: 'Nombres',
    }, {
        type: 'char',
        modelRequired: true,
        name: 'lastname',
        string: 'Apellido paterno',
    }, {
        type: 'char',
        modelRequired: true,
        name: 'lastname2',
        string: 'Apellido materno',
    }, {
        type: 'email',
        required: true,
        name: 'email_from',
        string: 'Your Email',
    }, {
        type: 'char',
        required: true,
        name: 'partner_phone',
        string: 'Phone Number',
    }, {
        type: 'char',
        name: 'identification_id',
        string: 'Identificación No.',
    }, {
        type: 'date',
        name: 'birthday',
        string: 'Fecha de nacimiento',
    }, {
        type: 'integer',
        name: 'children',
        string: 'Números de hijos',
    }, {
        type: 'char',
        name: 'street',
        string: 'Calle',
    }, {
        type: 'char',
        name: 'street_number',
        string: 'Casa',
    }, {
        type: 'char',
        name: 'street_number2',
        string: 'Puerta',
    }, {
        type: 'text',
        name: 'description',
        string: 'Short Introduction',
    }, {
        type: 'char',
        name: 'zip',
        string: 'Código postal',
    }, {
        type: 'char',
        name: 'type_vehicle',
        string: 'Tipo de vehículo que maneja',
    }, {
        type: 'char',
        name: 'contact_name1',
        string: 'Nombre y Apellidos',
    }, {
        type: 'char',
        name: 'contact_relation1',
        string: 'Parestesco',
    }, {
        type: 'char',
        name: 'contact_mobile1',
        string: 'Movil',
    }, {
        type: 'char',
        name: 'contact_name2',
        string: 'Nombre y Apellidos',
    }, {
        type: 'char',
        name: 'contact_relation2',
        string: 'Parestesco',
    }, {
        type: 'char',
        name: 'contact_mobile2',
        string: 'Movil',
    }, {
        type: 'char',
        name: 'bank_account',
        string: 'Cuenta',
    }, {
        type: 'char',
        name: 'cci',
        string: 'CCI',
    }, {
        type: 'char',
        name: 'number_ruc',
        string: 'Número de RUC',
    }, {
        type: 'boolean',
        name: 'has_family',
        string: '¿Tiene familiares (padres, hermanos, hijos, tíos, primos, esposo (a), cuñados) laborando en esta empresa?',
    }, {
        type: 'char',
        name: 'family_name',
        string: 'Nombre del familiar',
    }, {
        type: 'char',
        name: 'department',
        string: 'Área de trabajo',
    }, {
        type: 'char',
        name: 'vehicular_plate',
        string: 'Placa vehicular',
    }, {
        type: 'char',
        name: 'year_of_manufacture',
        string: 'Año de fabricación del vehículo',
    }, {
        type: 'char',
        name: 'model_vehicle',
        string: 'Modelo del vehículo',
    }, {
        type: 'char',
        name: 'mark_of_vehicle',
        string: 'Marca del vehículo',
    }, {
        type: 'char',
        name: 'color_of_vehicle',
        string: 'Color del vehículo',
    }, {
        type: 'date',
        name: 'expiration_date',
        string: 'Vencimiento de licencia de conducir',
    }, {
        type: 'char',
        name: 'category_of_license',
        string: 'Categoría de la Licencia de conducir',
    }, {
        type: 'char',
        name: 'driver_license',
        string: 'N° de Licencia de conducir',
    }, {
         type: 'date',
        name: 'soat_expiration',
        string: 'Vencimiento del SOAT',
    }, {
        type: 'binary',
        custom: true,
        name: 'Resume',
    }],
    fields: [{
        name: 'job_id',
        type: 'many2one',
        relation: 'hr.job',
        string: _t('Applied Job'),
    }, {
        name: 'gender',
        type: 'selection',
        string: 'Sexo',
    }, {
        name: 'document_type',
        type: 'many2one',
        relation: 'hr.employee.document.type',
        string: 'Tipo de documento',
    }, {
        name: 'country_id',
        type: 'many2one',
        relation: 'res.country',
        string: 'Nacionalidad (País)',
    }, {
        name: 'marital',
        type: 'selection',
        string: 'Estado civil',
    }, {
        name: 'blood_name',
        type: 'selection',
        string: 'Tipo de sangre',
    }, {
        name: 'blood_type',
        type: 'selection',
        string: 'Factor',
    }, {
        name: 'l10n_pe_district',
        type: 'many2one',
        relation: 'l10n_pe.res.city.district',
        string: 'Districto',
    }, {
        name: 'city_id',
        type: 'many2one',
        relation: 'res.city',
        string: 'Provincia',
    }, {
        name: 'addres_country_id',
        type: 'many2one',
        relation: 'res.country',
        string: 'País',
    }, {
        name: 'state_id',
        type: 'many2one',
        relation: 'res.country.state',
        string: 'Estado',
    }, {
        name: 'bank_id',
        type: 'many2one',
        relation: 'res.bank',
        string: 'Banco',
    }, {
        type: 'selection',
        name: 'proprietor',
        string: 'Propietario del vehículo',
    }, {
        name: 'department_id',
        type: 'many2one',
        relation: 'hr.department',
        string: _t('Department'),
    }],
    successPage: '/job-thank-you',
});

});
