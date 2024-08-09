# -*- coding: utf-8 -*-
from .main import *
import pdb
import datetime

from odoo import http
from odoo.http import request
import werkzeug
import json
import logging
import random

_logger = logging.getLogger(__name__)


class ResetPasswordREST(http.Controller):

    
    def generate_token(self, email):

        now = datetime.datetime.now()
        date_str = now.strftime("%Y%m%d%H%M%S")
        email_letters = list(email)
        random.shuffle(email_letters)
        shuffled_email = ''.join(email_letters)
        combined_str = f"{date_str}{shuffled_email}"
        token = hashlib.sha256(combined_str.encode()).hexdigest()
        token = token[:16]
        return token

    @http.route('/api/new-password', methods=['POST'], type='json', auth='none', cors='*', csrf=False)
    def reset_password(self, **kwargs):
        data = json.loads(request.httprequest.data)
        email = data.get('email')
        password = data.get('password')
        token = data.get('token')

        if not token or not password:
            return werkzeug.wrappers.Response(
                status=400,
                content_type='application/json; charset=utf-8',
                headers=[('Cache-Control', 'no-store'), ('Pragma', 'no-cache')],
                response=json.dumps({'status': 'error', 'message': f'email non valide '})
            )

        try:
            user = request.env['res.users'].sudo().search([('email', '=', email)], limit=1)
            partner = request.env['res.partner'].sudo().search([('signup_token', '=', token)], limit=1)
            if partner and user:
                if partner.signup_expiration > datetime.datetime.now():
                    return werkzeug.wrappers.Response(
                        status=400,
                        content_type='application/json; charset=utf-8',
                        headers=[('Cache-Control', 'no-store'), ('Pragma', 'no-cache')],
                        response=json.dumps({'status': 'error', 'message': f'Token expirer '})
                    )
                partner.write({
                    'signup_type' : None,
                    'signup_token': None,
                    'signup_expiration': None,
                })
                # user._set_password(password)
                new_passwd = password.strip()
                if not new_passwd:

                    return werkzeug.wrappers.Response(
                        status=200,
                        content_type='application/json; charset=utf-8',
                        headers=[('Cache-Control', 'no-store'), ('Pragma', 'no-cache')],
                        response=json.dumps({'status': 'error', 'message': f'"Setting empty passwords is not allowed for security reasons!"'})
                    )
                res_user = user.write({
                    'password': new_passwd
                })
                # user._password_changed = True
                if res_user:
                    return werkzeug.wrappers.Response(
                        status=200,
                        content_type='application/json; charset=utf-8',
                        headers=[('Cache-Control', 'no-store'), ('Pragma', 'no-cache')],
                        response=json.dumps({'status': 'success', 'message': f'Le mot de passe a été réinitialisé avec succès'})
                    )

        except Exception as e:
            _logger.error(f'Erreur lors de la réinitialisation du mot de passe: {str(e)}')
            return werkzeug.wrappers.Response(
                    status=400,
                    content_type='application/json; charset=utf-8',
                    headers=[('Cache-Control', 'no-store'), ('Pragma', 'no-cache')],
                    response=json.dumps({'status': 'error', 'message': str(e)})
                )


    @http.route('/api/reset-password/<email>', methods=['GET'], type='http', auth='none', cors='*', csrf=False)
    def reset_password_request(self,email, **kwargs):

        if not email:
            return werkzeug.wrappers.Response(
                status=400,
                content_type='application/json; charset=utf-8',
                headers=[('Cache-Control', 'no-store'), ('Pragma', 'no-cache')],
                response=json.dumps({'status': 'error', 'message': f'email non valide '})
            )

        user = request.env['res.users'].sudo().search([('email', '=', email)], limit=1)
        partner = request.env['res.partner'].sudo().search([ ('id' , '=' , user.partner_id.id ) ], limit=1)
        if not user:
            return werkzeug.wrappers.Response(
                status=400,
                content_type='application/json; charset=utf-8',
                headers=[('Cache-Control', 'no-store'), ('Pragma', 'no-cache')],
                response=json.dumps({'status': 'error', 'message': f'Utilisateur non valide '})
            )

        # Générer un token de réinitialisation de mot de passe
        token = self.generate_token(email)

        # Construire le contenu de l'e-mail
        subject = 'Réinitialiser votre mot de passe'
        reset_url = f'http://orbitcity.sn/new-password?mail={user.email}&token={token}'
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
                                                <span style="font-size: 10px;">Réinitialisation de mot de passe</span><br/>
                                                <span style="font-size: 20px; font-weight: bold;">
                                                    {user.name}
                                                </span>
                                            </td>
                                            <td valign="middle" align="right">
                                                <img style="padding: 0px; margin: 0px; height: auto; width: 80px;" src="http://orbitcity.sn/logo.png" alt="logo CCBM SHOP"/>
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
                                                    Vous avez demandé une réinitialisation de votre mot de passe.<br/>
                                                    Pour réinitialiser votre mot de passe, cliquez sur le lien suivant :
                                                    <div style="margin: 16px 0px 16px 0px;">
                                                        <a style="background-color: #875A7B; padding: 8px 16px 8px 16px; text-decoration: none; color: #fff; border-radius: 5px; font-size:13px;" href="{reset_url}">
                                                            Réinitialiser le mot de passe
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
                                Généré par <a target="_blank" href="http://orbitcity.sn" style="color: #875A7B;">Orbit City</a>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
        '''

        mail_server = request.env['ir.mail_server'].sudo().search([], limit=1)
        email_from = mail_server.smtp_user
        email_to = email

        email_values = {
            'email_from': email_from,
            'email_to': email_to,
            'subject': subject,
            'body_html': body_html,
            'state': 'outgoing',
        }

        mail_mail = request.env['mail.mail'].sudo().create(email_values)

        try:
            mail_mail.send()
            # Enregistrer le token
            partner.write({
                'signup_type' : 'reset',
                'signup_token': token,
                'signup_expiration': datetime.datetime.now() + datetime.timedelta(days=1),
            })

            return werkzeug.wrappers.Response(
                    status=200,
                    content_type='application/json; charset=utf-8',
                    headers=[('Cache-Control', 'no-store'), ('Pragma', 'no-cache')],
                    response=json.dumps({'status': 'success', 'message': f'Un lien de réinitialisation du mot de passe a été envoyé à votre adresse e-mail'})
                )
        except Exception as e:
            _logger.error(f'Error sending email: {str(e)}')
            return werkzeug.wrappers.Response(
                    status=200,
                    content_type='application/json; charset=utf-8',
                    headers=[('Cache-Control', 'no-store'), ('Pragma', 'no-cache')],
                    response=json.dumps({'status': 'error', 'message': str(e)})
                )
