from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import misc, DEFAULT_SERVER_DATETIME_FORMAT
from dateutil.relativedelta import relativedelta
import time
from datetime import datetime, timedelta 
from odoo import http


class AccountMoveMemo(models.Model):
    _inherit = 'account.move'

    active = fields.Boolean(string='Active', default=True)
    invoice_date = fields.Date(
        string='Invoice/Bill Date',
        readonly=True,
        states={'draft': [('readonly', False)]},
        index=True,
        copy=False,
        default=fields.Date.today(),
    )
    memo_id = fields.Many2one('memo.model', string="Memo Reference")
    # district_id = fields.Many2one('hr.district', string="District")
    origin = fields.Char(string="Source")
    stage_invoice_name = fields.Char(
        string="Stage invoice name", 
        store=True,
        help="Used to track if invoice is from the stage configuration",
        )
    stage_invoice_required = fields.Boolean(string="Stage invoice required?", store=True,
        help="Used to track if invoice is required based on the stage configuration")
    is_locked = fields.Boolean(string="Is locked", default=False)
    active = fields.Boolean(string="Active", default=True)
    memo_state = fields.Char(string="Memo state", compute="compute_memo_state")
    payment_journal_id = fields.Many2one(
        'account.journal', 
        string="Payment Journal", 
        required=False,
        domain="[('id', 'in', suitable_journal_ids)]"
        )
    example_amount = fields.Float(store=False, compute='_compute_payment_term_example')
    example_date = fields.Date(store=False, compute='_compute_payment_term_example')
    example_invalid = fields.Boolean(compute='_compute_payment_term_example')
    example_preview = fields.Html(compute='_compute_payment_term_example')

    @api.depends('memo_id')
    def _compute_payment_term_example(self):
        for rec in self:
            if rec.invoice_payment_term_id:
                rec.example_amount = rec.invoice_payment_term_id.example_amount
                rec.example_date = rec.invoice_payment_term_id.example_date
                rec.example_invalid = rec.invoice_payment_term_id.example_invalid
                rec.example_preview = rec.invoice_payment_term_id.example_preview
            else:
                rec.example_amount =False
                rec.example_date = False
                rec.example_invalid = False
                rec.example_preview = False

    @api.depends('memo_id')
    def compute_memo_state(self):
        for rec in self:
            if rec.memo_id:
                rec.memo_state = rec.memo_id.state
            else:
                rec.memo_state = rec.memo_id.state

    def action_post(self):
        if self.memo_id:
            if self.memo_id.memo_type.memo_key == "soe":
                '''This is added to help send the soe reference to the related cash advance'''
                self.sudo().memo_id.cash_advance_reference.soe_advance_reference = self.memo_id.id
                self.sudo().memo_id.set_cash_advance_as_retired()
            self.memo_id.is_request_completed = True
            self.sudo().memo_id.update_final_state_and_approver()
            self.sudo().memo_id.update_status_badge()
            # self.update_account_budget_line()
        return super(AccountMoveMemo, self).action_post()
                    
    # def update_account_budget_line(self): 
    #     for ln in self.invoice_line_ids:
    #         # if not ln.analytic_distribution:# and ln.analytic_line_ids:
    #         analytic_distribution_id = self.env['account.analytic.account'].search(
    #             ['|', 
    #             ('name', '=', ln.account_id.name),
    #             ('account_id', '=', ln.account_id.id)],
    #             limit=1)
    #         # {"142":100} line_form.analytic_distribution = {self.analytic_account.id: 100}
    #         if analytic_distribution_id:
    #             ln.analytic_distribution = {analytic_distribution_id.id: 100}
            # else:
            #     raise ValidationError('No analytic distribution ')
            # else:
            #     ln.analytic_line_ids[0].update({'account_id': ln.account_id.id})
        

class AccountMove(models.Model):
    _inherit = 'account.move.line'

    code = fields.Char(string="Code")
    active = fields.Boolean(string='Active', default=True)
    
    # === Accountable fields === #
    account_id = fields.Many2one(
        comodel_name='account.account',
        string='Account',
        # compute='_compute_account_id', store=True, readonly=False, precompute=True,
        store=True, readonly=False, precompute=True,
        inverse='_inverse_account_id',
        index=True,
        auto_join=True,
        ondelete="cascade",
        domain="[('deprecated', '=', False), ('company_id', '=', company_id), ('is_off_balance', '=', False)]",
        check_company=True,
        tracking=True,
    )

    @api.onchange('account_id')
    def _inverse_account_id(self):
        self._inverse_analytic_distribution()
        self._conditional_add_to_compute('tax_ids', lambda line: (
            line.account_id.tax_ids
            and not line.product_id.taxes_id.filtered(lambda tax: tax.company_id == line.company_id)
        ))
        for rec in self:
            if rec.account_id:
                analytic_distribution_id = self.env['account.analytic.account'].search(
                    ['|', 
                    ('name', '=', rec.account_id.name),
                    ('account_id', '=', rec.account_id.id)],
                    limit=1)
                # {"142":100} line_form.analytic_distribution = {self.analytic_account.id: 100}
                if analytic_distribution_id:
                    rec.analytic_distribution = {analytic_distribution_id.id: 100}
                # else:
                #     raise ValidationError('No analytic distribution ')
            
            
class AccountMoveReversal(models.TransientModel):
    _inherit = 'account.move.reversal'

    memo_id = fields.Many2one('memo.model', string="Memo Reference")
    # district_id = fields.Many2one('hr.district', string="District")

    # def reverse_moves(self):
    #     res = super(AccountMoveReversal, self).post()
    #     for rec in self.move_ids:
    #         if rec.memo_id:
    #             rec.memo_id.state = "Approve" # waiting for payment and confirmation
    #     return res

