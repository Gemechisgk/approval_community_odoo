# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ApprovalLine(models.Model):
    _name = 'approval.line'
    _description = 'Approval Action Log'
    _order = 'date desc, id desc'
    _rec_name = 'action'

    request_id = fields.Many2one(
        'approval.request', string="Request",
        ondelete='cascade', required=True, index=True)
    user_id = fields.Many2one(
        'res.users', string="User", required=True,
        default=lambda self: self.env.user)
    action = fields.Selection([
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('refused', 'Refused'),
        ('delegated', 'Delegated'),
        ('withdrawn', 'Withdrawn'),
        ('cancelled', 'Cancelled'),
        ('reset_to_draft', 'Reset to Draft'),
        ('escalated', 'Escalated'),
    ], string="Action", required=True)
    date = fields.Datetime(
        string="Date", required=True,
        default=fields.Datetime.now)
    note = fields.Text(string="Note")
    level_id = fields.Many2one(
        'approval.workflow.level', string="Workflow Level",
        help="The workflow level at which this action was taken.")
    company_id = fields.Many2one(
        string='Company', related='request_id.company_id',
        store=True, readonly=True)
