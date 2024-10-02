# -*- coding: utf-8 -*-
from .main import *
import pdb
import datetime

_logger = logging.getLogger(__name__)


class ApiWhatsappREST(http.Controller):

    @http.route('/api/webhooks', methods=['POST'], type='http', auth='none', cors="*", csrf=False)
    def api_whatsapp_webhooks(self,**kw):
        data = json.loads(request.httprequest.data)
        _logger.info(f"Received data: {data}")

        return request.make_response(
            json.dumps({"status": "success", "message": "Data received successfully"}),
            status=200,
            headers={'Content-Type': 'application/json'}
        )