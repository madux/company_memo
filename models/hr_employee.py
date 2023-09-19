from odoo import models, fields, api, _


class Hrdistrict(models.Model):
    _name = 'hr.district'
    
    name=fields.Char(string="District")
 

class HrEmployeeBase(models.AbstractModel):
    _inherit = "hr.employee.base"
 
    administrative_supervisor_id = fields.Many2one('hr.employee', string="Supervisor")
    ps_district_id=fields.Many2one('hr.district', string="District")
