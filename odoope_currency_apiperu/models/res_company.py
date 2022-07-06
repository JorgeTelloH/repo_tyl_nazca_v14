# -*- coding: utf-8 -*-

import datetime
from lxml import etree
from dateutil.relativedelta import relativedelta
import re
import logging
from pytz import timezone

import requests

from odoo import api, fields, models
from odoo.addons.web.controllers.main import xml2json_from_elementtree
from odoo.exceptions import UserError
from odoo.tools.translate import _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

_logger = logging.getLogger(__name__)



class ResCompany(models.Model):
    _inherit = 'res.company'

    token_currency = fields.Char(string="Token para Tipo de Cambio")
    currency_provider = fields.Selection(selection_add=[('apiperu', 'Tipo Cambio ApisPeru')])

    # def run_update_currency(self):
    #     """ This method is called from a cron job to update currency rates.
    #     """
    #     records = self.search([('currency_next_execution_date', '<=', fields.Date.today()),('auto_currency_rate','=',True)])
    #     if records:
    #         to_update = self.env['res.company']
    #         for record in records:
    #             if not record.token_currency:
    #                 continue
    #             next_update = relativedelta(days=+1)
    #
    #             res = record.update_currency_rates()
    #             if res:
    #                 record.currency_next_execution_date = datetime.date.today() + next_update

    # def update_currency_rates(self):
    #     rslt = False
    #     active_currencies = self.env['res.currency'].search([])
    #     if self.currency_purchase_id or self.currency_sale_id:
    #         date = fields.Date.today()
    #         endpoint = 'https://api.apis.net.pe/v1/tipo-cambio-sunat?fecha=' + date
    #         headers = {
    #             'Authorization': 'Bearer ' + self.token_currency,
    #             'Referer': 'https://apis.net.pe/tipo-de-cambio-sunat-api'}
    #         data = {"fecha": date}
    #         response = requests.get(endpoint, headers=headers, data=data)
    #         if response.status_code == 200:
    #             rate_obj = self.env['res.currency.rate']
    #             data = json.loads(response.text)
    #             purchase = data.get('compra')
    #             sale = data.get('venta')
    #             origen = data.get('origen')
    #             if self.currency_purchase_id:
    #                 rt_p = rate_obj.search([('name','=',date),('currency_id','=',self.currency_purchase_id.id)])
    #                 if not rt_p:
    #                     rate_create = rate_obj.create({'name': date,
    #                                                'rate_pe': purchase,
    #                                                'rate': 1 / purchase,
    #                                                'currency_id': self.currency_purchase_id.id,
    #                                                'company_id': self.id})
    #                     rate_create.onchange_rate_pe()
    #             if self.currency_sale_id:
    #                 rt_s = rate_obj.search([('name', '=', date), ('currency_id', '=', self.currency_sale_id.id)])
    #                 if not rt_s:
    #                     rate_create = rate_obj.create({'name':date,
    #                                                'rate_pe': sale,
    #                                                'rate': 1 / purchase,
    #                                                'currency_id': self.currency_sale_id.id,
    #                                                'company_id': self.id})
    #                     rate_create.onchange_rate_pe()
    #             rslt = True
    #         else:
    #             return False
    #     else:
    #         return False
    #
    #     return rslt

    def _generate_currency_rates(self, parsed_data):
        """ Generate the currency rate entries for each of the companies, using the
        result of a parsing function, given as parameter, to get the rates data.

        This function ensures the currency rates of each company are computed,
        based on parsed_data, so that the currency of this company receives rate=1.
        This is done so because a lot of users find it convenient to have the
        exchange rate of their main currency equal to one in Odoo.
        """
        Currency = self.env['res.currency']
        CurrencyRate = self.env['res.currency.rate']

        today = fields.Date.today()
        for company in self:
            rate_info = parsed_data.get(company.currency_id.name, None)

            if not rate_info:
                raise UserError(_("Your main currency (%s) is not supported by this exchange rate provider. Please choose another one.", company.currency_id.name))

            base_currency_rate = rate_info[0]

            for currency, (rate, rate2_purch, date_rate) in parsed_data.items():
                rate_value = rate/base_currency_rate
                rate_value2 = rate2_purch / base_currency_rate

                currency_objects = Currency.search([('name','=',currency),('entidad','=','sunat')])
                for currency_object in currency_objects:
                    already_existing_rate = CurrencyRate.search([('currency_id', '=', currency_object.id), ('name', '=', date_rate), ('company_id', '=', company.id)])
                    if already_existing_rate:
                        if already_existing_rate.type == 'sale':
                            already_existing_rate.rate = rate_value
                        if already_existing_rate.type == 'purchase':
                            already_existing_rate.rate = rate2_purch
                    else:
                        rate_res = rate_value
                        if currency_object.type == 'purchase':
                            rate_res = rate_value2
                        CurrencyRate.create({'currency_id': currency_object.id, 'rate': rate_res, 'name': date_rate, 'company_id': company.id})

    def _parse_apiperu_data(self, available_currencies):
        token = False
        for company in self:
            if company.token_currency:
                token = company.token_currency
                break
        date_format_url = '%Y-%m-%d'
        available_currency_names = available_currencies.mapped('name')
        result = {}
        if not token:
            return result
        if 'PEN' not in available_currency_names:
            return result
        result['PEN'] = (1.0, 1.0, fields.Date.context_today(self.with_context(tz='America/Lima'), False))
        headers = {
            'Authorization': 'Bearer ' + token,
            'Referer': 'https://apis.net.pe/tipo-de-cambio-sunat-api'}

        url_format = 'https://api.apis.net.pe/v1/tipo-cambio-sunat?fecha=%(date_start)s'
        date_pe = datetime.datetime.now(timezone('America/Lima'))
        first_pe_str = (date_pe).strftime(date_format_url)
        data = {
            'date_start': first_pe_str,
        }
        data2 = {"fecha": first_pe_str}
        url = url_format % data
        try:
            res = requests.get(url, headers=headers, data=data2)
            res.raise_for_status()
            series = res.json()
            purchase = series.get('compra')
            sale = series.get('venta')
            rate1 = 1.0 / float(sale)
            rate2 = 1.0 / float(purchase)
            result['USD'] = (rate1,rate2, date_pe)
        except Exception as e:
            _logger.error(e)

        return result
