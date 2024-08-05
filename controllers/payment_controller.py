# -*- coding: utf-8 -*-
from .main import *
import pdb
import datetime
import logging
import json
_logger = logging.getLogger(__name__)


class PaymentREST(http.Controller):

    # Dictionnaire en mémoire pour stocker les détails des paiements
    payment_details_memory = {}

    @http.route('/api/precommande/<id>/payment', methods=['GET'], type='http', cors="*", auth='none', csrf=False)
    def api_create_payment_preorder(self, id ):
        try:
            order = request.env['sale.order'].sudo().search([ ('id', '=', id) ], limit=1)
            partner = request.env['res.partner'].sudo().search([('id', '=', order.partner_id.id)], limit=1)
            company = request.env['res.company'].sudo().search([('id', '=', partner.company_id.id)], limit=1) #company : My Company (San Francisco) id = 1
            payment_method = request.env['account.payment.method'].sudo().search([ ( 'payment_type', '=',  'inbound' ) ], limit=1) # payement method : TYPE Inbound & id = 1
            journal = request.env['account.journal'].sudo().search([('company_id', '=', company.id),  ('type', '=', 'sale') ])  # type = sale & company id = 1  ==> journal id = 1 / si journal id = 7 : CASH
            payment_method_line_vr = request.env['account.payment.method.line'].sudo().search([
                    ('payment_method_id', '=', payment_method.id),( 'journal_id', '=', journal.id )], limit=1) # si journal est cash (id = 7)  et payment method inbound == payment method line id  = 1


            # Par defaut
            # journal = request.env['account.journal'].sudo().search([('id', '=', 7 )] , limit=1)
            # payment_method = request.env['account.payment.method'].sudo().search([ ( 'id', '=', 1 ) ], limit=1)
            # payment_method_line_vr = request.env['account.payment.method.line'].sudo().search([('id', '=', 1) ], limit=1)

            user = request.env['res.users'].sudo().search([('id', '=', request.env.uid)], limit=1)
            if not user or user._is_public():
                admin_user = request.env.ref('base.user_admin')
                request.env = request.env(user=admin_user.id)


            # enregistrement payment
            if order :
                _logger.info( f"journal  {journal} journal  : {journal.id} " )
                _logger.info( f"payment method line  {payment_method_line_vr.id}  " )
                account_payment = request.env['account.payment'].sudo().create({
                    'payment_type': 'inbound',
                    'partner_type': 'customer',
                    'partner_id': partner.id,
                    'amount': order.first_payment_amount,
                    'journal_id': journal.id,
                    'currency_id': partner.currency_id.id,
                    'payment_method_line_id': 1,
                    'payment_method_id': payment_method.id, # inbound
                    'sale_id': order.id,
                    'is_reconciled': True,
                    # 'move_id': new_invoice.id
                })
                if account_payment:
                    account_payment.action_post()
                    order.write({
                        'first_payment_state': True
                    })

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


    @http.route('/api/precommande/<id>/payment/<rang>/<amount>', methods=['GET'], type='http', cors="*", auth='none', csrf=False)
    def api_create_payment_rang_preorder(self, id , rang, amount):
        try:
            order = request.env['sale.order'].sudo().search([ ('id', '=', id) ], limit=1)
            partner = request.env['res.partner'].sudo().search([('id', '=', order.partner_id.id)], limit=1)
            company = request.env['res.company'].sudo().search([('id', '=', partner.company_id.id)], limit=1)
            payment_method = request.env['account.payment.method'].sudo().search([ ( 'payment_type', '=',  'inbound' ) ], limit=1)
            journal = request.env['account.journal'].sudo().search([('company_id', '=', company.id),  ('type', '=', 'sale') ])
            payment_method_line_vr = request.env['account.payment.method.line'].sudo().search([
                    ('payment_method_id', '=', payment_method.id),( 'journal_id', '=', journal.id )], limit=1)
            user = request.env['res.users'].sudo().search([('id', '=', request.env.uid)], limit=1)
            if not user or user._is_public():
                admin_user = request.env.ref('base.user_admin')
                request.env = request.env(user=admin_user.id)


            # enregistrement payment
            if order :

                account_payment = request.env['account.payment'].sudo().create({
                    'payment_type': 'inbound',
                    'partner_type': 'customer',
                    'partner_id': partner.id,
                    'amount': amount,
                    'journal_id': journal.id,
                    'currency_id': partner.currency_id.id,
                    'payment_method_line_id': 1,
                    'payment_method_id': payment_method.id, # inbound
                    'sale_id': order.id,
                    'is_reconciled': True,
                    # 'move_id': new_invoice.id
                })
                if account_payment:
                    account_payment.action_post()
                    if rang == 1:
                        if order.first_payment_amount == amount:
                            order.write({
                                'first_payment_state': True
                            })
                        else:
                            # Montant versé incorrect
                            return request.make_response(
                                json.dumps({'erreur': 'Montant versé incorrect pour le premier paiement'}),
                                headers={'Content-Type': 'application/json'}
                            )
                    elif rang == 2:
                        if order.second_payment_amount == amount:
                            order.write({
                                'second_payment_state': True
                            })
                        else:
                            # Montant versé incorrect
                            return request.make_response(
                                json.dumps({'erreur': 'Montant versé incorrect pour le deuxième paiement'}),
                                headers={'Content-Type': 'application/json'}
                            )
                    elif rang == 3:
                        if order.third_payment_amount == amount:
                            order.write({
                                'third_payment_state': True
                            })
                        else:
                            # Montant versé incorrect
                            return request.make_response(
                                json.dumps({'erreur': 'Montant versé incorrect pour le troisième paiement'}),
                                headers={'Content-Type': 'application/json'}
                            )


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
    # @check_permissions
    def api_create_payment_order(self, id ):
        try:
            order = request.env['sale.order'].sudo().search([ ('id', '=', id) ], limit=1)
            partner = request.env['res.partner'].sudo().search([('id', '=', order.partner_id.id)], limit=1)
            company = request.env['res.company'].sudo().search([('id', '=', partner.company_id.id)], limit=1) #company : My Company (San Francisco) id = 1

            _logger.info(f'partner {partner.email} ')
            _logger.info(f'company {company.name} ')

            journal = request.env['account.journal'].sudo().search([('id', '=', 6) ], limit=1)  # type = sale id= 1 & company_id = 1  ==> journal id = 1 / si journal id = 7 : CASH
            # sur le vps : le journal pour CASH est 6
            # journal = request.env['account.journal'].sudo().search([('company_id', '=', company.id),  ('type', '=', 'sale') ], limit=1)  # type = sale id= 1 & company_id = 1  ==> journal id = 1 / si journal id = 7 : CASH
            _logger.info(f'JOURNAL {journal.id} ')
            payment_method = request.env['account.payment.method'].sudo().search([ ( 'payment_type', '=',  'inbound' ) ], limit=1) # payement method : TYPE Inbound & id = 1
            payment_method_line_vr = request.env['account.payment.method.line'].sudo().search([
                    ('payment_method_id', '=', payment_method.id),( 'journal_id', '=', journal.id )], limit=1) # si journal est cash (id = 7)  et payment method inbound ==> payment method line id  = 1

            _logger.info(f'journal {journal} ')
            _logger.info(f'journal {payment_method} ')

            user = request.env['res.users'].sudo().browse(request.env.uid)
            if not user or user._is_public():
                admin_user = request.env.ref('base.user_admin')
                request.env = request.env(user=admin_user.id)

            # Création de la facture
            if order:
                # order.action_confirm()
                order_lines = request.env['sale.order.line'].sudo().search([('order_id','=', order.id ) ])
                invoice_lines = []

                # new_invoice.action_post()

                # Création de la facture
                # new_invoice = request.env['account.move'].sudo().create({
                #     'move_type': 'out_invoice',
                #     'amount_total' : order.amount_total,
                #     'invoice_date': datetime.datetime.now() ,
                #     'invoice_date_due': datetime.datetime.now(),
                #     'invoice_line_ids': [],
                #     'ref': 'Facture '+ order.name,
                #     'journal_id': journal.id,
                #     'partner_id': partner.id,
                #     'company_id':company.id,
                #     'currency_id': partner.currency_id.id,
                # })
                # Création des lignes de facture
                # for order_line in order_lines:
                #     product_id = order_line.product_id.id
                #     quantity = order_line.product_uom_qty
                #     price_unit = order_line.price_unit

                #     invoice_line = request.env['account.move.line'].sudo().create({
                #         'move_id': new_invoice.id,
                #         'product_id': product_id,
                #         'quantity': quantity,
                #         'price_unit': price_unit,
                #         'company_id': company.id,
                #         'currency_id': company.currency_id.id,
                #         'partner_id': partner.id,
                #         'ref': 'Facture ' + order.name,
                #         'journal_id':journal.id,
                #         'name': order.name,
                #     })
                # new_invoice.action_post()

            # enregistrement payment
            if order :
                order.write({
                    'invoice_status':  'invoiced',
                    # 'state': 'sale'
                })
                account_payment = request.env['account.payment'].sudo().create({
                    'payment_type': 'inbound',
                    'partner_type': 'customer',
                    'partner_id': partner.id,
                    'amount': order.amount_total,
                    'journal_id': journal.id,
                    'currency_id': journal.currency_id.id, #42
                    'payment_method_line_id': 1,
                    'payment_method_id': payment_method.id, # inbound
                    'sale_id': order.id,
                })
                # account_payment = request.env['account.payment'].sudo().create({
                #     'payment_type': 'inbound',
                #     'partner_type': 'customer',
                #     'partner_id': partner.id,
                #     'amount': order.amount_total,
                #     'journal_id': new_invoice.journal_id.id,
                #     'currency_id': new_invoice.currency_id.id, #42
                #     'payment_method_line_id': 1,
                #     'payment_method_id': payment_method.id, # inbound
                #     'sale_id': order.id,
                # })
                if account_payment:
                    account_payment.action_post()
                    # new_invoice.write({
                    #     'payment_id': account_payment.id,
                    #     'payment_state': 'paid',
                    # })
                    # account_payment.write({
                    #     'is_reconciled': True,
                    #     # 'move_id': new_invoice.id
                    # })
                    # Reconcilier le paiement avec la facture
                    account_payment.move_id.js_assign_outstanding_line(account_payment.move_id.line_ids.filtered('credit').id)

                    return request.make_response(
                            json.dumps({
                                'id': order.id,
                                'name': order.name,
                                'partner_id': order.partner_id.id,
                                'type_sale': order.type_sale,
                                'currency_id': order.currency_id.id,
                                'company_id': order.company_id.id,
                                # 'commitment_date': order.commitment_date.isoformat(),
                                'state': order.state,
                                'amount_total': order.amount_total,
                                # 'invoice_id': account_payment.move_id.id or None ,
                                # 'is_reconciled': account_payment.is_reconciled,
                                # 'payment_id': account_payment.id,
                                # 'payment_name': account_payment.name,
                                # 'sale_order': account_payment.sale_id.id,
                                # 'move_id': account_payment.move_id.id,
                                # 'move_name': account_payment.move_id.name,
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


    @http.route('/api/precommande/<id>/payment/<amount>', methods=['GET'], type='http', cors="*", auth='none', csrf=False)
    def api_create_payment_rang_preorder(self, id , amount):
        try:
            order = request.env['sale.order'].sudo().search([ ('id', '=', id) ], limit=1)
            partner = request.env['res.partner'].sudo().search([('id', '=', order.partner_id.id)], limit=1)
            company = request.env['res.company'].sudo().search([('id', '=', partner.company_id.id)], limit=1)
            # payment_method = request.env['account.payment.method'].sudo().search([ ( 'payment_type', '=',  'inbound' ) ], limit=1)
            # journal = request.env['account.journal'].sudo().search([('company_id', '=', company.id),  ('type', '=', 'sale') ])
            # payment_method_line_vr = request.env['account.payment.method.line'].sudo().search([
            #         ('payment_method_id', '=', payment_method.id),( 'journal_id', '=', journal.id )], limit=1)

            journal = request.env['account.journal'].sudo().search([('id', '=', 6 )] , limit=1) # type = sale id= 1 & company_id = 1  ==> journal id = 1 / si journal id = 7 : CASH
            payment_method = request.env['account.payment.method'].sudo().search([ ( 'payment_type', '=',  'inbound' ) ], limit=1) # payement method : TYPE Inbound & id = 1
            payment_method_line_vr = request.env['account.payment.method.line'].sudo().search([ ('payment_method_id', '=', payment_method.id), ( 'journal_id', '=', journal.id ) ], limit=1)  # si journal est cash (id = 7)  et payment method inbound ==> payment method line id  = 1

            user = request.env['res.users'].sudo().search([('id', '=', request.env.uid)], limit=1)
            if not user or user._is_public():
                admin_user = request.env.ref('base.user_admin')
                request.env = request.env(user=admin_user.id)


            # enregistrement payment
            if order :

                account_payment = request.env['account.payment'].sudo().create({
                    'payment_type': 'inbound',
                    'partner_type': 'customer',
                    'partner_id': partner.id,
                    'amount': amount,
                    'journal_id': journal.id,
                    'currency_id': partner.currency_id.id,
                    'payment_method_line_id': 1,
                    'payment_method_id': payment_method.id, # inbound
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
                                'amount_untaxed': order.amount_untaxed or None,
                                'amount_tax': order.amount_tax or None,
                                'amount_total': order.amount_total or None,
                                'amount_residual': order.amount_residual,
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
        

    #methode pour enregistrer un payement
    @http.route('/api/payment/set',  methods= ['POST'] , type="http" , cors="*" , auth="none", csrf=False  )
    def set_payment_details(self, **kw):
        try:
            data = json.loads(request.httprequest.data)
            transaction_id = data.get('transaction_id')
            amount = data.get('amount')
            order_id = data.get('order_id')
            order_type = data.get('order_type')
            partner_id = data.get('partner_id')
            # Convertir payment_date en objet datetime
            payment_date = datetime.datetime.now()

            if not all([transaction_id, amount, order_id, order_type, partner_id]):
                return request.make_response(
                    json.dumps({"error": "Missing required fields"}),
                    status=400,
                    headers={'Content-Type': 'application/json'}
                )

            # request.env['payment.details'].sudo().set_payment_details(
            #     transaction_id=transaction_id,
            #     amount=amount,
            #     payment_date=payment_date,
            #     order_id=order_id,
            #     order_type=order_type,
            #     partner_id=partner_id
            # )
             # Stocker les détails du paiement en mémoire
            self.payment_details_memory[transaction_id] = {
                'transaction_id': transaction_id,
                'amount': amount,
                'payment_date': payment_date.strftime('%Y-%m-%d %H:%M:%S'),
                'order_id': order_id,
                'order_type': order_type,
                'partner_id': partner_id,
            }
           

            return request.make_response(
                json.dumps({"message": "Payment details saved successfully", "transaction_id": transaction_id }),
                status=200,
                headers={'Content-Type': 'application/json'}
            )

        except Exception as e:
            return request.make_response(
                json.dumps({"error": str(e)}),
                status=500,
                headers={'Content-Type': 'application/json'}
            )

    # get payment details
    @http.route('/api/payment/get/<transaction_id>', methods=['GET'], type='http', auth='none', cors='*')
    def get_payment_details(self, transaction_id, **kw):
        try:
            # payment_details = request.env['payment.details'].sudo().get_payment_details(transaction_id)
            payment_details = self.payment_details_memory.get(transaction_id)

            if payment_details:
                return request.make_response(
                    json.dumps(payment_details),
                    status=200,
                    headers={'Content-Type': 'application/json'}
                )
            else:
                return request.make_response(
                    json.dumps({"error": "Payment details not found"}),
                    status=404,
                    headers={'Content-Type': 'application/json'}
                )

        except Exception as e:
            return request.make_response(
                json.dumps({"error": str(e)}),
                status=500,
                headers={'Content-Type': 'application/json'}
            )
