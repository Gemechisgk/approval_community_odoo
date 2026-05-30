# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ApprovalWorkflowLevel(models.Model):
    _name = 'approval.workflow.level'
    _description = 'Approval Workflow Level'
    _order = 'sequence, id'

    name = fields.Char(
        string="Level Name", required=True,
        help="E.g. Team Lead, Department Head, VP")
    sequence = fields.Integer(string="Sequence", default=10)
    workflow_id = fields.Many2one(
        'approval.workflow', string="Workflow",
        ondelete='cascade', required=True)
    company_id = fields.Many2one(
        string='Company', related='workflow_id.company_id',
        store=True, readonly=True)
    approval_type = fields.Selection([
        ('all', 'All Must Approve'),
        ('any', 'Any One Can Approve'),
        ('minimum', 'Minimum Number'),
    ], string="Approval Type", default='all', required=True,
        help="'All Must Approve': every approver at this level must approve.\n"
             "'Any One Can Approve': a single approval moves to next level.\n"
             "'Minimum Number': a minimum count of approvals is required.")
    user_ids = fields.Many2many(
        'res.users', 'approval_workflow_level_users_rel',
        'level_id', 'user_id',
        string="Approvers",
        help="Users who can approve at this level.")
    minimum_approvals = fields.Integer(
        string="Minimum Approvals", default=1,
        help="Number of approvals required at this level "
             "(only used when Approval Type is 'Minimum Number').")

    @api.constrains('minimum_approvals', 'user_ids', 'approval_type')
    def _check_minimum_approvals(self):
        for level in self:
            if (level.approval_type == 'minimum'
                    and level.minimum_approvals > len(level.user_ids)):
                raise ValidationError(_(
                    'Minimum approvals (%s) cannot exceed the number '
                    'of approvers (%s) at level "%s".',
                    level.minimum_approvals,
                    len(level.user_ids),
                    level.name))
