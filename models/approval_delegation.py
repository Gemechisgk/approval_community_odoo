# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ApprovalDelegation(models.Model):
    _name = 'approval.delegation'
    _description = 'Approval Delegation'
    _order = 'date_start desc'
    _rec_name = 'delegator_id'

    _check_company_auto = True

    delegator_id = fields.Many2one(
        'res.users', string="Delegator", required=True,
        help="The original approver who is delegating.",
        default=lambda self: self.env.user)
    delegate_id = fields.Many2one(
        'res.users', string="Delegate", required=True,
        help="The user who will approve on behalf of the delegator.")
    category_id = fields.Many2one(
        'approval.category', string="Category",
        help="Leave empty to delegate for all categories.")
    date_start = fields.Date(
        string="Start Date", required=True,
        default=fields.Date.today)
    date_end = fields.Date(
        string="End Date", required=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company', string='Company', required=True,
        default=lambda self: self.env.company)
    note = fields.Text(string="Reason")

    @api.constrains('date_start', 'date_end')
    def _check_dates(self):
        for record in self:
            if record.date_start and record.date_end:
                if record.date_end < record.date_start:
                    raise ValidationError(_(
                        'End date must be after start date.'))

    @api.constrains('delegator_id', 'delegate_id')
    def _check_different_users(self):
        for record in self:
            if record.delegator_id == record.delegate_id:
                raise ValidationError(_(
                    'You cannot delegate to yourself.'))

    @api.constrains('delegator_id', 'delegate_id', 'category_id',
                    'date_start', 'date_end')
    def _check_overlapping(self):
        for record in self:
            domain = [
                ('id', '!=', record.id),
                ('delegator_id', '=', record.delegator_id.id),
                ('active', '=', True),
                ('date_start', '<=', record.date_end),
                ('date_end', '>=', record.date_start),
            ]
            if record.category_id:
                domain.append(
                    ('category_id', 'in', [record.category_id.id, False]))
            else:
                # If no category, it overlaps with everything
                pass
            overlapping = self.search(domain, limit=1)
            if overlapping:
                raise ValidationError(_(
                    'There is already an active delegation for %s '
                    'during this period.',
                    record.delegator_id.name))
