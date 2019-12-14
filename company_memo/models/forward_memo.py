from odoo import models, fields, api, _
from odoo.exceptions import ValidationError 


class Forward_Wizard(models.TransientModel):
    _name = "memo.foward"

    resp = fields.Many2one('res.users', 'Current Sender')
    memo_record = fields.Many2one('memo.model','Memo Reference',)
    description_two = fields.Text('Comment')
    date = fields.Datetime('Date')#, default=fields.Datetime.now())
    direct_employee_id = fields.Many2one('hr.employee', 'Direct To')
    users_followers = fields.Many2many('hr.employee', string='Add followers')

    @api.one
    def forward_memo(self):  # Always available, 
        if self.direct_employee_id:
            lists = [] 
            # lists.append(self.direct_employee_id.user_id.id) 
            # if self.memo_record.state != "submit":
            #     for rec in self.memo_record.res_users:
            #         if rec.id == self.env.uid:
            #             raise ValidationError('You are not allowed to Edit this documents')
            memo = self.env['memo.model'].search([('id', '=', int(self.memo_record.id))])
            memo.write({'res_users': [(4, [self.env.uid])],
                        'set_staff': self.direct_employee_id.id,
                        'direct_employee_id': self.direct_employee_id.id,
                        'state': 'Sent'}) 
            # return{'type': 'ir.actions.act_window_close'}
            
        else:
            raise ValidationError('Please select an Employee to Direct To')
        return self.memo_record.forward_memos(self.direct_employee_id.name, self.description_two)
            
    # @api.one
    # def write(self, vals):
    #     res = super(Forward_Wizard, self).write(vals)
    #     if self.memo_record.state != "submit":
    #         for rec in self.memo_record.res_users:
    #             if rec.id == self.env.uid:
    #                 raise ValidationError('You are not allowed to Edit this document')
    #         return res
    #     else:
    #         pass