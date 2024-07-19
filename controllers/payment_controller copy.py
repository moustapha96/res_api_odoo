# -*- coding: utf-8 -*-
from .main import *
import pdb
import datetime
import logging
import json
_logger = logging.getLogger(__name__)


class PaymentREST(http.Controller):
    @http.route('/api/precommande/<id>/payment', methods=['GET'], type='http', cors="*", auth='none', csrf=False)
    def api_create_payment_preorder(self, id ):
        try:
            order = request.env['sale.order'].sudo().search([ ('id', '=', id) ], limit=1)
            partner = request.env['res.partner'].sudo().search([('id', '=', order.partner_id.id)], limit=1)
            company = request.env['res.company'].sudo().search([('id', '=', partner.company_id.id)], limit=1)
            # invoice = request.env['account.move'].sudo().search([('id', '=', id_invoice)], limit=1)
            if not request.env.user or request.env.user._is_public():
                admin_user = request.env.ref('base.user_admin')
                request.env = request.env(user=admin_user.id)

            # Création de la facture
            if order:
                # order.action_confirm()
                order_lines = request.env['sale.order.line'].sudo().search([('order_id','=', order.id ) ])
                # Création de la facture
                new_invoice = request.env['account.move'].sudo().create({
                    'move_type': 'out_invoice',
                    'partner_id': partner.id,
                    'invoice_date': order.first_payment_date,
                    'invoice_date_due': order.third_payment_date,
                    'invoice_line_ids': [],
                    'ref': 'Facture '+ order.name,
                })
                # Création des lignes de facture
                for order_line in order_lines:
                    product_id = order_line.product_id.id
                    quantity = order_line.product_uom_qty
                    price_unit = order_line.price_unit

                    invoice_line = request.env['account.move.line'].sudo().create({
                        'move_id': new_invoice.id,
                        'product_id': product_id,
                        'quantity': quantity,
                        'price_unit': price_unit,
                        # 'company_id': company.id,
                        # 'currency_id': company.currency_id.id,
                        'partner_id': partner.id,
                        'ref': 'Facture ' + order.name,
                        # 'name': order.name
                    })
                new_invoice.action_post()
            # enregistrement payment
            if order :

                journal = request.env['account.journal'].sudo().search([('id', '=', 6 )])
                currency = partner.currency_id.id
                if currency != new_invoice.currency_id.id:
                    partner.currency_id = new_invoice.currency_id

                _logger.info( f"journal  {journal} journal  : {journal.id} " )
                _logger.info( f"currency  {currency}  " )
                _logger.info( f"currency invoice  {new_invoice.currency_id.id}  " )
                # journal = request.env['account.journal'].sudo().search([('id', '=', 13)])
                # journal_vr = journal[-1]
                # _logger.info( f"journal  {journal} journal 6 : {journal_vr} " )

                payment_method_line_vr = request.env['account.payment.method.line'].sudo().search([
                    ('journal_id', '=', journal.id)], limit=1)
                # payment_method_line_vr = request.env['account.payment.method.line'].sudo().search([
                #                 ('id', '=', 5)], limit=1)
                _logger.info( f"payment method line  {payment_method_line_vr.id}  " )
                account_payment = request.env['account.payment'].sudo().create({
                    'payment_type': 'inbound',
                    'partner_type': 'customer',
                    'partner_id': partner.id,
                    'amount': order.first_payment_amount,
                    'journal_id': journal.id,
                    'currency_id': partner.currency_id.id,
                    'payment_method_line_id': payment_method_line_vr.id,
                    'payment_method_id': 1, # inbound
                    'sale_id': order.id,
                    'is_reconciled': True,
                    # 'move_id': new_invoice.id
                })
                if account_payment:
                    account_payment.action_post()

                    return request.make_response(
                            json.dumps({
                                'id': order.id,
                                'name': order.name,
                                'partner_id': order.partner_id.id,
                                'type_sale': order.type_sale,
                                'currency_id': order.currency_id.id,
                                'company_id': order.company_id.id,
                                'commitment_date': order.commitment_date.isoformat(),
                                'state': order.state,
                                'invoice_status': order.invoice_status,
                                'first_payment_date': order.first_payment_date.isoformat() if order.first_payment_date else None,
                                'second_payment_date': order.second_payment_date.isoformat() if order.second_payment_date else None,
                                'third_payment_date': order.third_payment_date.isoformat() if order.third_payment_date else None,

                                'first_payment_amount': order.first_payment_amount,
                                'second_payment_amount': order.second_payment_amount,
                                'third_payment_amount': order.third_payment_amount,

                                'first_payment_state': order.first_payment_state,
                                'second_payment_state': order.second_payment_state,
                                'third_payment_state': order.third_payment_state,

                                'invoice_id': account_payment.move_id.id or None ,
                                'is_reconciled': account_payment.is_reconciled,
                                'payment_id': account_payment.id,
                                'payment_name': account_payment.name,
                                'sale_order': account_payment.sale_id.id,
                                'move_id': account_payment.move_id.id,
                                'move_name': account_payment.move_id.name,
                                # 'payment_state': new_invoice.payment_state,
                                # 'invoice_lines': [
                                #     {
                                #         'id': invoice_line.id,
                                #         'product_id': invoice_line.product_id.id,
                                #         'quantity': invoice_line.quantity,
                                #         'price_unit': invoice_line.price_unit,
                                #         'company_id': invoice_line.company_id.id,
                                #         'currency_id': invoice_line.currency_id.id,
                                #         'partner_id': invoice_line.partner_id.id,
                                #         'ref': invoice_line.ref
                                #     } for invoice_line in new_invoice.invoice_line_ids
                                # ],
                            }),
                            headers={'Content-Type': 'application/json'}
                        )
            else:
                return request.make_response(
                            json.dumps({'erreur': 'precommande non trouvé' }),
                            headers={'Content-Type': 'application/json'}
                        )

        except ValueError as e:
            return request.make_response(
                json.dumps({'status': 'error', 'message': str(e)}),
                headers={'Content-Type': 'application/json'}
            )

    @http.route('/api/commande/<id>/payment', methods=['GET'], type='http', cors="*", auth='none', csrf=False)
    def api_create_payment_order(self, id ):
        try:
            order = request.env['sale.order'].sudo().search([ ('id', '=', id) ], limit=1)
            partner = request.env['res.partner'].sudo().search([('id', '=', order.partner_id.id)], limit=1)
            company = request.env['res.company'].sudo().search([('id', '=', partner.company_id.id)], limit=1)
            # invoice = request.env['account.move'].sudo().search([('id', '=', id_invoice)], limit=1)

            if not request.env.user or request.env.user._is_public():
                admin_user = request.env.ref('base.user_admin')
                request.env = request.env(user=admin_user.id)

            # Création de la facture
            if order:
                # order.action_confirm()
                order_lines = request.env['sale.order.line'].sudo().search([('order_id','=', order.id ) ])
                # Création de la facture
                new_invoice = request.env['account.move'].sudo().create({
                    'move_type': 'out_invoice',
                    'partner_id': partner.id,
                    'invoice_date': datetime.datetime.now() ,
                    'invoice_date_due': datetime.datetime.now(),
                    'invoice_line_ids': [],
                    'ref': 'Facture '+ order.name,
                })
                # Création des lignes de facture
                for order_line in order_lines:
                    product_id = order_line.product_id.id
                    quantity = order_line.product_uom_qty
                    price_unit = order_line.price_unit

                    invoice_line = request.env['account.move.line'].sudo().create({
                        'move_id': new_invoice.id,
                        'product_id': product_id,
                        'quantity': quantity,
                        'price_unit': price_unit,
                        # 'company_id': company.id,
                        # 'currency_id': company.currency_id.id,
                        'partner_id': partner.id,
                        'ref': 'Facture ' + order.name,
                        # 'name': order.name
                    })
                new_invoice.action_post()

            # enregistrement payment
            if order :
                order.write({
                    'invoice_status':  'invoiced'
                })
                journal = request.env['account.journal'].sudo().search([('type', 'in', ['bank', 'cash'])])
                journal_vr = journal[-1]
                _logger.info( f"journal  {journal} journal 6 : {journal_vr} " )

                payment_method_line_vr = request.env['account.payment.method.line'].sudo().search([
                    ('id', '=', 9)], limit=1)

                account_payment = request.env['account.payment'].sudo().create({
                    'payment_type': 'inbound',
                    'partner_type': 'customer',
                    'partner_id': partner.id,
                    'amount': order.amount_total ,
                    'journal_id': journal_vr.id,
                    'currency_id': journal_vr.currency_id.id,
                    'payment_method_line_id': payment_method_line_vr.id,
                    # 'payment_method_id': 1,
                    'sale_id': order.id,
                    'is_reconciled': True,
                    # 'move_id': new_invoice.id
                })
                if account_payment:
                    # new_invoice.write({
                    #     'payment_id': account_payment.id,
                    # })
                    _logger.info( f'id facture generere lors du payment {account_payment.move_id}')
                    account_payment.action_post()



                    return request.make_response(
                            json.dumps({
                                'id': order.id,
                                'name': order.name,
                                'partner_id': order.partner_id.id,
                                'type_sale': order.type_sale,
                                'currency_id': order.currency_id.id,
                                'company_id': order.company_id.id,
                                'commitment_date': order.commitment_date.isoformat(),
                                'state': order.state,
                                'amount_total': order.amount_total,
                                'invoice_id': account_payment.move_id.id or None ,
                                'is_reconciled': account_payment.is_reconciled,
                                'payment_id': account_payment.id,
                                'payment_name': account_payment.name,
                                'sale_order': account_payment.sale_id.id,
                                'move_id': account_payment.move_id.id,
                                'move_name': account_payment.move_id.name,
                                'invoice_status': order.invoice_status
                            }),
                            headers={'Content-Type': 'application/json'}
                        )
            else:
                return request.make_response(
                            json.dumps({'erreur': 'precommande non trouvé' }),
                            headers={'Content-Type': 'application/json'}
                        )

        except ValueError as e:
            return request.make_response(
                json.dumps({'status': 'error', 'message': str(e)}),
                headers={'Content-Type': 'application/json'}
            )