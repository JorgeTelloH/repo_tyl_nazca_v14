from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.main import content_disposition


class Main(http.Controller):

	@http.route('/reports/format/<string:object>/<string:file_format>/<int:ids>', type='http', auth='user')
	def report_guide_formats(self, object, file_format, ids, **kw):
		Model = request.env[object].browse(ids)
		content = Model.document_print()
		filename = Model.file_name(file_format)
		return request.make_response(content, [('Content-Type', self._get_content_type_format_print(file_format)),
											('Content-Disposition', content_disposition(filename))])

	def _get_content_type_format_print(self, file_format):
		dic = self._get_content_type_dic()
		return dic[file_format]

	def _get_content_type_dic(self):
		dic = {
			'txt': 'application/octet-stream;charset=utf-8;',
			'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
		}
		return dic