# -*- coding: utf-8 -*-
from .main import *
import pdb
import datetime

_logger = logging.getLogger(__name__)


class ControllerREST(http.Controller):
    
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
        products = request.env['product.product'].sudo().search([])
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
                'list_price': p.list_price,
                'volume': p.volume,
                'weight': p.weight,
                'sale_ok': p.sale_ok,
                'standard_price': p.standard_price,
                'active': p.active,
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
        p = request.env['product.product'].sudo().search([ ( 'id' , '=' , id ) ])
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
                'active': p.active
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
            })
        resp = werkzeug.wrappers.Response(
                status=200,
                content_type='application/json; charset=utf-8',
                headers=[('Cache-Control', 'no-store'), ('Pragma', 'no-cache')],
                response=json.dumps(product_data)
            )
        return resp



    # @http.route('/api/produits/last', methods=['GET'], type='http', auth='none', cors="*")
    # def api__products_GET_LAST(self, **kw):
    #     product_obj = request.env['product.product']  # Objet product.product
       
    #    # Rechercher les derniers produits créés
    #     last_products = product_obj.sudo().search_read([], [], order='create_date desc', limit=10)
        
    #     product_data = []
    #     if last_products:
    #         for p in last_products:

    #             product_data.append({
    #                 'id': p.id,
    #                 'name': p.name,
    #                 'display_name': p.display_name,
    #                 'quantite_en_stock': p.qty_available,
    #                 'quantity_reception':p.incoming_qty,
    #                 'quanitty_virtuelle_disponible': p.free_qty,
    #                 'quanitty_commande': p.outgoing_qty,
    #                 'quanitty_prevu': p.virtual_available,
    #                 'image_1920': p.image_1920,
    #                 'image_128' : p.image_128,
    #                 'image_1024': p.image_1024,
    #                 'image_512': p.image_512,
    #                 'image_256': p.image_256,
    #                 'categ_id': p.categ_id.name,
    #                 'type': p.type,
    #                 'description': p.description,
    #                 'list_price': p.list_price,
    #                 'volume': p.volume,
    #                 'weight': p.weight,
    #                 'sale_ok': p.sale_ok,
    #                 'standard_price': p.standard_price,
    #                 'active': p.active,
    #             })

    #         resp = werkzeug.wrappers.Response(
    #             status=200,
    #             content_type='application/json; charset=utf-8',
    #             headers=[('Cache-Control', 'no-store'), ('Pragma', 'no-cache')],
    #             response=json.dumps(product_data)
    #         )
    #         return resp
    #     return  werkzeug.wrappers.Response(
    #         status=200,
    #         content_type='application/json; charset=utf-8',
    #         headers=[('Cache-Control', 'no-store'), ('Pragma', 'no-cache')],
    #         response=json.dumps("pas de données")  )



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
    

    @http.route('/api/new_compte',  methods=['POST'] , type='http', auth='none' , cors="*" , csrf=False )
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
        # company_name = data.get('company_name')
        city = data.get('city')
        phone = data.get('phone')

        company = request.env['res.company'].sudo().search([('id', '=', 1)], limit=1)
        country = request.env['res.country'].sudo().search([ ('id' , '=' , 204 ) ] , limit = 1 )

        partner_email = request.env['res.partner'].sudo().search([('email', '=', email)], limit=1)

        if partner_email :
            return werkzeug.wrappers.Response(
                status=400,
                content_type='application/json; charset=utf-8',
                headers=[('Cache-Control', 'no-store'), ('Pragma', 'no-cache')],
                response=json.dumps("Utilisateur avec cet adresse mail existe déjà")
            )
        partner_phone =  request.env['res.partner'].sudo().search([('phone', '=', phone)], limit=1)
        if partner_phone :
            return werkzeug.wrappers.Response(
                status=400,
                content_type='application/json; charset=utf-8',
                headers=[('Cache-Control', 'no-store'), ('Pragma', 'no-cache')],
                response=json.dumps("Utilisateur avec ce numero téléphone existe déjà")
            )
        if not partner_email and not partner_phone:
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
            if partner:
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
                    return werkzeug.wrappers.Response(
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

        return werkzeug.wrappers.Response(
            status=400,
            content_type='application/json; charset=utf-8',
            headers=[('Cache-Control', 'no-store'), ('Pragma', 'no-cache')],
            response=json.dumps(f"Compte client non créer")
        )