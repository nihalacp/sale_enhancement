from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, timedelta

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    delivery_deadline = fields.Date(string='Delivery Deadline')
    priority_level = fields.Selection([('low', 'Low'),('medium', 'Medium'),('high', 'High')], string='Priority Level', default='medium', required=True)
    customer_rating = fields.Float(string='Customer Rating',default=0.0, compute="_compute_customer_rating",store=True,)
    is_deadline_overdue = fields.Boolean(string='Is Deadline Overdue', compute='_compute_deadline_status', store=True)
    deadline_delay_days = fields.Integer(string='Deadline Delay Days', compute='_compute_deadline_status', store=True)

    @api.depends('delivery_deadline')
    def _compute_deadline_status(self):
        today = date.today()
        for order in self:
            if order.delivery_deadline:
                if order.delivery_deadline < today:
                    order.is_deadline_overdue = True
                    order.deadline_delay_days = (today - order.delivery_deadline).days
                else:
                    order.is_deadline_overdue = False
                    order.deadline_delay_days = 0
            else:
                order.is_deadline_overdue = False
                order.deadline_delay_days = 0

    @api.depends('partner_id', 'partner_id.customer_rating')
    def _compute_customer_rating(self):
        for order in self:
            order.customer_rating = float(order.partner_id.customer_rating) if order.partner_id else 0.0


    def action_confirm(self):
        for order in self:
            if not order.delivery_deadline:
                raise UserError(_("Please set a Delivery Deadline before confirming the order."))
            if order.priority_level == 'high':
                if not order.date_order:
                    raise UserError(_("Order Date is not available."))
                allowed_deadline = order.date_order.date() + timedelta(days=3)
                if order.delivery_deadline > allowed_deadline:
                    raise UserError(_(
                        "For High Priority Orders, the Delivery Deadline must be within 3 days of the Order Date."
                    ))
            if order.customer_rating < 0 or order.customer_rating > 5:
                raise UserError(_("Customer Rating must be between 0 and 5."))
        return super(SaleOrder, self).action_confirm()
    
    def action_extend_deadline_3_days(self):
        for order in self:
            if not order.delivery_deadline:
                raise UserError(_("Cannot extend deadline: No delivery deadline set for order %s.") % order.name)
            old_deadline = order.delivery_deadline
            new_deadline = order.delivery_deadline + timedelta(days=3)
            order.delivery_deadline = new_deadline
            order.message_post(
                body=_("Delivery deadline extended by 3 days.Old deadline: %s New deadline: %s") % (
                    old_deadline.strftime('%Y-%m-%d'),
                    new_deadline.strftime('%Y-%m-%d')
                ),
                subject=_("Delivery Deadline Extended"),
                message_type='comment',
                subtype_xmlid='mail.mt_note'
            )
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
    
    def cron_update_deadline_status(self):
        today = date.today()
        orders = self.search([('delivery_deadline', '!=', False)])
        for order in orders:
            if order.delivery_deadline < today:
                order.write({
                    'is_deadline_overdue': True,
                    'deadline_delay_days': (today - order.delivery_deadline).days
                })
            else:
                order.write({
                    'is_deadline_overdue': False,
                    'deadline_delay_days': 0
                })

class ResPartner(models.Model):
    _inherit = 'res.partner'

    customer_rating = fields.Integer(string='Customer Rating', default=0)

    @api.constrains('customer_rating')
    def _check_customer_rating_range(self):
        for partner in self:
            if partner.customer_rating < 0 or partner.customer_rating > 5:
                raise ValidationError(_("Customer Rating must be between 0 and 5."))
