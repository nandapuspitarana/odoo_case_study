from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, RedirectWarning, ValidationError

class PaymentRequest(models.Model):
    _name = 'payment.request'
    _inherit = 'mail.thread'

    @api.depends('payment_line.amount')
    def _amount_all(self):
        for o in self:
            o.update({
                'amount_total': sum([l.amount for l in o.payment_line])
            })

    name = fields.Char('Reference', default='/', readonly=True)
    date = fields.Date('Date', required=True, default=fields.Date.context_today, readonly=True, states={
                       'draft': [('readonly', False)]}, track_visibility='onchange')
    user_id = fields.Many2one('res.users', string='Responsible', readonly=True,
                              required=True, default=lambda self: self.env.user, copy=False)
    employee_id = fields.Many2one('hr.employee', string='Employee', readonly=True, states={
                                  'draft': [('readonly', False)]}, track_visibility='onchange')
    department_id = fields.Many2one('hr.department', string='Department',
                                    related='employee_id.department_id', track_visibility='onchange')
    description = fields.Char('Description', required=True, readonly=True, states={
                              'draft': [('readonly', False)]}, track_visibility='onchange')
    type = fields.Selection([
        ('apr', 'Approval Payment Request'),
        ('aap', 'Approval Advance Payment'),
        ('as', 'Approval Settlement')
    ], string='Type', required=True, copy=False)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('done', 'Approve'),
        ('paid', 'Paid'),
        ('cancel', 'Cancel'),
    ], string='Status', readonly=True, copy=False, default='draft', track_visibility='onchange')
    payment_line = fields.One2many('payment.request.line', 'payment_request_id',
                                   'Payment Lines', readonly=True, states={'draft': [('readonly', False)]})
    amount_total = fields.Monetary(
        'Total', store=True, compute='_amount_all', track_visibility='onchange')
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)

    @api.model
    def create(self, vals):
        nama = '/'
        if vals['type'] == 'apr':
            nama = self.env['ir.sequence'].next_by_code(
                'approval.payment.request')
        elif vals['type'] == 'aap':
            nama = self.env['ir.sequence'].next_by_code(
                'approval.advance.payment')
        elif vals['type'] == 'as':
            nama = self.env['ir.sequence'].next_by_code('approval.settlements')
        vals['name'] = nama
        return super(PaymentRequest, self).create(vals)

    def unlink(self):
        for o in self:
            if o.state != 'draft':
                raise UserError(
                    ("Dokumen ini tidak bisa dihapus pada state %s !") % (o.state))
        return super(PaymentRequest, self).unlink()

    def payment_draft(self):
        for o in self:
            return o.write({'state': 'draft'})

    def payment_open(self):
        for o in self:
            return o.write({'state': 'confirm'})

    def payment_done(self):
        for o in self:
            return o.write({'state': 'done'})


class PaymentRequestLine(models.Model):
    _name = 'payment.request.line'

    payment_request_id = fields.Many2one(
        'payment.request', 'Payment Reference', required=True, ondelete='cascade')
    name = fields.Char('Description', required=True)
    invoice_id = fields.Many2one('account.move', 'Vendor Bill', domain=[
                                 ('state', '=', 'posted'), ('move_type', '=', 'in_invoice')])
    amount = fields.Monetary('Amount', required=True,
                             digits=dp.get_precision('Product Price'))
    currency_id = fields.Many2one(related='payment_request_id.currency_id', depends=[
                                  'payment_request_id'], store=True, string='Currency')
    state = fields.Selection([('open', 'Open'), ('paid', 'Paid')],
                             string='Status', readonly=True, default='open')

    @api.onchange('invoice_id')
    def onchange_invoice_id(self):
        if self.invoice_id:
            self.amount = self.invoice_id.amount_total
            self.name = 'Payment Vendor Bill ' + self.invoice_id.partner_id.name
