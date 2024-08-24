from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def create_invoice(self):
        for order in self:
            # Vérifiez si la commande est confirmée
            if order.state == 'sale':
                # Créez une facture basée sur la commande de vente
                invoice = self.env['account.move'].create({
                    'partner_id': order.partner_id.id,
                    'move_type': 'out_invoice',
                    'invoice_origin': order.name,
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
        res = super(SaleOrder, self).action_confirm()
        self.create_invoice()
        return res