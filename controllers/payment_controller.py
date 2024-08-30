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


    @http.route('/api/commande/<id>/payment', methods=['GET'], type='http', cors="*", auth='none', csrf=False)
    # @check_permissions
    def api_create_payment_order(self, id ):
        try:
            order = request.env['sale.order'].sudo().search([ ('id', '=', id) ], limit=1)
            partner = request.env['res.partner'].sudo().search([('id', '=', order.partner_id.id)], limit=1)
            company = request.env['res.company'].sudo().search([('id', '=', partner.company_id.id)], limit=1) #company : My Company (San Francisco) id = 1

            _logger.info(f'partner {partner.email} ')
            _logger.info(f'company {company.name} ')

            # journal = request.env['account.journal'].sudo().search([('id', '=', 7) ], limit=1)  # type = sale id= 1 & company_id = 1  ==> journal id = 1 / si journal id = 7 : CASH (en local )
            journal = request.env['account.journal'].sudo().search([('code', '=', 'CSH1'),( 'company_id', '=', company.id ) ], limit=1)  # type = CASH1 id= 7 & company_id = 1  ==> journal id = 7 / journal id = 7 : CASH
            # journal = request.env['account.journal'].sudo().search([('code', '=', 'sale'),( 'company_id', '=', company.id ) ], limit=1)  # type = sale id= 1 & company_id = 1  ==> journal id = 1 / si journal id = 7 : CASH
            # journal = request.env['account.journal'].sudo().search([('company_id', '=', company.id),  ('type', '=', 'sale') ], limit=1)  # type = sale id= 1 & company_id = 1  ==> journal id = 1 / si journal id = 7 : CASH
            _logger.info(f'JOURNAL {journal.id} ')
            payment_method = request.env['account.payment.method'].sudo().search([ ( 'payment_type', '=',  'inbound' ) ], limit=1) # payement method : TYPE Inbound & id = 1
            payment_method_line_vr = request.env['account.payment.method.line'].sudo().search([
                    ('payment_method_id', '=', payment_method.id),( 'journal_id', '=', journal.id )], limit=1) # si journal est cash (id = 7)  et payment method inbound ==> payment method line id  = 1
            # on a pas besoin de payment method line 

            _logger.info(f'journal {journal} ')
            _logger.info(f'journal {payment_method} ')
            user = request.env['res.users'].sudo().browse(request.env.uid)
            if not user or user._is_public():
                admin_user = request.env.ref('base.user_admin')
                request.env = request.env(user=admin_user.id)


            # enregistrement payment
            if order :
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
                if account_payment:
                    account_payment.action_post()

                    # Création de la facture
                    # new_invoice = request.env['account.move'].sudo().create({
                    #     'move_type': 'out_invoice',
                    #     'amount_total' : order.amount_total,
                    #     'invoice_date': datetime.datetime.now() ,
                    #     'invoice_date_due': datetime.datetime.now(),
                    #     'invoice_line_ids': [],
                    #     'ref': 'Facture '+ order.name,
                    #     'journal_id': journal_facture.id,
                    #     'partner_id': partner.id,
                    #     'company_id':company.id,
                    #     'currency_id': partner.currency_id.id,
                    #     # 'payment_id': account_payment.id,
                    #     'sale_id': order.id
                    # })
                    # if new_invoice:
                    #     # Création des lignes de facture
                    #     order_lines = request.env['sale.order.line'].sudo().search([('order_id','=', order.id ) ])
                    #     for order_line in order_lines:
                    #         product_id = order_line.product_id.id
                    #         quantity = order_line.product_uom_qty
                    #         price_unit = order_line.price_unit

                    #         invoice_line = request.env['account.move.line'].sudo().create({
                    #             'move_id': new_invoice.id,
                    #             'product_id': product_id,
                    #             'quantity': quantity,
                    #             'price_unit': price_unit,
                    #             'company_id': company.id,
                    #             'currency_id': company.currency_id.id,
                    #             'partner_id': partner.id,
                    #             'ref': 'Facture ' + order.name,
                    #             'journal_id': journal_facture.id,
                    #             'name': order.name,
                    #         })


                        # new_invoice.action_post()
                    # order.action_confirm()
                     # Création automatique de la facture et liaison du paiement
                    order.action_confirm()
                  
                    # Reconcilier le paiement avec la facture
                    # account_payment.move_id.js_assign_outstanding_line(account_payment.move_id.line_ids.filtered('credit').id)
                # Création de la facture
            
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


    # methode qu'on utilise
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

            journal = request.env['account.journal'].sudo().search([('code', '=', 'CSH1'),( 'company_id', '=', company.id ) ], limit=1)  # type = sale id= 1 & company_id = 1  ==> journal id = 1 / si journal id = 7 : CASH
            
            # journal = request.env['account.journal'].sudo().search([('id', '=', 6 )] , limit=1) # type = sale id= 1 & company_id = 1  ==> journal id = 1 / si journal id = 7 : CASH
            payment_method = request.env['account.payment.method'].sudo().search([ ( 'payment_type', '=',  'inbound' ) ], limit=1) # payement method : TYPE Inbound & id = 1
            # payment_method_line_vr = request.env['account.payment.method.line'].sudo().search([ ('payment_method_id', '=', payment_method.id), ( 'journal_id', '=', journal.id ) ], limit=1)  # si journal est cash (id = 7)  et payment method inbound ==> payment method line id  = 1

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
            partner_id = data.get('partner_id')
            payment_token = data.get('payment_token')
            payment_state = data.get('payment_state')
            payment_date = datetime.datetime.now()

            if not all([transaction_id, amount, order_id,  partner_id]):
                return request.make_response(
                    json.dumps({"error": "Missing required fields"}),
                    status=400,
                    headers={'Content-Type': 'application/json'}
                )

            order = request.env['sale.order'].sudo().search([('id','=', order_id )], limit=1)
            if order.type_sale == "order":
                payment_details_existe = request.env['payment.details'].sudo().search([('transaction_id', '=', transaction_id)], limit=1)
                if payment_details_existe:
                    payment_details_existe.write({
                        'amount': amount,
                        'payment_date': payment_date,
                        'payment_token': payment_token,
                        'payment_state': payment_state
                    })
                    return request.make_response(
                        json.dumps({
                            'id': payment_details_existe.id,
                            'transaction_id': payment_details_existe.transaction_id,
                            'amount': payment_details_existe.amount,
                            'currency': payment_details_existe.currency,
                            'payment_method': payment_details_existe.payment_method,
                            'payment_date': payment_details_existe.payment_date.isoformat(),
                            'order_id': payment_details_existe.order_id,
                            'order_name': payment_details_existe.order_name,
                            'order_type': payment_details_existe.order_type,
                            'partner_id': payment_details_existe.partner_id,
                            'payment_token': payment_details_existe.payment_token,
                            'url_facture': payment_details_existe.url_facture,
                            'customer_name' : payment_details_existe.customer_name,
                            'customer_email' : payment_details_existe.customer_email,
                            'customer_phone' : payment_details_existe.customer_phone,
                            'payment_state': payment_details_existe.payment_state,}),
                        status=200,
                        headers={'Content-Type': 'application/json'}
                    )
            if  order.type_sale == "preorder":
                payment_details_existe = request.env['payment.details'].sudo().search([('transaction_id', '=', transaction_id)], limit=1)
                if payment_details_existe:
                    if  payment_details_existe.payment_state == "completed":
                        minutes = payment_date.minute
                        new_transaction_id = payment_details_existe.transaction_id + '-' + str(minutes)

                        payment_details = request.env['payment.details'].sudo().set_payment_details(
                            transaction_id=new_transaction_id,
                            amount=amount,
                            payment_date=payment_date,
                            order_id=order_id,
                            order_name=order.name,
                            order_type=order.type_sale,
                            partner_id=partner_id,
                            payment_token=payment_token,
                            payment_state=payment_state
                        )
                        return request.make_response(
                            json.dumps({
                                    'id': payment_details.id,
                                    'transaction_id': payment_details.transaction_id,
                                    'amount': payment_details.amount,
                                    'currency': payment_details.currency,
                                    'payment_method': payment_details.payment_method,
                                    'payment_date': payment_details.payment_date.isoformat(),
                                    'order_id': payment_details.order_id,
                                    'order_name': payment_details.order_name,
                                    'order_type': payment_details.order_type,
                                    'partner_id': payment_details.partner_id,
                                    'payment_token': payment_details.payment_token,
                                    'url_facture': payment_details.url_facture,
                                    'customer_name' : payment_details.customer_name,
                                    'customer_email' : payment_details.customer_email,
                                    'customer_phone' : payment_details.customer_phone,
                                    'payment_state': payment_details.payment_state,}),
                            status=200,
                            headers={'Content-Type': 'application/json'}
                        )
                    else:
                        payment_details_existe.write({
                            'amount': amount,
                            'payment_date': payment_date,
                            'payment_token': payment_token,
                            'payment_state': payment_state
                        })    
                        return request.make_response(
                            json.dumps({
                                'id': payment_details_existe.id,
                                'transaction_id': payment_details_existe.transaction_id,
                                'amount': payment_details_existe.amount,
                                'currency': payment_details_existe.currency,
                                'payment_method': payment_details_existe.payment_method,
                                'payment_date': payment_details_existe.payment_date.isoformat(),
                                'order_id': payment_details_existe.order_id,
                                'order_name': payment_details_existe.order_name,
                                'order_type': payment_details_existe.order_type,
                                'partner_id': payment_details_existe.partner_id,
                                'payment_token': payment_details_existe.payment_token,
                                'url_facture': payment_details_existe.url_facture,
                                'customer_name' : payment_details_existe.customer_name,
                                'customer_email' : payment_details_existe.customer_email,
                                'customer_phone' : payment_details_existe.customer_phone,
                                'payment_state': payment_details_existe.payment_state,}),
                            status=200,
                            headers={'Content-Type': 'application/json'}
                        )
                    
            payment_details = request.env['payment.details'].sudo().set_payment_details(
                transaction_id=transaction_id,
                amount=amount,
                payment_date=payment_date,
                order_id=order_id,
                order_name=order.name,
                order_type=order.type_sale,
                partner_id=partner_id,
                payment_token=payment_token,
                payment_state=payment_state
            )

            return request.make_response(
                json.dumps({
                        'id': payment_details.id,
                        'transaction_id': payment_details.transaction_id,
                        'amount': payment_details.amount,
                        'currency': payment_details.currency,
                        'payment_method': payment_details.payment_method,
                        'payment_date': payment_details.payment_date.isoformat(),
                        'order_id': payment_details.order_id,
                        'order_name': payment_details.order_name,
                        'order_type': payment_details.order_type,
                        'partner_id': payment_details.partner_id,
                        'payment_token': payment_details.payment_token,
                        'url_facture': payment_details.url_facture,
                        'customer_name' : payment_details.customer_name,
                        'customer_email' : payment_details.customer_email,
                        'customer_phone' : payment_details.customer_phone,
                        'payment_state': payment_details.payment_state,}),
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
    @http.route('/api/payment/get/<transaction>', methods=['GET'], type='http', auth='none', cors='*')
    def get_payment_details(self, transaction, **kw):
        try:
            # payment_details = request.env['payment.details'].sudo().get_payment_details(transaction)
            payment_details = request.env['payment.details'].sudo().search([('transaction_id', '=', transaction)], limit=1)
            if payment_details:
                return request.make_response(
                    json.dumps({
                        'id': payment_details.id,
                        'transaction_id': payment_details.transaction_id,
                        'amount': payment_details.amount,
                        'currency': payment_details.currency,
                        'payment_method': payment_details.payment_method,
                        'payment_date': payment_details.payment_date.isoformat(),
                        'order_id': payment_details.order_id,
                        'order_name': payment_details.order_name,
                        'order_type': payment_details.order_type,
                        'partner_id': payment_details.partner_id.id,
                        'partner_name': payment_details.partner_id.name,
                        'payment_token': payment_details.payment_token,
                        'payment_state': payment_details.payment_state,
                        'url_facture': payment_details.url_facture,
                        'customer_name' : payment_details.customer_name,
                        'customer_email' : payment_details.customer_email,
                        'customer_phone' : payment_details.customer_phone,
                    }),
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

    @http.route('/api/payment/partner/<id>', methods=['GET'], type='http', auth='none', cors='*')
    def get_payment_partner(self, id, **kw):
        try:
            payment_details = request.env['payment.details'].sudo().get_payment_partner(id)
            resp = werkzeug.wrappers.Response(
                status=200,
                content_type='application/json; charset=utf-8',
                headers=[('Cache-Control', 'no-store'), ('Pragma', 'no-cache')],
                response=json.dumps(payment_details)
            )
            return resp

        except Exception as e:
            return request.make_response(
                json.dumps({"error": str(e)}),
                status=400,
                headers={'Content-Type': 'application/json'}
            )


    @http.route('/api/payment/byId/<id>', methods=['GET'], type='http', auth='none', cors='*')
    def get_payment_by_id(self, id, **kw):
        try:
            payment_details = request.env['payment.details'].sudo().search([('id', '=', id)], limit=1)
            return request.make_response(
                    json.dumps({
                        'id': payment_details.id,
                        'transaction_id': payment_details.transaction_id,
                        'amount': payment_details.amount,
                        'currency': payment_details.currency,
                        'payment_method': payment_details.payment_method,
                        'payment_date':  payment_details.payment_date.isoformat() if payment_details.payment_date else None,
                        'order_id': payment_details.order_id,
                        'order_name': payment_details.order_name,
                        'order_type': payment_details.order_type,
                        'partner_id': payment_details.partner_id,
                        'payment_token': payment_details.payment_token,
                        'payment_state': payment_details.payment_state,
                        'url_facture': payment_details.url_facture,
                        'customer_name' : payment_details.customer_name,
                        'customer_email' : payment_details.customer_email,
                        'customer_phone' : payment_details.customer_phone,
                    }),
                    status=200,
                    headers={'Content-Type': 'application/json'}
                )

        except Exception as e:
            return request.make_response(
                json.dumps({"error": str(e)}),
                status=400,
                headers={'Content-Type': 'application/json'}
            )



    @http.route('/api/payment/byOrder/<order_id>', methods=['GET'], type='http', auth='none', cors='*')
    def get_payment_by_name_order(self, order_id, **kw):
        try:
            order = request.env['sale.order'].sudo().search([('id','=', order_id )], limit=1)
            if not order:
                return request.make_response(
                    json.dumps({"error": "Order not found"}),
                    status=404,
                    headers={'Content-Type': 'application/json'}
                )
            if order:
                if order.type_sale == "preorder":
                    payment_details = request.env['payment.details'].sudo().search([('order_id', '=', order_id),( 'payment_state', '=', 'completed' )])
                    resultat = []
                    for payment in payment_details:
                        resultat.append({
                            'id': payment.id,
                            'transaction_id': payment.transaction_id,
                            'amount': payment.amount,
                            'currency': payment.currency,
                            'payment_method': payment.payment_method,
                            'payment_date':  payment.payment_date.isoformat() if payment.payment_date else None,
                            'order_id': payment.order_id,
                            'order_name': payment.order_name,
                            'order_type': payment.order_type,
                            'partner_id': payment.partner_id,
                            'payment_token': payment.payment_token,
                            'payment_state': payment.payment_state,
                            'url_facture': payment.url_facture,
                            'customer_name' : payment.customer_name,
                            'customer_email' : payment.customer_email,
                            'customer_phone' : payment.customer_phone,
                        })
                    return request.make_response(
                        json.dumps(resultat),
                        status=200,
                        headers={'Content-Type': 'application/json'}
                    )
                else:
                    payment_details = request.env['payment.details'].sudo().search([('order_id', '=', order_id)], limit=1)
                    return request.make_response(
                            json.dumps({
                                'id': payment_details.id,
                                'transaction_id': payment_details.transaction_id,
                                'amount': payment_details.amount,
                                'currency': payment_details.currency,
                                'payment_method': payment_details.payment_method,
                                'payment_date':  payment_details.payment_date.isoformat() if payment_details.payment_date else None,
                                'order_id': payment_details.order_id,
                                'order_name': payment_details.order_name,
                                'order_type': payment_details.order_type,
                                'partner_id': payment_details.partner_id,
                                'payment_token': payment_details.payment_token,
                                'payment_state': payment_details.payment_state,
                                'url_facture': payment_details.url_facture,
                                'customer_name' : payment_details.customer_name,
                                'customer_email' : payment_details.customer_email,
                                'customer_phone' : payment_details.customer_phone,
                            }),
                            status=200,
                            headers={'Content-Type': 'application/json'}
                        )

        except Exception as e:
            return request.make_response(
                json.dumps({"error": str(e)}),
                status=400,
                headers={'Content-Type': 'application/json'}
            )
        

    @http.route('/api/payment/byToken/<token>', methods=['GET'], type='http', auth='none', cors='*')
    def get_payment_by_token(self, token, **kw):
        try:
            payment_details = request.env['payment.details'].sudo().search([('payment_token', '=', token)], limit=1)
            if not payment_details:
                return request.make_response(
                    json.dumps({"error": "Payment details not found"}),
                    status=404,
                    headers={'Content-Type': 'application/json'}
                )
            else:
                return request.make_response(
                        json.dumps({
                            'id': payment_details.id,
                            'transaction_id': payment_details.transaction_id,
                            'amount': payment_details.amount,
                            'currency': payment_details.currency,
                            'payment_method': payment_details.payment_method,
                            'payment_date':  payment_details.payment_date.isoformat() if payment_details.payment_date else None,
                            'order_id': payment_details.order_id,
                            'order_name': payment_details.order_name,
                            'order_type': payment_details.order_type,
                            'partner_id': payment_details.partner_id,
                            'payment_token': payment_details.payment_token,
                            'payment_state': payment_details.payment_state,
                            'url_facture': payment_details.url_facture,
                            'customer_name' : payment_details.customer_name,
                            'customer_email' : payment_details.customer_email,
                            'customer_phone' : payment_details.customer_phone,
                        }),
                        status=200,
                        headers={'Content-Type': 'application/json'}
                    )

        except Exception as e:
            return request.make_response(
                json.dumps({"error": str(e)}),
                status=400,
                headers={'Content-Type': 'application/json'}
            )


    @http.route('/api/payment/update/<id>', methods=['PUT'], type='http', auth='none', cors='*' ,csrf=False)
    def update_payment_by_id(self, id, **kw):
        try:
            data = json.loads(request.httprequest.data)
            payment_state = data.get('payment_state')
            url_facture = data.get('url_facture')
            customer_name  = data.get('customer_name') , 
            customer_email = data.get('customer_email'),
            customer_phone = data.get('customer_phone'),
            payment_date = datetime.datetime.now()

            payment_details = request.env['payment.details'].sudo().search([('id', '=', id)], limit=1)
            if payment_details.payment_state == "completed":
                return request.make_response(
                   json.dumps({
                        'id': payment_details.id,
                        'transaction_id': payment_details.transaction_id,
                        'amount': payment_details.amount,
                        'currency': payment_details.currency,
                        'payment_method': payment_details.payment_method,
                        'payment_date':  payment_details.payment_date.isoformat() if payment_details.payment_date else None,
                        'order_id': payment_details.order_id,
                        'order_name': payment_details.order_name,
                        'order_type': payment_details.order_type,
                        'partner_id': payment_details.partner_id,
                        'payment_token': payment_details.payment_token,
                        'payment_state': payment_details.payment_state,
                        'url_facture': payment_details.url_facture,
                        'customer_name' : payment_details.customer_name,
                        'customer_email' : payment_details.customer_email,
                        'customer_phone' : payment_details.customer_phone,
                    }),
                    status=200,
                    headers={'Content-Type': 'application/json'}
                )

            if not payment_details:
                return request.make_response(
                    json.dumps({"error": "Payment details not found"}),
                    status=404,
                    headers={'Content-Type': 'application/json'}
                )

            # Mettre à jour les champs avec les nouvelles valeurs
            payment_details.write({
                'payment_state': payment_state,
                'payment_date': payment_date,
                'url_facture': url_facture,
                'customer_name' : customer_name,
                'customer_email' : customer_email,
                'customer_phone' : customer_phone,
            })

            return request.make_response(
                json.dumps({
                        'id': payment_details.id,
                        'transaction_id': payment_details.transaction_id,
                        'amount': payment_details.amount,
                        'currency': payment_details.currency,
                        'payment_method': payment_details.payment_method,
                        'payment_date':  payment_details.payment_date.isoformat() if payment_details.payment_date else None,
                        'order_id': payment_details.order_id,
                        'order_name': payment_details.order_name,
                        'order_type': payment_details.order_type,
                        'partner_id': payment_details.partner_id,
                        'payment_token': payment_details.payment_token,
                        'payment_state': payment_details.payment_state,
                        'url_facture': payment_details.url_facture,
                        'customer_name' : payment_details.customer_name,
                        'customer_email' : payment_details.customer_email,
                        'customer_phone' : payment_details.customer_phone,
                    }),
                    status=200,
                    headers={'Content-Type': 'application/json'}
                )

        except Exception as e:
            return request.make_response(
                json.dumps({"error": str(e)}),
                status=400,
                headers={'Content-Type': 'application/json'}
            )