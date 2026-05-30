# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ApprovalWorkflow(models.Model):
    _name = 'approval.workflow'
    _description = 'Approval Workflow'
    _order = 'name'

    _check_company_auto = True

    name = fields.Char(string="Workflow Name", required=True, translate=True)
    company_id = fields.Many2one(
        'res.company', string='Company', required=True,
        default=lambda self: self.env.company)
    active = fields.Boolean(default=True)
    description = fields.Text(string="Description")
    level_ids = fields.One2many(
        'approval.workflow.level', 'workflow_id',
        string="Approval Levels", copy=True)
    level_count = fields.Integer(
        string="Levels", compute='_compute_level_count')
    category_ids = fields.One2many(
        'approval.category', 'workflow_id',
        string="Used In Categories")

    @api.depends('level_ids')
    def _compute_level_count(self):
        for workflow in self:
            workflow.level_count = len(workflow.level_ids)
