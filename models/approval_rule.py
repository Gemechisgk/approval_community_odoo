# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

import logging

_logger = logging.getLogger(__name__)


class ApprovalRule(models.Model):
    _name = 'approval.rule'
    _description = 'Approval Rule'
    _order = 'sequence, id'

    _check_company_auto = True

    name = fields.Char(string="Rule Name", required=True)
    category_id = fields.Many2one(
        'approval.category', string="Category",
        ondelete='cascade', required=True)
    sequence = fields.Integer(
        string="Priority", default=10,
        help="Rules are evaluated in order. Lower number = higher priority. "
             "First matching rule applies.")
    active = fields.Boolean(default=True)

    # Condition fields
    condition_field = fields.Selection([
        ('amount', 'Amount'),
        ('quantity', 'Quantity'),
        ('department_id', 'Department'),
        ('priority', 'Priority'),
    ], string="Condition Field", required=True,
        help="The field on the request to evaluate.")
    condition_operator = fields.Selection([
        ('=', 'Equals'),
        ('!=', 'Not Equals'),
        ('>', 'Greater Than'),
        ('<', 'Less Than'),
        ('>=', 'Greater Than or Equal'),
        ('<=', 'Less Than or Equal'),
    ], string="Operator", required=True, default='=')
    condition_value = fields.Char(
        string="Value", required=True,
        help="Value to compare against. For numeric fields, enter a number. "
             "For relational fields, enter the record ID.")

    # Domain-based condition (advanced)
    use_domain = fields.Boolean(
        string="Use Domain Filter",
        help="Use an Odoo domain expression instead of simple conditions.")
    domain_filter = fields.Char(
        string="Domain Filter", default="[]",
        help="Odoo domain filter to match requests. "
             "E.g.: [('amount', '>', 5000), ('department_id.name', '=', 'Sales')]")

    # Target workflow
    workflow_id = fields.Many2one(
        'approval.workflow', string="Assign Workflow",
        help="The workflow to assign when this rule matches.")

    company_id = fields.Many2one(
        string='Company', related='category_id.company_id',
        store=True, readonly=True)

    # Rule description (computed for display)
    condition_summary = fields.Char(
        string="Condition", compute='_compute_condition_summary')

    @api.depends('condition_field', 'condition_operator',
                 'condition_value', 'use_domain')
    def _compute_condition_summary(self):
        field_labels = dict(self._fields['condition_field'].selection)
        op_labels = dict(self._fields['condition_operator'].selection)
        for rule in self:
            if rule.use_domain:
                rule.condition_summary = rule.domain_filter or '[]'
            else:
                field_label = field_labels.get(rule.condition_field, '')
                op_label = op_labels.get(rule.condition_operator, '')
                rule.condition_summary = '%s %s %s' % (
                    field_label, op_label, rule.condition_value or '')

    @api.model
    def evaluate_rules(self, request):
        """Evaluate rules for a request and return the first matching workflow.

        Rules are evaluated in sequence (priority) order.
        The first rule that matches determines the workflow.

        Args:
            request: An approval.request record.

        Returns:
            approval.workflow record or False
        """
        rules = self.search([
            ('category_id', '=', request.category_id.id),
            ('active', '=', True),
        ], order='sequence, id')

        for rule in rules:
            if rule._matches_request(request):
                _logger.info(
                    'Approval rule "%s" matched for request "%s", '
                    'assigning workflow "%s"',
                    rule.name, request.name,
                    rule.workflow_id.name if rule.workflow_id else 'None')
                return rule.workflow_id
        return False

    def _matches_request(self, request):
        """Check if this rule matches the given request.

        Args:
            request: An approval.request record.

        Returns:
            bool: True if the rule matches.
        """
        self.ensure_one()

        if self.use_domain and self.domain_filter:
            try:
                import ast
                domain = ast.literal_eval(self.domain_filter)
                matching = request.filtered_domain(domain)
                return bool(matching)
            except Exception as e:
                _logger.warning(
                    'Failed to evaluate domain for rule "%s": %s',
                    self.name, str(e))
                return False

        # Simple condition evaluation
        try:
            field_value = request[self.condition_field]
            compare_value = self.condition_value

            # Handle relational fields (compare IDs)
            if hasattr(field_value, 'id'):
                field_value = field_value.id
                compare_value = int(compare_value)
            elif isinstance(field_value, (int, float)):
                compare_value = float(compare_value)

            operators = {
                '=': lambda a, b: a == b,
                '!=': lambda a, b: a != b,
                '>': lambda a, b: a > b,
                '<': lambda a, b: a < b,
                '>=': lambda a, b: a >= b,
                '<=': lambda a, b: a <= b,
            }
            op_func = operators.get(self.condition_operator)
            if op_func:
                return op_func(field_value, compare_value)
        except Exception as e:
            _logger.warning(
                'Failed to evaluate rule "%s": %s', self.name, str(e))

        return False
