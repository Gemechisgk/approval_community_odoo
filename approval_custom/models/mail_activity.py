# -*- coding: utf-8 -*-

from odoo import models


class MailActivity(models.Model):
    _inherit = 'mail.activity'

    def _action_done(self, feedback=False, attachment_ids=None):
        """Override to handle approval activity completion.
        When an approval activity is completed via the activity view,
        we don't need special handling — the approval actions handle it."""
        if self.filtered(lambda a: a.res_model == 'approval.request'):
            # Let the approval actions handle the logic
            pass
        return super()._action_done(
            feedback=feedback, attachment_ids=attachment_ids)
