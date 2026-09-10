# -*- coding: utf-8 -*-

from odoo import models


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    def _check_company(self):
        """Allow attachments on approval requests to bypass company check
        when they are accessed by approvers from different companies."""
        approval_attachments = self.filtered(
            lambda a: a.res_model == 'approval.request')
        other_attachments = self - approval_attachments
        if other_attachments:
            super(IrAttachment, other_attachments)._check_company()
