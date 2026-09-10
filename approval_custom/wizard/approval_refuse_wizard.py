# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ApprovalRefuseWizard(models.TransientModel):
    _name = 'approval.refuse.wizard'
    _description = 'Approval Refuse Wizard'

    request_id = fields.Many2one(
        'approval.request', string='Request',
        required=True, ondelete='cascade')
    approver_id = fields.Many2one(
        'approval.approver', string='Approver')
    reason = fields.Text(
        string='Rejection Reason', required=True,
        help='Please provide a reason for refusing this request.')

    def action_refuse(self):
        """Refuse the request with the given reason."""
        self.ensure_one()
        # Post the rejection reason in chatter
        self.request_id.message_post(
            body=_('<strong>Rejection Reason:</strong><br/>%s') % self.reason,
            message_type='comment',
            subtype_xmlid='mail.mt_note',
        )

        # Log in audit trail with reason
        self.request_id._log_approval_action(
            'refused', note=self.reason)

        # Perform the refusal
        approver = self.approver_id or self.request_id.approver_ids.filtered(
            lambda a: a.user_id == self.env.user)
        if approver:
            approver.write({'status': 'refused'})
            self.request_id.sudo()._update_next_approvers(
                'refused', approver, only_next_approver=False,
                cancel_activities=True)
            self.request_id.sudo()._get_user_approval_activities(
                user=self.env.user).action_feedback()

        self.request_id._send_notification('refused')

        return {'type': 'ir.actions.act_window_close'}
