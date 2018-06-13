from odoo import api, fields, models,_
from wdb import set_trace as depurador

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    repair_id = fields.Many2one('car_workshop.repair')

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        result = super(SaleOrderLine, self).product_id_change()
        vals = {}

        if 'order_id' in self._context.keys():
            self.order_id = self._context['order_id']
        if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
            vals['product_uom'] = self.product_id.uom_id
            vals['product_uom_qty'] = 1.0

        product = self.product_id.with_context(
            lang=self.order_id.partner_id.lang,
            partner=self.order_id.partner_id.id,
            quantity=vals.get('product_uom_qty') or self.product_uom_qty,
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom.id
        )
        if 'pricelist_id' in self._context and 'partner_id' in self._context:
            partner = self.env['res.partner'].browse(self._context['partner_id'])
            product = self.product_id.with_context(
                lang=self.order_id.partner_id.lang,
                partner=partner.id,
                quantity=vals.get('product_uom_qty') or self.product_uom_qty,
                date=self.order_id.date_order,
                pricelist=self._context['pricelist_id'],
                uom=self.product_uom.id
            )
            vals['price_unit'] = product.price
        self.update(vals)

    @api.multi
    def _action_launch_procurement_rule(self):
        #Con este método sólo se pretende evitar que genere un albarán.
        #De esta forma sólo se llama al padre si no proviene de una orden de reparación.
        #El consumo de esta línea de pedido se realizará desde el apartado de materiales.
        for record in self:
            print(record.order_id.repair_id)
            if not record.order_id.repair_id:
                super(SaleOrderLine, self)._action_launch_procurement_rule()
        return True

    # @api.onchange('product_uom_qty', 'product_uom', 'route_id')
    # def _onchange_product_id_check_availability(self):
    #
    #     print('HI ODOO DEVELOPER')
    #     print(self.order_id.id)
    #     print(self.order_id.warehouse_id.id)
    #     res = super(SaleOrderLine, self)._onchange_product_id_check_availability()
    #     print(res)
    #     return res
