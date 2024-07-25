# -*- coding: utf-8 -*-
from .main import *
import pdb
import datetime

_logger = logging.getLogger(__name__)


class userREST(http.Controller):

    @http.route('/api/users/<id>', methods=['GET'], type='http', auth='none', cors="*")
    def api_users_GET(self, id , **kw):
        if id:
            user = request.env['res.users'].sudo().search([('id','=',id)])
            if user:
                user_data = {
                    'id': user.id,
                    'name': user.name,
                    'email': user.email,
                    'login': user.login,
                    'partner_id': user.partner_id.id or None,
                    'partner_name': user.partner_id.name or None,
                    'partner_street': user.partner_id.street or None,
                    'partner_street2': user.partner_id.street2 or None,
                    'partner_city': user.partner_id.city or None,
                    'partner_state_id': user.partner_id.state_id.id or None,
                    'partner_state_name': user.partner_id.state_id.name or None,
                    'partner_zip': user.partner_id.zip or None,
                    'partner_country_id': user.partner_id.country_id.id or None,
                    'partner_country_name': user.partner_id.country_id.name or None,
                    'partner_vat': user.partner_id.vat or None,
                    'partner_email': user.partner_id.email or None,
                    'partner_phone': user.partner_id.phone or None,
                    'company_id': user.company_id.id or None,
                    'company_name': user.company_id.name or None,
                    'company_street': user.company_id.street or None,
                    'company_street2': user.company_id.street2 or None,
                    'company_city': user.company_id.city or None,
                    'company_state_id': user.company_id.state_id.id or None,
                    'company_state_name': user.company_id.state_id.name or None,
                    'company_zip': user.company_id.zip or None,
                    'company_country_id': user.company_id.country_id.id or None,
                    'company_country_name': user.company_id.country_id.name or None,
                    'company_vat': user.company_id.vat or None,
                    'company_email': user.company_id.email or None,
                    'company_phone': user.company_id.phone or None
                }

                resp = werkzeug.wrappers.Response(
                    status=200,
                    content_type='application/json; charset=utf-8',
                    headers=[('Cache-Control', 'no-store'), ('Pragma', 'no-cache')],
                    response=json.dumps(user_data)
                )
                return resp
            return  werkzeug.wrappers.Response(
                status=404,
                content_type='application/json; charset=utf-8',
                headers=[('Cache-Control', 'no-store'), ('Pragma', 'no-cache')],
                response=json.dumps("Utilisateur non trouvée")
            )
        return  werkzeug.wrappers.Response(
            status=400,
            content_type='application/json; charset=utf-8',
            headers=[('Cache-Control', 'no-store'), ('Pragma', 'no-cache')],
            response=json.dumps("user_id est obligatoire")
        )


    @http.route('/api/users', methods=['POST'],auth="public"  , type='http', cors="*", csrf=False)
    @check_permissions
    def api_users_POST(self, **kw):
        data = json.loads(request.httprequest.data)
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        # company_name = data.get('company_name')
        city = data.get('city')
        phone = data.get('phone')


        if data:
           
            company = request.env['res.company'].sudo().search([('id', '=', 1)], limit=1)
            country = request.env['res.country'].sudo().search([ ('id' , '=' , 204 ) ] , limit = 1 )
           
            # Création du partenaire
            partner_email = request.env['res.partner'].sudo().search([('email', '=', email)], limit=1)
            user_email = request.env['res.users'].sudo().search([('login', '=', email)], limit=1)
            if partner_email or user_email:
                return werkzeug.wrappers.Response(
                    status=400,
                    content_type='application/json; charset=utf-8',
                    headers=[('Cache-Control', 'no-store'), ('Pragma', 'no-cache')],
                    response=json.dumps("Utilisateur avec cet adresse mail existe déjà")
                )
            partner_phone =  request.env['res.partner'].sudo().search([('phone', '=', phone)], limit=1)

            if partner_phone :
                return werkzeug.wrappers.Response(
                    status=409,
                    content_type='application/json; charset=utf-8',
                    headers=[('Cache-Control', 'no-store'), ('Pragma', 'no-cache')],
                    response=json.dumps("Utilisateur avec ce numero téléphone existe déjà")
                )
            if not partner_email and not user_email:
                partner = request.env['res.partner'].sudo().create({
                    'name': name,
                    'email': email,
                    'customer_rank': 1,
                    'company_id': company.id,
                    'city': city,
                    'phone': phone,
                    'is_company': False,
                    'active' : True,
                    'type': 'contact',
                    'company_name': company.name,
                    'country_id': country.id or None,
                })
                # Création de l'utilisateur
                user = request.env['res.users'].sudo().create({
                    'login': email,
                    'password': password,
                    'partner_id': partner.id,
                    'active': True,
                    # 'karma': 0,
                    'notification_type': 'email',
                    'company_id': partner.company_id.id,
                    'company_ids': [partner.company_id.id],
                    'create_uid': 1
                })

                if user:
                    partner.write({
                        'user_id': user.id
                    })
                    resp = werkzeug.wrappers.Response(
                        status=201,
                        content_type='application/json; charset=utf-8',
                        headers=[('Cache-Control', 'no-store'), ('Pragma', 'no-cache')],
                        response=json.dumps({
                            'id': user.id,
                            'name': user.name,
                            'email': user.email,
                            'partner_id': user.partner_id.id,
                            'company_id': user.company_id.id,
                            'company_name': user.company_id.name,
                            'partner_city': user.partner_id.city,
                            'partner_phone': user.partner_id.phone,
                            'country_id': user.partner_id.country_id.id or None,
                            'country_name': user.partner_id.country_id.name or None,
                            'country_code': user.partner_id.country_id.code,
                            'country_phone_code': user.partner_id.country_id.phone_code,
                        })
                    )
                    return resp
                return werkzeug.wrappers.Response(
                    status=400,
                    content_type='application/json; charset=utf-8',
                    headers=[('Cache-Control', 'no-store'), ('Pragma', 'no-cache')],
                    response=json.dumps({'message': "Erreur lors de la création de l'utilisateur"})
                )
            return werkzeug.wrappers.Response(
                status=400,
                content_type='application/json; charset=utf-8',
                headers=[('Cache-Control', 'no-store'), ('Pragma', 'no-cache')],
                response=json.dumps({'message': 'L\'utilisateur existe déjà'})
            )
        return werkzeug.wrappers.Response(
            status=400,
            content_type='application/json; charset=utf-8',
            headers=[('Cache-Control', 'no-store'), ('Pragma', 'no-cache')],
            response=json.dumps({'message': 'Données invalides'})
        )

    @http.route('/api/users/<id>/compte', methods=['GET'],  type='http', auth='none', cors="*")
    def api_users_compte(self, id):
        partner = request.env['res.partner'].sudo().search( [ ('id', '=' , id)] , limit=1)
        order_obj = request.env['sale.order']
        if partner:
           
            # Compter les commandes de type "order"
            order_count = order_obj.sudo().search_count([('partner_id.id', '=', partner.id), ('state', 'not in', ['cancel', 'draft']), ('type_sale', '=', 'order')])

            # Compter les commandes de type "preorder"
            preorder_count = order_obj.sudo().search_count([('partner_id.id', '=', partner.id), ('state', 'not in', ['cancel', 'draft']), ('type_sale', '=', 'preorder')])

            # Compter les commandes livrées
            delivered_count = order_obj.sudo().search_count([('partner_id.id', '=', partner.id), ('state', '=', 'done')])

            # Compter les commandes en cours
            progress_count = order_obj.sudo().search_count([('partner_id.id', '=', partner.id), ('state', 'in', ['progress', 'manual_progress']), ('type_sale', 'in', ['order', 'preorder'])])
           
            return http.Response(json.dumps({
                'user_name': partner.name,
                'order_count': order_count,
                'preorder_count': preorder_count,
                'delivered_count': delivered_count,
                'progress_count': progress_count,
            }), content_type='application/json')
        else:
            return http.Response(json.dumps({
                'message': 'Utilisateur introuvable'
            }), content_type='application/json')
        

    @http.route('/api/users/<int:id>/update', methods=['PUT'], type='http', auth='none', cors='*', csrf=False)
    def api_users_POST(self, id, **kw):
        data = json.loads(request.httprequest.data)
        name = data.get('name')
        city = data.get('city')
        phone = data.get('phone')

        if data:
            country = request.env['res.country'].sudo().search([ ('id' , '=' , 204 ) ] , limit = 1 )
            partner_phone = request.env['res.partner'].sudo().search([('phone', '=', phone), ('id', '!=', id)], limit=1)
            partner = request.env['res.partner'].sudo().search([ ('id', '=', id)], limit=1)

            if partner and partner_phone.phone != phone:
                partner.write({
                    'name': name,
                    'city': city,
                    'phone': phone,
                    'country_id': country.id or None,
                })
                # Mise à jour de l'utilisateur associé au partenaire
                user = request.env['res.users'].sudo().search([('partner_id', '=', partner.id)], limit=1)
                if user:
                    user.write({
                        'name': name,
                    })

                resp = werkzeug.wrappers.Response(
                    status=200,
                    content_type='application/json; charset=utf-8',
                    headers=[('Cache-Control', 'no-store'), ('Pragma', 'no-cache')],
                    response=json.dumps({
                        'id': user.id,
                        'name': partner.name,
                        'email': partner.email,
                        'partner_id': partner.id,
                        'company_id': partner.company_id.id,
                        'company_name': user.company_id.name,
                        'partner_city': partner.city,
                        'partner_phone': partner.phone,
                        'country_id': partner.country_id.id or None,
                        'country_name': partner.country_id.name or None,
                        'country_code': partner.country_id.code,
                        'country_phone_code': partner.country_id.phone_code,
                    })
                )
                return resp
            return werkzeug.wrappers.Response(
                status=400,
                content_type='application/json; charset=utf-8',
                headers=[('Cache-Control', 'no-store'), ('Pragma', 'no-cache')],
                response=json.dumps({'message': "Un compte avec ce numéro téléphone existe déjà"})
            )
        return werkzeug.wrappers.Response(
            status=400,
            content_type='application/json; charset=utf-8',
            headers=[('Cache-Control', 'no-store'), ('Pragma', 'no-cache')],
            response=json.dumps({'message': 'Données invalides'})
        )
