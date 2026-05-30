# -*- coding: utf-8 -*-
{
    'name': 'Professional Approval Management',
    'version': '18.0.1.0.0',
    'category': 'Human Resources/Approvals',
    'sequence': 190,
    'summary': 'Multi-level approval workflows with dynamic rules engine',
    'description': """
Professional Approval Management for Odoo 17 Community
=======================================================

A comprehensive approval module that provides:
- Multi-level approval workflows (sequential and parallel)
- Dynamic rules engine with condition-based routing
- Approval delegation with date ranges
- Complete audit trail for all approval actions
- Email notifications and reminders
- Dashboard with pending counts and analytics
- Integration-ready mixin for other modules
- Category-based approval types with configurable fields

This module replicates and extends the functionality of
Odoo Enterprise's native approval module for Community Edition.
    """,
    'author': 'Custom Development',
    'website': '',
    'depends': ['mail', 'hr', 'product'],
    'data': [
        # Security (must load first)
        'security/approval_security.xml',
        'security/ir.model.access.csv',

        # Data
        'data/mail_activity_type_data.xml',
        'data/approval_category_data.xml',
        'data/mail_template_data.xml',
        'data/approval_cron_data.xml',

        # Wizard
        'wizard/approval_refuse_wizard_views.xml',

        # Views
        'views/approval_category_approver_views.xml',
        'views/approval_product_line_views.xml',
        'views/approval_line_views.xml',
        'views/approval_workflow_views.xml',
        'views/approval_rule_views.xml',
        'views/approval_delegation_views.xml',
        'views/approval_category_views.xml',
        'views/approval_request_views.xml',
        'views/res_users_views.xml',
    ],
    'demo': [],
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
