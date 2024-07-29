# -*- coding: utf-8 -*-
from .main import *

import json
from odoo.http import request
_logger = logging.getLogger(__name__)


class MailerRest(http.Controller):

    @http.route('/api/sendMail', methods=['POST'], type='json', auth='none', cors="*", csrf=False)
    def send_mail(self, **kw):
        # Récupérer les paramètres de la requête
        data = json.loads(request.httprequest.data)

        email_from = data.get('email_from')
        email_to = data.get('email_to')
        subject = data.get('subject')
        body = data.get('body')

        if not email_from or not email_to or not subject or not body:
            return {'status': 'error', 'message': 'Missing required parameters'}

        # Récupérer ou créer une instance de IrMailServer
        mail_server = request.env['ir.mail_server'].sudo().search([], limit=1)

        # Construire le message e-mail
        message = mail_server.build_email(email_from, [email_to], subject, body)

        try:
            # Envoyer l'e-mail
            mail_server.send_email(message)
            return {'status': 'success', 'message': 'Email sent successfully'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
        

    @http.route('/api/sendMailUser', methods=['POST'], type='json', auth='none', cors="*", csrf=False)
    def send_mail_user(self, **kw):
        # Récupérer les paramètres de la requête
        data = json.loads(request.httprequest.data)

        email_from = data.get('email_from')
        email_to = data.get('email_to')
        subject = data.get('subject')
        body = data.get('body')

        if not email_from or not email_to or not subject or not body:
            return {'status': 'error', 'message': 'Missing required parameters'}

        # Récupérer ou créer une instance de IrMailServer
        mail_server = request.env['ir.mail_server'].sudo().search([], limit=1)
        if not mail_server:
            mail_server = request.env['ir.mail_server'].sudo().create({
                'name': 'Gmail',
                'smtp_host': 'smtp.gmail.com',
                'smtp_port': 587,
                'smtp_user': 'moustaphakhouma964@gmail.com',
                'smtp_pass': 'moustaphakhouma1996',
                'smtp_encryption': 'starttls',
            })

        # Récupérer le partenaire associé à l'adresse e-mail
        partner = request.env['res.partner'].sudo().search([('id', '=', 70)], limit=1)
        if not partner:
            return {'status': 'error', 'message': 'Partner not found for the given email'}

        user = request.env['res.users'].sudo().browse(request.env.uid)
        if not user or user._is_public():
            admin_user = request.env.ref('base.user_admin')
            request.env = request.env(user=admin_user.id)
        # Créer un enregistrement temporaire de crm.lead
        lead = request.env['crm.lead'].sudo().create({
            'name': subject,
            'partner_id': partner.id,
            'email_from': email_from,
            'company_id': partner.company_id.id,
            'user_id':  request.env.user.id,
        })

        # Récupérer le template d'e-mail
        mail_template = request.env['mail.template'].sudo().search([('id', '=', 15)], limit=1)
        if not mail_template:
            return {'status': 'error', 'message': 'Mail template not found'}

        # Générer le contenu de l'e-mail en utilisant le template
        email_values = mail_template.generate_email([lead.id], fields=['email_from', 'email_to', 'subject', 'body_html'])

        # Créer et envoyer l'e-mail
        mail_mail = request.env['mail.mail'].sudo().create(email_values[lead.id])
        try:
            mail_mail.send()
            return {'status': 'success', 'message': 'Email sent successfully'}
        except Exception as e:
            _logger.error(f'Error sending email: {str(e)}')
            return {'status': 'error', 'message': str(e)}


    @http.route('/api/welcome_mail/<email>', methods=['GET'], type='json', auth='none', cors="*", csrf=False)
    def send_welcome_mail(self, email , **kw):
        # Récupérer ou créer une instance de IrMailServer
        mail_server = request.env['ir.mail_server'].sudo().search([], limit=1)

        # Récupérer l'utilisateur associé à l'adresse e-mail
        user = request.env['res.users'].sudo().search([('email', '=', email)], limit=1)
        if not user:
            return {'status': 'error', 'message': 'User not found for the given email'}

        # Récupérer le template d'e-mail
        mail_template = request.env['mail.template'].sudo().search([('id', '=', 33)], limit=1)
        if not mail_template:
            return {'status': 'error', 'message': 'Mail template not found'}

        # Générer le contenu de l'e-mail en utilisant le template
        email_values = mail_template.generate_email([user.id], fields=['email_from', 'email_to', 'subject', 'body_html'])

        # Créer et envoyer l'e-mail
        mail_mail = request.env['mail.mail'].sudo().create(email_values[user.id])
        try:
            mail_mail.send()
            return {'status': 'success', 'message': 'Email sent successfully'}
        except Exception as e:
            _logger.error(f'Error sending email: {str(e)}')
            return {'status': 'error', 'message': str(e)}


    @http.route('/api/sendResetPasswordMail/<email>', methods=['GET'], type='http', auth='none', cors="*", csrf=False)
    def send_reset_password_mail(self,email, **kw):


        # Récupérer ou créer une instance de IrMailServer
        mail_server = request.env['ir.mail_server'].sudo().search([], limit=1)
        if not mail_server:
            mail_server = request.env['ir.mail_server'].sudo().create({
                'name': 'Gmail',
                'smtp_host': 'smtp.gmail.com',
                'smtp_port': 587,
                'smtp_user': 'moustaphakhouma964@gmail.com',
                'smtp_pass': 'moustaphakhouma1996',
                'smtp_encryption': 'starttls',
            })

        # Récupérer l'utilisateur associé à l'adresse e-mail
        user = request.env['res.users'].sudo().search([('email', '=', email)], limit=1)
        if not user:
            return werkzeug.wrappers.Response(
                    status=400,
                    content_type='application/json; charset=utf-8',
                    headers=[('Cache-Control', 'no-store'), ('Pragma', 'no-cache')],
                    response=json.dumps("Utilisateur non trouvé pour l'e-mail donné")
                )

        # Vérifier si l'utilisateur existe et n'est pas supprimé
        if not user.exists():
            return werkzeug.wrappers.Response(
                    status=400,
                    content_type='application/json; charset=utf-8',
                    headers=[('Cache-Control', 'no-store'), ('Pragma', 'no-cache')],
                    response=json.dumps("L'utilisateur n'existe pas ou a été supprimé")
                )

        # Récupérer le template d'e-mail
        mail_template = request.env['mail.template'].sudo().search([('id', '=', 1)], limit=1)
        if not mail_template:
            return werkzeug.wrappers.Response(
                        status=400,
                        content_type='application/json; charset=utf-8',
                        headers=[('Cache-Control', 'no-store'), ('Pragma', 'no-cache')],
                        response=json.dumps("Modèle de courrier électronique non trouvé")
                    )

        email_values = mail_template.generate_email([user.id], fields=['email_from', 'email_to', 'subject', 'body_html'])

        # Créer et envoyer l'e-mail
        mail_mail = request.env['mail.mail'].sudo().create(email_values[user.id])
        try:
            mail_mail.send()

            return werkzeug.wrappers.Response(
                            status=200,
                            content_type='application/json; charset=utf-8',
                            headers=[('Cache-Control', 'no-store'), ('Pragma', 'no-cache')],
                            response=json.dumps("E-mail envoyé avec succès")
                        )
        except Exception as e:
            _logger.error(f'Error sending email: {str(e)}')
            return werkzeug.wrappers.Response(
                            status=400,
                            content_type='application/json; charset=utf-8',
                            headers=[('Cache-Control', 'no-store'), ('Pragma', 'no-cache')],
                            response=json.dumps(f'Error sending email: {str(e)}')
                        )


    @http.route('/api/sendPortalInvitationMail/<email>', methods=['GET'], type='json', auth='none', cors="*", csrf=False)
    def send_portal_invitation_mail(self, email , **kw):

        # Récupérer ou créer une instance de IrMailServer
        mail_server = request.env['ir.mail_server'].sudo().search([], limit=1)
        if not mail_server:
            mail_server = request.env['ir.mail_server'].sudo().create({
                'name': 'Gmail',
                'smtp_host': 'smtp.gmail.com',
                'smtp_port': 587,
                'smtp_user': 'moustaphakhouma964@gmail.com',
                'smtp_pass': 'moustaphakhouma1996',
                'smtp_encryption': 'starttls',
            })

        # Récupérer l'utilisateur associé à l'adresse e-mail
        user = request.env['res.users'].sudo().search([('id', '=', 9)], limit=1)
        if not user:
            return {'status': 'error', 'message': 'User not found for the given email'}

        # Vérifier si l'utilisateur existe et n'est pas supprimé
        if not user.exists():
            return {'status': 'error', 'message': 'User does not exist or has been deleted'}

        # Récupérer le template d'e-mail
        mail_template = request.env['mail.template'].sudo().search([('id', '=', 2)], limit=1)
        if not mail_template:
            return {'status': 'error', 'message': 'Mail template not found'}

        # Générer le contenu de l'e-mail en utilisant le template
        email_values = mail_template.generate_email([user.id], fields=['email_from', 'email_to', 'subject', 'body_html'])

        # Créer et envoyer l'e-mail
        mail_mail = request.env['mail.mail'].sudo().create(email_values[user.id])
        try:
            mail_mail.send()
            return {'status': 'success', 'message': 'Email sent successfully'}
        except Exception as e:
            _logger.error(f'Error sending email: {str(e)}')
            return {'status': 'error', 'message': str(e)}




    @http.route('/api/mail_contact', methods=['POST'], type='json', auth='none', cors="*", csrf=False)
    def send_welcome_mail(self, **kw):
        data = json.loads(request.httprequest.data)

        email = data.get('email')
        nom = data.get('nom')
        sujet = data.get('sujet')
        message = data.get('message')
        
        # Récupérer ou créer une instance de IrMailServer
        mail_server = request.env['ir.mail_server'].sudo().search([], limit=1)

        # Récupérer l'utilisateur associé à l'adresse e-mail
        user = request.env['res.users'].sudo().search([('email', '=', email)], limit=1)
        if not user:
            return {'status': 'error', 'message': 'User not found for the given email'}

        # Récupérer le template d'e-mail
        mail_template = request.env['mail.template'].sudo().search([('id', '=', 33)], limit=1)
        if not mail_template:
            return {'status': 'error', 'message': 'Mail template not found'}

        # Générer le contenu de l'e-mail en utilisant le template
        email_values = mail_template.generate_email([user.id], fields=['email_from', 'email_to', 'subject', 'body_html'])

        # Créer et envoyer l'e-mail
        mail_mail = request.env['mail.mail'].sudo().create(email_values[user.id])
        try:
            mail_mail.send()
            return {'status': 'success', 'message': 'Email sent successfully'}
        except Exception as e:
            _logger.error(f'Error sending email: {str(e)}')
            return {'status': 'error', 'message': str(e)}