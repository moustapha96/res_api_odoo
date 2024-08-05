from odoo import models, fields, api

from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

from odoo import models, fields, api

class PaymentDetails(models.Model):
    _name = 'payment.details'
    _description = 'Payment Details'

    transaction_id = fields.Char(string='Transaction ID', required=True)
    amount = fields.Float(string='Amount', required=True)
    currency = fields.Char(string='Currency', required=True)
    payment_method = fields.Char(string='Payment Method', required=True)
    payment_date = fields.Datetime(string='Payment Date', required=True)
    order_id = fields.Char(string='Order ID', required=True)
    order_type = fields.Selection([
        ('order', 'Order'),
        ('preorder', 'Preorder')
    ], string='Order Type', required=True)
    partner_id = fields.Many2one('res.partner', string='Partner', required=True)

    @api.model
    def set_payment_details(self, transaction_id, amount,  payment_date, order_id, order_type, partner_id):
        # Enregistrer les détails du paiement
        self.create({
            'transaction_id': transaction_id,
            'amount': amount,
            'currency': 'XOF',
            'payment_method': 'Inbound',
            'payment_date': payment_date,
            'order_id': order_id,
            'order_type': order_type,
            'partner_id': partner_id,
        })

    @api.model
    def get_payment_details(self, transaction_id):
        # Récupérer les détails du paiement
        payment_details = self.search([('transaction_id', '=', transaction_id)], limit=1)
        if payment_details:
            return {
                'transaction_id': payment_details.transaction_id,
                'amount': payment_details.amount,
                'currency': payment_details.currency,
                'payment_method': payment_details.payment_method,
                'payment_date': payment_details.payment_date,
                'order_id': payment_details.order_id,
                'order_type': payment_details.order_type,
                'partner_id': payment_details.partner_id.id,
                'partner_name': payment_details.partner_id.name,
            }
        return None
