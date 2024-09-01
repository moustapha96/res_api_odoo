from odoo import models, fields, api

class SaleOrderAccountMove(models.Model):
    _inherit = 'sale.order'

    def create_invoice(self):
        for order in self:
            # Vérifiez si la commande est confirmée
            if order.state == 'sale':
                # Créez une facture basée sur la commande de vente
                journal = self.env['account.journal'].sudo().search([('code', '=', 'sale'), ( 'company_id', '=', order.company.id ) ], limit=1)  # type = sale id= 1 & company_id = 1  ==> journal id = 1 / si journal id = 7 : CASH

                invoice = self.env['account.move'].create({
                    'partner_id': order.partner_id.id,
                    'move_type': 'out_invoice',
                    'invoice_origin': order.name,
                    'journald_id': journal.id,
                    'currency_id': journal.currency_id.id, 
                    'invoice_line_ids': [(0, 0, {
                        'product_id': line.product_id.id,
                        'quantity': line.product_uom_qty,
                        'price_unit': line.price_unit,
                        'name': line.name,
                        'account_id': line.product_id.property_account_income_id.id or line.product_id.categ_id.property_account_income_categ_id.id,
                    }) for line in order.order_line],
                })
                # Validez la facture
                invoice.action_post()

    @api.model
    def action_confirm(self):
        res = super(SaleOrderAccountMove, self).action_confirm()
        self.create_invoice()
        return res