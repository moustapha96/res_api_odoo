# -*- coding: utf-8 -*-
from .main import *
import pdb
import datetime

_logger = logging.getLogger(__name__)


class ControllerREST(http.Controller):
    
    def send_verification_mail(self, email):
        # Récupérer ou créer une instance de IrMailServer
        mail_server = request.env['ir.mail_server'].sudo().search([], limit=1)

        # Récupérer l'utilisateur associé à l'adresse e-mail
        user = request.env['res.users'].sudo().search([('email', '=', email)], limit=1)
        if not user:
            return {'status': 'error', 'message': 'User not found for the given email'}

        # Construire le contenu de l'e-mail
        subject = 'Vérifiez votre compte'
       
        body_html = f'''
        <table border="0" cellpadding="0" cellspacing="0" style="padding-top: 16px; background-color: #FFFFFF; font-family:Verdana, Arial,sans-serif; color: #454748; width: 100%; border-collapse:separate;">
            <tr>
                <td align="center">
                    <table border="0" cellpadding="0" cellspacing="0" width="590" style="padding: 16px; background-color: #FFFFFF; color: #454748; border-collapse:separate;">
                        <tbody>
                            <tr>
                                <td align="center" style="min-width: 590px;">
                                    <table border="0" cellpadding="0" cellspacing="0" width="590" style="min-width: 590px; background-color: white; padding: 0px 8px 0px 8px; border-collapse:separate;">
                                        <tr>
                                            <td valign="middle">
                                                <span style="font-size: 10px;">Votre compte</span><br/>
                                                <span style="font-size: 20px; font-weight: bold;">
                                                    {user.name}
                                                </span>
                                            </td>
                                            <td valign="middle" align="right">
                                                <img style="padding: 0px; margin: 0px; height: auto; width: 80px;" src="https://ccbme.sn/logo.png" alt="logo CCBM SHOP"/>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td colspan="2" style="text-align:center;">
                                                <hr width="100%" style="background-color:rgb(204,204,204);border:medium none;clear:both;display:block;font-size:0px;min-height:1px;line-height:0; margin: 16px 0px 16px 0px;"/>
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                            <tr>
                                <td align="center" style="min-width: 590px;">
                                    <table border="0" cellpadding="0" cellspacing="0" width="590" style="min-width: 590px; background-color: white; padding: 0px 8px 0px 8px; border-collapse:separate;">
                                        <tr>
                                            <td valign="top" style="font-size: 13px;">
                                                <div>
                                                    Cher {user.name},<br/><br/>
                                                    Votre compte a été créé avec succès !<br/>
                                                    Votre identifiant est <strong>{user.email}</strong><br/>
                                                    Pour accéder à votre compte, vous pouvez utiliser le lien suivant :
                                                    <div style="margin: 16px 0px 16px 0px;">
                                                        <a style="background-color: #875A7B; padding: 8px 16px 8px 16px; text-decoration: none; color: #fff; border-radius: 5px; font-size:13px;" href="https://ccbme.sn/login?mail={user.email}&isVerified=1&token={user.id}">
                                                            Aller à Mon compte
                                                        </a>
                                                    </div>
                                                    Merci,<br/>
                                                </div>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td style="text-align:center;">
                                                <hr width="100%" style="background-color:rgb(204,204,204);border:medium none;clear:both;display:block;font-size:0px;min-height:1px;line-height:0; margin: 16px 0px 16px 0px;"/>
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                            <tr>
                                <td align="center" style="min-width: 590px;">
                                    <table border="0" cellpadding="0" cellspacing="0" width="590" style="min-width: 590px; background-color: white; font-size: 11px; padding: 0px 8px 0px 8px; border-collapse:separate;">
                                        <tr>
                                            <td valign="middle" align="left">
                                               {user.company_id.name}
                                            </td>
                                        </tr>
                                        <tr>
                                            <td valign="middle" align="left" style="opacity: 0.7;">
                                               {user.company_id.phone}
                                                | <a style="text-decoration:none; color: #454748;" href="mailto:{user.company_id.email}">{user.company_id.email}</a>
                                                | 
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </td>
            </tr>
            <tr>
                <td align="center" style="min-width: 590px;">
                    <table border="0" cellpadding="0" cellspacing="0" width="590" style="min-width: 590px; background-color: #F1F1F1; color: #454748; padding: 8px; border-collapse:separate;">
                        <tr>
                            <td style="text-align: center; font-size: 13px;">
                                Généré par <a target="_blank" href="https://ccbme.sn" style="color: #875A7B;">Orbit City</a>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
        '''

        email_from = mail_server.smtp_user
        email_to = email

        mail_server = request.env['ir.mail_server'].sudo().search([], limit=1)
        # Définir les valeurs du message e-mail
        email_values = {
            'email_from': email_from,
            'email_to': email_to,
            'subject': subject,
            'body_html': body_html,
            'state': 'outgoing',
        }
        # Construire le message e-mail
        mail_mail = request.env['mail.mail'].sudo().create(email_values)

        try:
            # mail_server.send_email(message)
            mail_mail.send()
            return {'status': 'succes', 'message': 'Mail envoyé avec succès'}
        except Exception as e:
            _logger.error(f'Error sending email: {str(e)}')
            return {'status': 'error', 'message': str(e)}
    
    def set_verification_status(self, email, is_verified):
        # Stocker la valeur de isVerified dans ir.config_parameter
        request.env['ir.config_parameter'].sudo().set_param(f'user_verification_{email}', is_verified)

    def get_verification_status(self, email):
        # Récupérer la valeur de isVerified depuis ir.config_parameter
        return request.env['ir.config_parameter'].sudo().get_param(f'user_verification_{email}')
    
    def set_user_avatar(self, email, avatar):
        # Stocker la valeur de isVerified dans ir.config_parameter
        request.env['ir.config_parameter'].sudo().set_param(f'user_avatar_{email}', avatar)

    def get_user_avatar(self, email):
        # Récupérer la valeur de isVerified depuis ir.config_parameter
        return request.env['ir.config_parameter'].sudo().get_param(f'user_avatar_{email}')
    
    def define_schema_params(self, request, model_name, method):
        schema = pre_schema = default_vals = None
        cr, uid = request.cr, request.session.uid
        Model = request.env['ir.model'].sudo().search([('model', '=', model_name)], limit=1)
        ResModel = request.env(cr, uid)[model_name]
        if Model.rest_api__used:
            model_available = True
            if method == 'read_all':
                if Model.rest_api__read_all__schema:
                    schema = literal_eval(Model.rest_api__read_all__schema)
                    pre_schema = True
                else:
                    if 'name' in ResModel._fields.keys():
                        schema = ('id', 'name',)
                    else:
                        schema = ('id',)
                    pre_schema = False
            elif method == 'read_one':
                if Model.rest_api__read_one__schema:
                    schema = literal_eval(Model.rest_api__read_one__schema)
                    pre_schema = True
                else:
                    schema = tuple(ResModel._fields.keys())
                    pre_schema = False
            elif method == 'create_one':
                if Model.rest_api__create_one__schema:
                    schema = literal_eval(Model.rest_api__create_one__schema)
                    pre_schema = True
                else:
                    schema = ('id',)
                    pre_schema = False
                default_vals = literal_eval(Model.rest_api__create_one__defaults or '{}')
        else:
            model_available = False
        return model_available, schema, pre_schema, default_vals
    
    # Read all (with optional filters, offset, limit, order, exclude_fields, include_fields):
    @http.route('/api/<string:model_name>', methods=['GET'], type='http', auth='none', cors=rest_cors_value)
    @check_permissions
    def api__model_name__GET(self, model_name, **kw):
        model_available, schema, pre_schema, _ = self.define_schema_params(request, model_name, 'read_all')
        if not model_available:
            return error_response_501__model_not_available()
        _logger.debug('schema == %s; pre_schema == %s' % (schema, pre_schema))
        return wrap__resource__read_all(
            modelname = model_name,
            default_domain = [],
            success_code = 200,
            OUT_fields = schema,
            pre_schema = pre_schema,
        )
    
    # Read one (with optional exclude_fields, include_fields):
    @http.route('/api/<string:model_name>/<id>', methods=['GET'], type='http', auth='none', cors=rest_cors_value)
    @check_permissions
    def api__model_name__id_GET(self, model_name, id, **kw):
        model_available, schema, pre_schema, _ = self.define_schema_params(request, model_name, 'read_one')
        if not model_available:
            return error_response_501__model_not_available()
        _logger.debug('schema == %s; pre_schema == %s' % (schema, pre_schema))
        return wrap__resource__read_one(
            modelname = model_name,
            id = id,
            success_code = 200,
            OUT_fields = schema,
            pre_schema = pre_schema,
        )
    
    # Create one:
    @http.route('/api/<string:model_name>', methods=['POST'], type='http', auth='none', cors=rest_cors_value, csrf=False)
    @check_permissions
    def api__model_name__POST(self, model_name, **kw):
        model_available, schema, _, default_vals = self.define_schema_params(request, model_name, 'create_one')
        if not model_available:
            return error_response_501__model_not_available()
        _logger.debug('schema == %s; default_vals == %s' % (schema, default_vals))
        return wrap__resource__create_one(
            modelname = model_name,
            default_vals = default_vals,
            success_code = 200,
            OUT_fields = schema,
        )
    
    # Update one:
    @http.route('/api/<string:model_name>/<id>', methods=['PUT'], type='http', auth='none', cors=rest_cors_value, csrf=False)
    @check_permissions
    def api__model_name__id_PUT(self, model_name, id, **kw):
        return wrap__resource__update_one(
            modelname = model_name,
            id = id,
            success_code = 200,
        )

    # Delete one:
    @http.route('/api/<string:model_name>/<id>', methods=['DELETE'], type='http', auth='none', cors=rest_cors_value, csrf=False)
    @check_permissions
    def api__model_name__id_DELETE(self, model_name, id, **kw):
        return wrap__resource__delete_one(
            modelname = model_name,
            id = id,
            success_code = 200,
        )

    # Call method (with optional parameters):
    @http.route('/api/<string:model_name>/<id>/<method>', methods=['PUT'], type='http', auth='none', cors=rest_cors_value, csrf=False)
    @check_permissions
    def api__model_name__id__method_PUT(self, model_name, id, method, **kw):
        return wrap__resource__call_method(
            modelname = model_name,
            id = id,
            method = method,
            success_code = 200,
        )


    @http.route('/api/categories', methods=['GET'], type='http', auth='none', cors="*")
    def api__categories_GET(self, **kw):
        categories = request.env['product.category'].sudo().search([])
        categories_data = []
        if categories: 
            for category in categories:
                categories_data.append({
                    'id': category.id,
                    'name': category.name,
                })

            resp = werkzeug.wrappers.Response(
                status=200,
                content_type='application/json; charset=utf-8',
                headers=[('Cache-Control', 'no-store'), ('Pragma', 'no-cache')],
                response=json.dumps(categories_data)
            )
            return resp
        
        return  werkzeug.wrappers.Response(
            status=200,
            content_type='application/json; charset=utf-8',
            headers=[('Cache-Control', 'no-store'), ('Pragma', 'no-cache')],
            response=json.dumps("pas de données")  )

    @http.route('/api/produits', methods=['GET'], type='http', auth='none', cors="*")
    def api__products_GET(self, **kw):
        products = request.env['product.product'].sudo().search([('sale_ok', '=', True)])
        product_data = []
        if products:
            for p in products:
                product_data.append({
                'id': p.id,
                'name': p.name,
                'display_name': p.display_name,
                # 'avg_cost': p.avg_cost,
                'quantite_en_stock': p.qty_available,
                'quantity_reception':p.incoming_qty,
                'quanitty_virtuelle_disponible': p.free_qty,
                'quanitty_commande': p.outgoing_qty,
                'quanitty_prevu': p.virtual_available,
                'image_1920': p.image_1920,
                'image_128' : p.image_128,
                'image_1024': p.image_1024,
                'image_512': p.image_512,
                'image_256': p.image_256,
                'categ_id': p.categ_id.name,
                'type': p.type,
                'description': p.product_tmpl_id.description,
                'en_promo' : p.product_tmpl_id.en_promo,
                'list_price': p.list_price,
                'volume': p.volume,
                'weight': p.weight,
                'sale_ok': p.sale_ok,
                'standard_price': p.standard_price,
                'active': p.active,
                'is_preorder': p.product_tmpl_id.is_preorder,
                'preorder_price': p.product_tmpl_id.preorder_price,
                # 'ttc_price': p.product_tmpl_id.ttc_price
            })

            resp = werkzeug.wrappers.Response(
                status=200,
                content_type='application/json; charset=utf-8',
                headers=[('Cache-Control', 'no-store'), ('Pragma', 'no-cache')],
                response=json.dumps(product_data)
            )
            return resp
        return  werkzeug.wrappers.Response(
            status=200,
            content_type='application/json; charset=utf-8',
            headers=[('Cache-Control', 'no-store'), ('Pragma', 'no-cache')],
            response=json.dumps("pas de données")  )



    @http.route('/api/produits-precommande', methods=['GET'], type='http', auth='none', cors="*")
    def api__products__precommande_GET(self, **kw):
        products = request.env['product.product'].sudo().search([('sale_ok', '=', True), ( 'is_preorder', '=', True ) ])
        product_data = []
        if products:
            for p in products:

                product_data.append({
                'id': p.id,
                'name': p.name,
                'display_name': p.display_name,
                # 'avg_cost': p.avg_cost,
                'quantite_en_stock': p.qty_available,
                'quantity_reception':p.incoming_qty,
                'quanitty_virtuelle_disponible': p.free_qty,
                'quanitty_commande': p.outgoing_qty,
                'quanitty_prevu': p.virtual_available,
                'image_1920': p.image_1920,
                'image_128' : p.image_128,
                'image_1024': p.image_1024,
                'image_512': p.image_512,
                'image_256': p.image_256,
                'categ_id': p.categ_id.name,
                'type': p.type,
                'description': p.product_tmpl_id.description,
                'en_promo' : p.product_tmpl_id.en_promo,
                'list_price': p.list_price,
                'volume': p.volume,
                'weight': p.weight,
                'sale_ok': p.sale_ok,
                'standard_price': p.standard_price,
                'active': p.active,
                'is_preorder': p.product_tmpl_id.is_preorder,
                'preorder_price': p.product_tmpl_id.preorder_price,
                # 'ttc_price': p.product_tmpl_id.ttc_price
            })

            resp = werkzeug.wrappers.Response(
                status=200,
                content_type='application/json; charset=utf-8',
                headers=[('Cache-Control', 'no-store'), ('Pragma', 'no-cache')],
                response=json.dumps(product_data)
            )
            return resp
        return  werkzeug.wrappers.Response(
            status=200,
            content_type='application/json; charset=utf-8',
            headers=[('Cache-Control', 'no-store'), ('Pragma', 'no-cache')],
            response=json.dumps("pas de données")  )

    @http.route('/api/produits/<id>', methods=['GET'], type='http', auth='none', cors="*")
    def api__products__one_GET(self,id, **kw):
        p = request.env['product.product'].sudo().search([ ( 'id' , '=' , id ),('sale_ok', '=', True) ])
        if p:
            produit_data = {
                'id': p.id,
                'name': p.name,
                'image_1920': p.image_1920,
                'image_128' : p.image_128,
                'image_1024': p.image_1024,
                'image_512': p.image_512,
                'image_256': p.image_256,
                'categ_id': p.categ_id.name,
                'type': p.type,
                'description': p.description,
                'list_price': p.list_price,
                'volume': p.volume,
                'weight': p.weight,
                'sale_ok': p.sale_ok,
                'standard_price': p.standard_price,
                'active': p.active,
                'en_promo' : p.product_tmpl_id.en_promo,
                'is_preorder': p.product_tmpl_id.is_preorder,
                'preorder_price': p.product_tmpl_id.preorder_price,
                # 'ttc_price': p.product_tmpl_id.ttc_price
            }

            resp = werkzeug.wrappers.Response(
                status=200,
                content_type='application/json; charset=utf-8',
                headers=[('Cache-Control', 'no-store'), ('Pragma', 'no-cache')],
                response=json.dumps(produit_data)
            )
            return resp
        return  werkzeug.wrappers.Response(
            status=200,
            content_type='application/json; charset=utf-8',
            headers=[('Cache-Control', 'no-store'), ('Pragma', 'no-cache')],
            response=json.dumps("pas de données")  )

    @http.route('/api/produits/flash',   methods=['GET'],  type='http', auth='none' , cors="*")
    def api_flash_produits_get(self, **kw):
        products = request.env['product.product'].sudo().search([ ('sale_ok', '=', True), ('active', '=', True)])
        product_data = []
        if products:
            for p in products:
                product_data.append({
                'id': p.id,
                'name': p.name,
                'display_name': p.display_name,
                'quantite_en_stock': p.qty_available,
                'quantity_reception':p.incoming_qty,
                'quanitty_virtuelle_disponible': p.free_qty,
                'quanitty_commande': p.outgoing_qty,
                'quanitty_prevu': p.virtual_available,
                'image_1920': p.image_1920,
                'image_128' : p.image_128,
                'image_1024': p.image_1024,
                'image_512': p.image_512,
                'image_256': p.image_256,
                'categ_id': p.categ_id.name,
                'type': p.type,
                'description': p.description,
                'list_price': p.list_price,
                'volume': p.volume,
                'weight': p.weight,
                'sale_ok': p.sale_ok,
                'standard_price': p.standard_price,
                'active': p.active,
                'en_promo' : p.product_tmpl_id.en_promo,
                'is_preorder': p.product_tmpl_id.is_preorder,
                'preorder_price': p.product_tmpl_id.preorder_price,
                # 'ttc_price': p.product_tmpl_id.ttc_price
            })
        resp = werkzeug.wrappers.Response(
                status=200,
                content_type='application/json; charset=utf-8',
                headers=[('Cache-Control', 'no-store'), ('Pragma', 'no-cache')],
                response=json.dumps(product_data)
            )
        return resp




    # Reccuperer la liste des stats
    @http.route('/api/state', methods=['GET'], type='http', auth='none', cors='*' )
    def api_state_get(self, **kw):
        countrys = request.env['res.country.state'].sudo().search([])
        country_data = []
        if countrys:
            for p in countrys:
                country_data.append({
                'id': p.id,
                'state_name': p.name,
                'state_id': p.id,
                'country_id': p.country_id.id,
                'phone': p.country_id.phone_code,
                'code' : p.code,
                'country_name': p.country_id.name
            })

            resp = werkzeug.wrappers.Response(
                status=200,
                content_type='application/json; charset=utf-8',
                headers=[('Cache-Control', 'no-store'), ('Pragma', 'no-cache')],
                response=json.dumps(country_data)
            )
            return resp
        return werkzeug.wrappers.Response(
                status=400,
                content_type='application/json; charset=utf-8',
                headers=[('Cache-Control', 'no-store'), ('Pragma', 'no-cache')],
                response=json.dumps("Erreur lors de la reccuperation des pays"))

    @http.route('/api/country', methods=['GET'], type='http', auth='none', cors='*' )
    def api_country_get(self, **kw):
        countrys = request.env['res.country'].sudo().search([])
        country_data = []
        if countrys:
            for p in countrys:
                country_data.append({
                'id': p.id,
                'phone': p.phone_code,
                'code' : p.code,
                'name': p.name
            })

            resp = werkzeug.wrappers.Response(
                status=200,
                content_type='application/json; charset=utf-8',
                headers=[('Cache-Control', 'no-store'), ('Pragma', 'no-cache')],
                response=json.dumps(country_data)
            )
            return resp
        return werkzeug.wrappers.Response(
                status=400,
                content_type='application/json; charset=utf-8',
                headers=[('Cache-Control', 'no-store'), ('Pragma', 'no-cache')],
                response=json.dumps("Erreur lors de la reccuperation des pays"))


    # @http.route('/api/new_compte',  methods=['POST'] , type='http', auth='none' , cors="*" , csrf=False )
    # def api_new_compte_post(self, **kw):
    #     data = json.loads(request.httprequest.data)
    #     if not data:
    #         return werkzeug.wrappers.Response(
    #             status=400,
    #             content_type='application/json; charset=utf-8',
    #             headers=[('Cache-Control', 'no-store'), ('Pragma', 'no-cache')],
    #             response=json.dumps("Données manquantes")
    #         )

    #     name = data.get('name')
    #     email = data.get('email')
    #     password = data.get('password')
    #     # company_name = data.get('company_name')
    #     city = data.get('city')
    #     phone = data.get('phone')

    #     company = request.env['res.company'].sudo().search([('id', '=', 1)], limit=1)
    #     country = request.env['res.country'].sudo().search([ ('id' , '=' , 204 ) ] , limit = 1 )

    #     partner_email = request.env['res.partner'].sudo().search([('email', '=', email)], limit=1)

    #     if partner_email :
    #         return werkzeug.wrappers.Response(
    #             status=400,
    #             content_type='application/json; charset=utf-8',
    #             headers=[('Cache-Control', 'no-store'), ('Pragma', 'no-cache')],
    #             response=json.dumps("Utilisateur avec cet adresse mail existe déjà")
    #         )
    #     # partner_phone =  request.env['res.partner'].sudo().search([('phone', '=', phone)], limit=1)
    #     # if partner_phone :
    #     #     return werkzeug.wrappers.Response(
    #     #         status=400,
    #     #         content_type='application/json; charset=utf-8',
    #     #         headers=[('Cache-Control', 'no-store'), ('Pragma', 'no-cache')],
    #     #         response=json.dumps("Utilisateur avec ce numero téléphone existe déjà")
    #     #     )
    #     if not partner_email :
    #         partner = request.env['res.partner'].sudo().create({
    #             'name': name,
    #             'email': email,
    #             'customer_rank': 1,
    #             'company_id': company.id,
    #             'city': city,
    #             'phone': phone,
    #             'is_company': False,
    #             'active' : True,
    #             'type': 'contact',
    #             'company_name': company.name,
    #             'country_id': country.id or None,
    #         })
    #         if partner:
    #             # Création de l'utilisateur
    #             user = request.env['res.users'].sudo().create({
    #                 'login': email,
    #                 'password': password,
    #                 'partner_id': partner.id,
    #                 'active': True,
    #                 # 'karma': 0,
    #                 'notification_type': 'email',
    #                 'company_id': partner.company_id.id,
    #                 'company_ids': [partner.company_id.id],
    #                 # 'create_uid': 1,
    #                 # 'share': True,
    #                 # 'is_web_user': True,
    #                 # 'groups_id': [(6, 0, [request.env.ref('base.group_portal').id])] or None
    #             })
    #             if user:
    #                 partner.write({
    #                     'user_id': user.id
    #                 })
    #                 self.send_verification_mail(user.email)
    #                 return werkzeug.wrappers.Response(
    #                     status=201,
    #                     content_type='application/json; charset=utf-8',
    #                     headers=[('Cache-Control', 'no-store'), ('Pragma', 'no-cache')],
    #                     response=json.dumps({
    #                         'id': user.id,
    #                         'name': user.name,
    #                         'email': user.email,
    #                         'partner_id': user.partner_id.id,
    #                         'company_id': user.company_id.id,
    #                         'company_name': user.company_id.name,
    #                         'partner_city': user.partner_id.city,
    #                         'partner_phone': user.partner_id.phone,
    #                         'country_id': user.partner_id.country_id.id or None,
    #                         'country_name': user.partner_id.country_id.name or None,
    #                         'country_code': user.partner_id.country_id.code,
    #                         'country_phone_code': user.partner_id.country_id.phone_code,
    #                         'is_verified' : self.get_verification_status(email) or None,
    #                         'avatar': self.get_user_avatar(email) or None,
    #                         'image_1920': user.partner_id.image_1920 or None
    #                     })
    #                 )

    #     return werkzeug.wrappers.Response(
    #         status=400,
    #         content_type='application/json; charset=utf-8',
    #         headers=[('Cache-Control', 'no-store'), ('Pragma', 'no-cache')],
    #         response=json.dumps(f"Compte client non créer")
    #     )
    @http.route('/api/new_compte', methods=['POST'], type='http', auth='none', cors="*", csrf=False)
    def api_new_compte_post(self, **kw):
        data = json.loads(request.httprequest.data)
        if not data:
            return werkzeug.wrappers.Response(
                status=400,
                content_type='application/json; charset=utf-8',
                headers=[('Cache-Control', 'no-store'), ('Pragma', 'no-cache')],
                response=json.dumps("Données manquantes")
            )

        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        city = data.get('city')
        phone = data.get('phone')

        company = request.env['res.company'].sudo().search([('id', '=', 1)], limit=1)
        country = request.env['res.country'].sudo().search([('id', '=', 204)], limit=1)

        partner_email = request.env['res.partner'].sudo().search([('email', '=', email)], limit=1)

        if partner_email:
            return werkzeug.wrappers.Response(
                status=400,
                content_type='application/json; charset=utf-8',
                headers=[('Cache-Control', 'no-store'), ('Pragma', 'no-cache')],
                response=json.dumps("Utilisateur avec cet adresse mail existe déjà")
            )
        partner_phone = request.env['res.partner'].sudo().search([('phone', '=', phone)], limit=1)
        if partner_phone:
            return werkzeug.wrappers.Response(
                status=400,
                content_type='application/json; charset=utf-8',
                headers=[('Cache-Control', 'no-store'), ('Pragma', 'no-cache')],
                response=json.dumps("Utilisateur avec ce numero téléphone existe déjà")
            )
        if not partner_email and not partner_phone:
            user = request.env['res.users'].sudo().search([('id', '=', request.env.uid)], limit=1)
            if not user or user._is_public():
                admin_user = request.env.ref('base.user_admin')
                request.env = request.env(user=admin_user.id)

            partner = request.env['res.partner'].sudo().create({
                'name': name,
                'email': email,
                'customer_rank': 1,
                'company_id': company.id,
                'city': city,
                'phone': phone,
                'is_company': False,
                'active': True,
                'type': 'contact',
                'company_name': company.name,
                'country_id': country.id or None,
            })
            if partner:
                # Création de l'utilisateur
                userc = request.env['res.users'].sudo().create({
                    'login': email,
                    'password': password,
                    'partner_id': partner.id,
                    'active': True,
                    'notification_type': 'email',
                    'company_id': partner.company_id.id,
                    'company_ids': [partner.company_id.id],
                })
                if userc:
                    partner.write({
                        'user_id': userc.id
                    })
                    self.send_verification_mail(userc.email)
                    return werkzeug.wrappers.Response(
                        status=201,
                        content_type='application/json; charset=utf-8',
                        headers=[('Cache-Control', 'no-store'), ('Pragma', 'no-cache')],
                        response=json.dumps({
                            'id': userc.id,
                            'name': userc.name,
                            'email': userc.email,
                            'partner_id': userc.partner_id.id,
                            'company_id': userc.company_id.id,
                            'company_name': userc.company_id.name,
                            'partner_city': userc.partner_id.city,
                            'partner_phone': userc.partner_id.phone,
                            'country_id': userc.partner_id.country_id.id or None,
                            'country_name': userc.partner_id.country_id.name or None,
                            'country_code': userc.partner_id.country_id.code,
                            'country_phone_code': userc.partner_id.country_id.phone_code,
                            'is_verified': self.get_verification_status(email) or None,
                            'avatar': self.get_user_avatar(email) or None,
                            'image_1920': userc.partner_id.image_1920 or None
                        })
                    )

        return werkzeug.wrappers.Response(
            status=400,
            content_type='application/json; charset=utf-8',
            headers=[('Cache-Control', 'no-store'), ('Pragma', 'no-cache')],
            response=json.dumps(f"Compte client non créer")
        )
