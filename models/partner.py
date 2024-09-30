from odoo import  fields, models, _

class Partner(models.Model):
    _inherit = 'res.partner'

    password = fields.Char(string='Mot de passe de connexion sur la partie web', required=False)
    is_verified = fields.Boolean(string='Etat verification compte mail', default=False)
    avatar = fields.Char(string='Photo profil Client', required=False)
