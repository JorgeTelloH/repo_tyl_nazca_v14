from collections import OrderedDict, defaultdict
from datetime import date, datetime
from functools import partial
from operator import attrgetter
import itertools
import logging

import pytz
import psycopg2
from odoo.tools import float_is_zero, pycompat
from odoo.fields import Binary
from odoo.fields import Field
import base64
import binascii
from odoo.tools.mimetypes import guess_mimetype
from odoo.exceptions import UserError
from odoo import _



# def convert_to_column(self, value, record, values=None, validate=True):
#     # Binary values may be byte strings (python 2.6 byte array), but
#     # the legacy OpenERP convention is to transfer and store binaries
#     # as base64-encoded strings. The base64 string may be provided as a
#     # unicode in some circumstances, hence the str() cast here.
#     # This str() coercion will only work for pure ASCII unicode strings,
#     # on purpose - non base64 data must be passed as a 8bit byte strings.
#     if not value:
#         return None
#     # Detect if the binary content is an SVG for restricting its upload
#     # only to system users.
#     magic_bytes = {
#         b'P',  # first 6 bits of '<' (0x3C) b64 encoded
#         b'<',  # plaintext XML tag opening
#     }
#     if isinstance(value, str):
#         value = value.encode()
#     if value[:1] in magic_bytes:
#         try:
#             decoded_value = base64.b64decode(value.translate(None, delete=b'\r\n'), validate=True)
#         except binascii.Error:
#             decoded_value = value
#         # Full mimetype detection
#         if (guess_mimetype(decoded_value).startswith('image/svg') and
#                 not record.env.is_system()):
#             raise UserError(_("Only admins can upload SVG files."))
#     if isinstance(value, bytes):
#         return psycopg2.Binary(value)
#     try:
#         return psycopg2.Binary(str(value).encode('ascii'))
#     except UnicodeEncodeError:
#         raise UserError(_("ASCII characters are required for %s in %s") % (value, self.name))
#
# Binary.convert_to_column = convert_to_column


# def write(self, records, value):
#     if not self.attachment:
#         return Field.write(records, value)
#
#     # discard recomputation of self on records
#     records.env.remove_to_compute(self, records)
#
#     # update the cache, and discard the records that are not modified
#     cache = records.env.cache
#     cache_value = self.convert_to_cache(value, records)
#     records = cache.get_records_different_from(records, self, cache_value)
#     if not records:
#         return records
#     if self.store:
#         # determine records that are known to be not null
#         not_null = cache.get_records_different_from(records, self, None)
#
#     cache.update(records, self, [cache_value] * len(records))
#
#     # retrieve the attachments that store the values, and adapt them
#     if self.store and any(records._ids):
#         real_records = records.filtered('id')
#         atts = records.env['ir.attachment'].sudo()
#         if not_null:
#             atts = atts.search([
#                 ('res_model', '=', self.model_name),
#                 ('res_field', '=', self.name),
#                 ('res_id', 'in', real_records.ids),
#             ])
#         if value:
#             # update the existing attachments
#             atts.write({'datas': value})
#             atts_records = records.browse(atts.mapped('res_id'))
#             # create the missing attachments
#             missing = (real_records - atts_records)
#             if missing:
#                 atts.create([{
#                     'name': self.name,
#                     'res_model': record._name,
#                     'res_field': self.name,
#                     'res_id': record.id,
#                     'type': 'binary',
#                     'datas': value,
#                 }
#                     for record in missing
#                 ])
#         else:
#             atts.unlink()
#
#     return records
#
# Binary.write = write
