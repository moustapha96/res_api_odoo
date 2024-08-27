from odoo import models, fields, api

from odoo.http import request
import logging

_logger = logging.getLogger(__name__)



# class PaymentDetails(models.Model):
#     _name = 'payment.details'
#     _description = 'Payment Details'

#     transaction_id = fields.Char(string='Transaction ID', required=True)
#     amount = fields.Float(string='Amount', required=True)
#     currency = fields.Char(string='Currency', required=True)
#     payment_method = fields.Char(string='Payment Method', required=True)
#     payment_token = fields.Char(string='Payment Token', required=True)
#     payment_date = fields.Datetime(string='Payment Date', required=True)
#     order_id = fields.Many2one('sale.order', string='Order', required=True)
#     partner_id = fields.Many2one('res.partner', string='Partner', required=True)
#     payment_state = fields.Selection([
#         ('pending', 'Pending'),
#         ('completed', 'Completed'),
#         ('failed', 'Failed')
#     ], string='Payment State', required=True)

#     @api.model
#     def set_payment_details(self, transaction_id, amount,  payment_date, order_id,  partner_id, payment_token, payment_state):
#         # Enregistrer les détails du paiement
#         p = self.create({
#             'transaction_id': transaction_id,
#             'amount': amount,
#             'currency': 'XOF',
#             'payment_method': 'Inbound',
#             'payment_date': payment_date,
#             'order_id': order_id,
#             'partner_id': partner_id,
#             'payment_token': payment_token,
#             'payment_state': payment_state,
#         })
#         return p

#     @api.model
#     def get_payment_details(self, transaction_id):
#         # Récupérer les détails du paiement
#         payment_details = self.search([('transaction_id', '=', transaction_id)], limit=1)
#         if payment_details:
#             return {
#                 'transaction_id': payment_details.transaction_id,
#                 'amount': payment_details.amount,
#                 'currency': payment_details.currency,
#                 'payment_method': payment_details.payment_method,
#                 'payment_date': payment_details.payment_date,
#                 'order_id': payment_details.order_id.id,
#                 'order':{
#                             'id' : payment_details.order_id.id,
#                             'name': payment_details.order_id.name
#                 },
#                 'partner_id': payment_details.partner_id.id,
#                 'partner_name': payment_details.partner_id.name,
#                 'payment_token': payment_details.payment_token,
#                 'payment_state': payment_details.payment_state,
#             }
#         return None
    
#     @api.model
#     def get_payment_partner(self,partner_id):
#         payments = self.search([('partner_id.id', '=', partner_id)])
#         if payments:
#             payment_details = []
#             for p in payments:
#                 payment_details.append({
#                     'transaction_id': p.transaction_id,
#                     'amount': p.amount,
#                     'currency': p.currency,
#                     'payment_method': p.payment_method,
#                     'payment_date': p.payment_date.isoformat(),
#                     'order_id': p.order_id.id,
#                     'order':{
#                             'id' : p.order_id.id,
#                             'name': p.order_id.name
#                     },
#                     'partner_id': p.partner_id.id,
#                     'partner_name': p.partner_id.name,
#                     'payment_token': p.payment_token,
#                     'payment_state': p.payment_state,
#             })
#             return payment_details
#         return []





class PaymentDetails(models.Model):
    _name = 'payment.details'
    _description = 'Payment Details'

    transaction_id = fields.Char(string='Transaction ID', required=True)
    amount = fields.Float(string='Amount', required=True)
    currency = fields.Char(string='Currency', required=True)
    payment_method = fields.Char(string='Payment Method', required=True)
    payment_token = fields.Char(string='Payment Token', required=True)
    payment_date = fields.Datetime(string='Payment Date', required=True)
    order_id = fields.Integer(string='Order ID', required=True)
    partner_id = fields.Integer(string='Partner ID', required=True)
    payment_state = fields.Selection([
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ], string='Payment State', required=True)

    @api.model
    def set_payment_details(self, transaction_id, amount, payment_date, order_id, partner_id, payment_token, payment_state):
        # Enregistrer les détails du paiement
        p = self.create({
            'transaction_id': transaction_id,
            'amount': amount,
            'currency': 'XOF',
            'payment_method': 'Inbound',
            'payment_date': payment_date,
            'order_id': order_id,
            'partner_id': partner_id,
            'payment_token': payment_token,
            'payment_state': payment_state,
        })
        return p

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
                'partner_id': payment_details.partner_id,
                'payment_token': payment_details.payment_token,
                'payment_state': payment_details.payment_state,
            }
        return None

    @api.model
    def get_payment_partner(self, partner_id):
        payments = self.search([('partner_id', '=', partner_id)])
        if payments:
            payment_details = []
            for p in payments:
                payment_details.append({
                    'transaction_id': p.transaction_id,
                    'amount': p.amount,
                    'currency': p.currency,
                    'payment_method': p.payment_method,
                    'payment_date': p.payment_date.isoformat(),
                    'order_id': p.order_id,
                    'partner_id': p.partner_id,
                    'payment_token': p.payment_token,
                    'payment_state': p.payment_state,
                })
            return payment_details
        return []
