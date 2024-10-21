from odoo import models, fields, api, _ 
import logging

_logger = logging.getLogger(__name__)





class AccountMoveMemo(models.Model):
    _inherit = 'account.journal'

    overall_balance_in_gl = fields.Integer(
        string='Balance in GL',
        compute="compute_overall_journal_balance")

    @api.depends('name')
    def compute_overall_journal_balance(self):
        for rec in self:
            inflow = 0
            outflow = 0
            if rec.name:
                journal_move_ids = self.env['account.move.line'].search([
                    ('move_id.journal_id.id', '=', rec.id)])
                if journal_move_ids: 
                    for mv in journal_move_ids:
                        inflow += mv.debit
                        outflow += mv.credit
                _logger.info(f'THHHHHHHHHHHHHHERRRRRRRRRRRRREE        {inflow} {outflow}')
                balance = inflow - outflow
                rec.overall_balance_in_gl = balance
            else:
                rec.overall_balance_in_gl = 30900

