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
                    }) for line in order.order_line],
                })
                # Validez la facture
                invoice.action_post()

    @api.model
    def create(self, vals):
        order = super(SaleOrder, self).create(vals)
        order.create_invoice()
        return order
    # def action_confirm(self):
    #     res = super(SaleOrder, self).action_confirm()
    #     self._link_payment_to_invoice()
    #     return res

    # def _link_payment_to_invoice(self):
    #     for order in self:
    #         payment = self.env['account.payment'].sudo().search([('sale_id', '=', order.id)], limit=1)
    #         if payment:
    #             invoice = self.env['account.move'].sudo().search([('sale_id', '=', order.id)], limit=1)
    #             if invoice:
    #                 payment.write({
    #                     'move_id': invoice.id,
    #                     # 'invoice_ids': [(4, invoice.id)],
    #                 })