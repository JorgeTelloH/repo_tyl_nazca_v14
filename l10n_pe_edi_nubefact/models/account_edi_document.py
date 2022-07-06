# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons.account_edi_extended.models.account_edi_document import DEFAULT_BLOCKING_LEVEL
from psycopg2 import OperationalError
import logging

_logger = logging.getLogger(__name__)


class AccountEdiDocument(models.Model):
    _inherit = 'account.edi.document'


    @api.model
    def _process_job(self, documents, doc_type):


        def _postprocess_post_edi_results2(documents, edi_result):
            attachments_to_unlink = self.env['ir.attachment']
            for document in documents:
                move = document.move_id
                move_result = edi_result.get(move, {})

        _postprocess_post_edi_results = _postprocess_post_edi_results2

        res = super()._process_job(documents, doc_type)

        # edi_format = documents.edi_format_id
        # state = documents[0].state
        # test_mode = self._context.get('edi_test_mode', False)
        # if doc_type == 'invoice':
        #     if state == 'to_send':
        #         edi_result = edi_format._post_invoice_edi(documents.move_id, test_mode=test_mode)
        #         _postprocess_post_edi_results_nube(documents, edi_result)
        #     # elif state == 'to_cancel':
        #     #     edi_result = edi_format._cancel_invoice_edi(documents.move_id, test_mode=test_mode)
        #     #     _postprocess_cancel_edi_results(documents, edi_result)

        return res
