from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import misc, DEFAULT_SERVER_DATETIME_FORMAT
from dateutil.relativedelta import relativedelta
import time
from datetime import datetime, timedelta 
from odoo import http
import random
from lxml import etree


class Memo_Model(models.Model):
    _name = "memo.model"
    _inherit = ['mail.thread']  #, 'ir.needaction_mixin']
    _rec_name = "name"
    _order = "id desc"
    
    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('memo.model')
        vals['code'] = str(sequence)
        return super(Memo_Model, self).create(vals)

    @api.multi
    def _compute_attachment_number(self):
        attachment_data = self.env['ir.attachment'].read_group([('res_model', '=', 'memo.model'), ('res_id', 'in', self.ids)], ['res_id'], ['res_id'])
        attachment = dict((data['res_id'], data['res_id_count']) for data in attachment_data)
        for rec in self:
            rec.attachment_number = attachment.get(rec.id, 0)
    @api.multi
    def action_get_attachment_view(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window'].for_xml_id('base', 'action_attachment')
        res['domain'] = [('res_model', '=', 'memo.model'), ('res_id', 'in', self.ids)]
        res['context'] = {'default_res_model': 'memo.model', 'default_res_id': self.id}
        return res
    
    # efault to current employee using the system 
    def _default_employee(self):
        return self.env.context.get('default_employee_id') or \
            self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    def _default_user(self):
        return self.env.context.get('default_user_id') \
            or self.env['res.users'].search([('id', '=', self.env.uid)], limit=1)

    memo_type = fields.Selection([("Payment", "Payment"),
                                     ("Internal", "Internal Memo")], 
                                 string="Memo Type",
                                 default="Internal",
                                 required=True)

    name = fields.Char('Subject', size=400)
    code = fields.Char('Code', readonly=True)
    employee_id = fields.Many2one('hr.employee', string = 'Employee', 
                                  default =_default_employee) 
    direct_employee_id = fields.Many2one('hr.employee', string = 'Employee') 
    set_staff = fields.Many2one('hr.employee', string = 'Employee')
    demo_staff = fields.Integer(string='User', compute="get_user_staff",
                                default=lambda self: self.env['res.users']\
                                    .search([('id', '=', self.env.uid)], limit=1).id)

    @api.depends('set_staff')
    def get_user_staff(self):
        self.demo_staff = self.set_staff.user_id.id
        
    user_ids = fields.Many2one('res.users', string = 'Users', default =_default_user)
    dept_ids = fields.Many2one('hr.department', string ='Department',
                               compute="employee_department",
                               readonly = True, store =True)
    description = fields.Char('Note')
    project_id = fields.Many2one('account.analytic.account', 'Project')
    vendor_id = fields.Many2one('res.partner', 'Vendor',
                                domain=[('supplier','=', True)])
    amountfig = fields.Float('Budget Amount', store=True)
    description_two = fields.Text('Reasons')
    reason_back = fields.Char('Return Reason')
    file_upload = fields.Binary('File Upload')
    file_namex = fields.Char("FileName")
    state = fields.Selection([('submit', 'Draft'),
                                ('Sent', 'Sent'),
                                ('Approve', 'Waiting For Payment'),
                                ('Approve2', 'Memo Approved'),
                                ('Done', 'Done'),
                                ('refuse', 'Refused'),
                              ], string='Status', index=True, readonly=True,
                             track_visibility='onchange',
                             copy=False, default='submit',
                             required=True,
                             help='Request Report state')
    date = fields.Datetime('Request Date', default=fields.Datetime.now())
    invoice_id = fields.Many2one('account.invoice', string='Invoice', store=True)
    status_progress = fields.Float(string="Progress(%)",
                                   compute='_progress_state')
    users_followers = fields.Many2many('hr.employee', string='Add followers')
    res_users = fields.Many2many('res.users', string='Approvers')
    comments = fields.Text('Comments', default="-")
    attachment_number = fields.Integer(compute='_compute_attachment_number', string='No. Attachments')
    partner_id = fields.Many2many('res.partner', string='Related Partners')
    
    @api.onchange('invoice_id')
    def get_amount(self):
        if self.invoice_id:
            self.amountfig = self.invoice_id.amount_total
         

    @api.model
    def fields_view_get(self, view_id='company_memo.memo_model_form_view_3', 
                        view_type='form', toolbar=False, submenu=False):
        res = super(Memo_Model, self).fields_view_get(view_id=view_id,
                                                      view_type=view_type,
                                                      toolbar=toolbar,
                                                      submenu = submenu)
        doc = etree.XML(res['arch']) 
        # users = self.env['memo.model'].search([('user_id', 'in', self.users_followers.user_id.id)])
        for rec in self.res_users:
            if rec.id == self.env.uid:
                for node in doc.xpath("//field[@name='users_followers']"):
                    node.set('modifiers', '{"readonly": true}') 
                    
                for node in doc.xpath("//button[@name='return_memo']"):
                    node.set('modifiers', '{"invisible": true}')
        res['arch'] = etree.tostring(doc)
        return res

    @api.multi
    def print_memo(self):
        return self.env.ref('company_memo.print_memo_model_report').report_action(self)
             
    @api.one   
    def set_draft(self):
        self.write({'state': "submit", 'direct_employee_id': False})
        
    @api.one   
    def user_done_memo(self):
        self.write({'state': "Done"})

    @api.one
    def Cancel(self):
        self.write({'state': "submit", 
                    'direct_employee_id': False, 
                    'partner_id':False, 
                    'user_followers': False})

    def get_url(self, id, name):
        base_url = http.request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        base_url += '/web#id=%d&view_type=form&model=%s' % (id, name)
        return "<a href={}> </b>Click<a/>. ".format(base_url)
    
    # get the employee's department
    @api.depends('employee_id')
    def employee_department(self):
        if self.employee_id:
            self.dept_ids = self.employee_id.department_id.id
  
    """checks if the current user is the initiator of the memo, if true, raises error
    else: it opens the wizard"""
    @api.multi
    def forward_memo(self): 
        users = self.env['res.users'].browse([self.env.uid])
        manager = users.has_group("company_memo.mainmemo_manager")
        admin = users.has_group("base.group_system")
        dummy, view_id = self.env['ir.model.data'].get_object_reference('company_memo', 'memo_model_forward_wizard')

        return {
              'name': 'Forward Memo',
              'view_type': 'form',
              'view_id': view_id,
              "view_mode": 'form',
              'res_model': 'memo.foward',
              'type': 'ir.actions.act_window',
              'target': 'new',
              'context': {
                  'default_memo_record': self.id,
                  'default_date': self.date,
                  'default_resp': self.env.uid,
              },
        }
    """The wizard action passes the employee whom the memo was director to this function."""
    @api.one
    def forward_memos(self, employee, comments): # Always available,  
        user_id = self.env['res.users'].search([('id','=',self.env.user.id)])
        lists2 = [y.partner_id.id for x in self.users_followers for y in x.user_id]
        # self.write({'partner_id': [(4, lists2)]})  
        bodyx = "Dear {}, </br>I wish to notify you that a memo with description, '{}',\
                from {} department was sent to you. Kindly review and get back to me. </br> </br>Kindly {} </br>\
                Yours Faithfully</br>{}".format(self.direct_employee_id.name,
                                                self.name, self.employee_id.department_id.name,
                                                self.get_url(self.id, self._name),
                                                self.env.user.name)
        self.mail_sending_direct(bodyx)
        self.direct_employee_id = False 
        body = "Memo for %s initiated by %s, moved by- ; %s and sent to %s" %(self.name, self.employee_id.name, self.env.user.name, employee)
        body_main = body + "\n with the comments: %s" %(comments)
        self.follower_messages(body_main)

    def mail_sending_direct(self, bodyx): 
        subject = "Memo Notification"
        email_from = self.env.user.email
        mail_to = self.direct_employee_id.work_email
        emails = (','.join(str(item2.work_email) for item2 in self.users_followers))
        mail_data = {
                'email_from': email_from,
                'subject': subject,
                'email_to': mail_to,
                'reply_to': email_from,
                'email_cc': emails if self.users_followers else [],
                'body_html': bodyx
            }
        mail_id = self.env['mail.mail'].create(mail_data)
        self.env['mail.mail'].send(mail_id)

    def _get_group_users(self):
        followers = []
        account_id = self.env.ref('company_memo.mainmemo_account')
        acc_group = self.env['res.groups'].search([('id', '=', int(account_id.id))], limit=1)

        for users in acc_group.users:
            employee = self.env['hr.employee'].search([('user_id', '=', users.id)])
            for rex in employee:
                followers.append(rex.id)
        return self.write({'users_followers': [(4, followers)]})

    @api.one
    def approve_memo(self): # Always available to Some specific groups
        users = self.env['res.users'].browse([self.env.uid])
        manager = users.has_group("company_memo.mainmemo_manager")
        if not manager:
            if self.env.uid == self.employee_id.user_id.id:
                raise ValidationError('You are not Permitted to approve a Payment Memo.\
                Forward it to the authorized Person')
   
        body = "MEMO APPROVE NOTIFICATION: -Approved By ;\n %s on %s" %(self.env.user.name,fields.Date.today())
        bodyx = "Dear {}, </br>I wish to notify you that a memo with description, '{}',\
                from {} department have been approved by {}. Accountant's/ Respective authority should take note. \
                Kindly review and get back to me. </br> </br>Kindly {} </br>\
                Yours Faithfully</br>{}".format(self.employee_id.name, 
                                            self.name, self.employee_id.department_id.name, self.env.user.name,
                                            self.get_url(self.id, self._name), self.env.user.name)

        users = self.env['res.users'].browse([self.env.uid])
        if self.state == "Approve":
            raise ValidationError("Sorry you have already approved this payment")
        
        if self.memo_type == "Payment":
            self.state = "Approve"
            self.write({'res_users': [(4, users.id)]})
        elif self.memo_type == "Internal":
            self.state = "Done"
            self.write({'res_users': [(4, users.id)]})
        self.mail_sending_direct(bodyx)
        self.follower_messages(body)
    
    @api.one
    def user_approve_memo(self): # Always available to Some specific groups
        body = "MEMO APPROVE NOTIFICATION: -Approved By ;\n %s on %s" %(self.env.user.name, fields.Date.today())
        bodyx = "Dear {}, </br>I wish to notify you that a memo with description, '{}',\
                from {} department have been approved by {}. Kindly review. </br> </br>Kindly {} </br>\
                Yours Faithfully</br>{}".format(self.employee_id.name, 
                                            self.name, self.employee_id.department_id.name, self.env.user.name,
                                            self.get_url(self.id, self._name), self.env.user.name)
        
        users = self.env['res.users'].browse([self.env.uid])
        user = users.has_group("company_memo.mainmemo_officer")
        manager = users.has_group("company_memo.mainmemo_manager")
        acc = users.has_group("company_memo.mainmemo_account")
        if not manager:
            if self.env.uid == self.employee_id.user_id.id:
                raise ValidationError('You are not Permitted to approve a Payment Memo.\
                Forward it to the authorized Person')
            self.approve_memo()
            
        else:
            self.approve_memo()
        
    def follower_messages(self, body):
        # body= "RETURN NOTIFICATION;\n %s" %(self.reason_back)
        body = body
        records = self._get_followers()
        followers = records
        self.message_post(body=body, subtype='mt_comment',message_type='notification',partner_ids=followers)

    @api.multi
    def Register_Payment(self):
        dummy, view_id = self.env['ir.model.data'].get_object_reference('account', 'view_account_payment_form')
        # if not self.vendor_id:
        #     raise ValidationError("Please select a Vendor")
            
        if (self.memo_type != "Payment") or (self.amountfig < 1):
            raise ValidationError("(1) Memo type must be 'Payment'\n (2) Amount must be greater than one to proceed with payment")
        ret = {
                'name':'Register Memo Payment',
                'view_mode': 'form',
                'view_id': view_id,
                'view_type': 'form',
                'res_model': 'account.payment',
                'type': 'ir.actions.act_window',
                'domain': [],
                'context': {
                        'default_amount': self.amountfig,
                        'default_payment_type': 'outbound',
                        'default_partner_id':self.vendor_id.id, 
                        'default_communication': self.code, 
                        # 'default_memo_id':self.id,
                        #'default_journal_id':self._default_journal(),
                        #'default_commmunication': str(self.name)+ ' from ' + str(self.employee_id.name),
                },
                'target': 'new'
                }
        return ret
        
    @api.multi
    def return_memo(self):
        # for rec in self.res_users:
        #     if self.env.uid == rec.id:
        #         raise ValidationError('You are not allow to return or reject a memo')
        return {
              'name': 'Reason for Return',
              'view_type': 'form',
              "view_mode": 'form',
              'res_model': 'memo.back',
              'type': 'ir.actions.act_window',
              'target': 'new',
              'context': {
                  'default_memo_record': self.id,
                  'default_date': self.date,
                  'default_direct_employee_id': self.set_staff.id,
                  'default_resp':self.env.uid,
              },
        }
    
    @api.multi
    @api.depends('state')
    # Depending on any field change (ORM or Form), the function is triggered.
    def _progress_state(self):
        for order in self:
            if order.state == "submit":
                order.status_progress = random.randint(0, 20)

            elif order.state == "Sent":
                order.status_progress = random.randint(30, 60)

            elif order.state == "Approve":
                order.status_progress = random.randint(80, 88)
                
            elif order.state == "Approve2":
                order.status_progress = random.randint(89, 95)
                
            elif order.state == "Done":
                order.status_progress = random.randint(98, 100)
            else:
                order.status_pogress = random.randint(70, 100) # 100 / len(order.state)


    @api.multi
    def unlink(self):
        for delete in self.filtered(lambda delete: delete.state in ['Sent','Approve2', 'Approve']):
            raise ValidationError(_('You cannot delete a Memo which is in %s state.') % (delete.state,))
        return super(Memo_Model, self).unlink()

    

class Send_Memoo_back(models.Model):
    _name = "memo.back"

    resp = fields.Many2one('res.users', 'Responsible')
    memo_record = fields.Many2one('memo.model','Memo ID',)
    reason = fields.Char('Reason') 
    date = fields.Datetime('Date')
    direct_employee_id = fields.Many2one('hr.employee', 'Direct To')
    
        
    def get_url(self, id, name):
        base_url = http.request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        base_url += '/web#id=%d&view_type=form&model=%s' % (id, name)
        return "<a href={}> </b>Click<a/>. ".format(base_url)

    @api.multi
    def post_refuse(self):
        get_state = self.env['memo.model'].search([('id','=', self.memo_record.id)])
        reasons = "<b><h4>Refusal Message From %s </br></br>Please refer to the reasons below:</br></br> %s.</h4></b>" %(self.env.user.name,self.reason)
        get_state.write({'reason_back': reasons})
        if self.reason:
            bodyx = "Dear Sir/Madam, </br>We wish to notify you that a Memo request from {} has been refused / returned. </br>\
             </br>Kindly {} to Review</br> </br>Thanks".format(self.memo_record.employee_id.name, self.get_url(self.id, self._name))

            get_state.write({'state':'refuse'})
            for rec in get_state.res_users:
                if get_state.user_ids.id == rec.id:
                    get_state.res_users = [(3, rec.id)]
            self.mail_sending_reject(bodyx)
        else:
            raise ValidationError('Please Add the Reasons for refusal') 
        return{'type': 'ir.actions.act_window_close'}

    def mail_sending_reject(self, bodyx):
        subject = "Memo Rejection Notification"
        email_from = self.env.user.email
        mail_to = self.direct_employee_id.work_email
        initiator = self.memo_record.employee_id.work_email
        # emails = (','.join(str(item2.work_email) for item2 in self.users_followers))
        mail_data = {
                'email_from': email_from,
                'subject': subject,
                'email_to': mail_to,
                'reply_to': email_from,
                'email_cc': initiator,  # emails if self.users_followers else [],
                'body_html': bodyx
            }
        mail_id = self.env['mail.mail'].create(mail_data)
        self.env['mail.mail'].send(mail_id)
        
class account_payment(models.Model):
    _inherit = 'account.payment'

    #  advance_account = fields.Many2one('account.account', 'Advance Account', related='journal_id.default_debit_account_id')
    @api.multi
    def post(self):
        res = super(account_payment, self).post()
        if self.communication:
            memo_model = self.env['memo.model'].sudo().search([('code', '=', self.communication)])
            if memo_model: 
                memo_model.sudo().write({'state':'Done'}) 
            else:
                pass
         
        return res
