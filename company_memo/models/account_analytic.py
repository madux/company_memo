from odoo import models, fields, api, _ 
import logging

_logger = logging.getLogger(__name__)


class AccountAnalytic(models.Model):
    _inherit = 'account.analytic.account'

    account_id = fields.Many2one(
        'account.account',
        string='Account',)

    def update_account_id(self):
        for rec in self:
            if not rec.account_id:
                account_id = self.env['account.account'].search([('name', '=', rec.name)], limit=1)
                if account_id:
                    rec.account_id = account_id.id
                    