from datetime import datetime, timedelta
import time
import base64
from odoo import models, fields, api, _, SUPERUSER_ID
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)


class HrEmployeeBase(models.AbstractModel):
    _inherit = "hr.employee.base"

    @api.constrains('employee_number')
    def _check_duplicate_employee_number(self):
        employee = self.env['hr.employee'].sudo()
        if self.employee_number not in ["", False]:
            duplicate_employee = employee.search([('employee_number', '=', self.employee_number)], limit=2)
            if len([r for r in duplicate_employee]) > 1:
                raise ValidationError("Employee with same staff ID already existing")

    employee_number = fields.Char(
        string="Staff Number", 
        )
    administrative_supervisor_id = fields.Many2one('hr.employee', string="Administrative Supervisor")
    is_external_staff = fields.Boolean(string='Is External')
    external_company_id = fields.Many2one('res.partner', string='External Company')
    
    
class HrEmployee(models.AbstractModel):
    _inherit = "hr.employee"
 
    def attendance_manual(self, next_action, entered_pin=None):
        self.ensure_one()
        attendance_user_and_no_pin = self.user_has_groups(
            'hr_attendance.group_hr_attendance_user,'
            '!hr_attendance.group_hr_attendance_use_pin')
        attendance_portal_user = self.user_has_groups(
            'base.group_portal')
        can_check_without_pin = attendance_user_and_no_pin or (self.user_id == self.env.user and entered_pin is None)
        if can_check_without_pin or entered_pin is not None and entered_pin == self.sudo().pin:
            return self._attendance_action(next_action)
        if not self.user_has_groups('hr_attendance.group_hr_attendance_user') or not self.user_has_groups('base.group_portal'):
            return {'warning': _('To activate Kiosk mode without pin code, you must have access right as an Officer or above in the Attendance app. Please contact your administrator.')}
        return {'warning': _('Wrong PIN')}
    