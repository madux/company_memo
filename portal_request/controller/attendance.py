# -*- coding: utf-8 -*-
import base64
import json
import logging
import random
from multiprocessing.spawn import prepare
import urllib.parse
from odoo import http, fields
from odoo.exceptions import ValidationError
from odoo.tools import consteq, plaintext2html
from odoo.http import request
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from bs4 import BeautifulSoup
import odoo
import odoo.addons.web.controllers.home as main
from odoo.addons.web.controllers.utils import ensure_db, _get_login_redirect_url, is_user_internal
from odoo.tools.translate import _


_logger = logging.getLogger(__name__)
 

def format_to_odoo_date(date_str: str) -> str:
    """Formats date format mm/dd/yyyy eg.07/01/1988 to %Y-%m-%d
        OR  date format yyyy/mm/dd to  %Y-%m-%d
    Args:
        date (str): date string to be formated

    Returns:
        str: The formated date
    """
    if not date_str:
        return

    data = date_str.split('/')
    if len(data) > 2 and len(data[0]) ==2: #format mm/dd/yyyy
        try:
            mm, dd, yy = int(data[0]), int(data[1]), data[2]
            if mm > 12: #eg 21/04/2021" then reformat to 04/21/2021"
                dd, mm = mm, dd
            if mm > 12 or dd > 31 or len(yy) != 4:
                return
            return f"{yy}-{mm}-{dd}"
        except Exception:
            return
         
class PortalAttendance(http.Controller):
    @http.route(["/portal/attendance"], type='http', auth='user', website=True, website_published=True)
    def portal_attendance(self): 
        user = request.env.user
        current_time = datetime.now() 
        hr_at = request.env['hr.attendance'].sudo()
        hr_attendance = hr_at.search([
            ('employee_id', '=', user.employee_id.id),
            ('check_in', '<', current_time),
            # 'check_out', '=', False,
        ], order="id desc", limit=1)
        res = 'in' if hr_attendance.check_in and not hr_attendance.check_out else 'out'
        _logger.info(f'RESSSSSS ...{res}')
        
        vals = {  
            "user": user,
            "hr_attendance": hr_attendance,
            "checked_in": res,
        }
        return request.render("portal_request.attendance_form_template", vals)
      
        
    @http.route(['/attendance/check/'], type='json', website=True, auth="user", csrf=False)
    def checkin_attendance(self, type=False):
        user_id = request.env.user
        # current_time = datetime.now() or  post.get('current_time')
        type_check = "In" if type in ['IN', 'in', 'In'] else 'Out' 
        attendance_data = user_id.employee_id.attendance_manual({})
        if attendance_data and 'warning' in attendance_data.keys():
            error_msg = attendance_data.get('warning', '')
            # return json.dumps({
            # 'status': False, 
            # 'message': error_msg,
            # })
            return {
                'status': False, 
                'message': error_msg,
                }
        else:
            # return json.dumps({
            return {
                'status': True,
                'message': f"Successfully checked {type_check}",
            }
            
        
        # vals = {
        #     'employee_id': user_id.employee_id.id,
        #     'check_in': current_time,
        #     'check_out': False,
        # }
        # hr_attendance = request.env['hr.attendance'].sudo()
        # hr_at = hr_attendance.create(vals)
        # _logger.info(f"Attendance created")
        # return json.dumps({
        #     'success': True, 
        #     'data': {
        #         'attendance_id': hr_at.id,
        #         }
        #     })
  
    # @http.route(['/attendance/checkout'], type='http', website=True, auth="user", csrf=False)
    # def checkout_attendance(self, **post):
    #     user = request.env.user
    #     current_time = datetime.now() or  post.get('current_time')
    #     vals = {
    #         'employee_id': user.employee_id.id,
    #         'check_out': current_time,
    #     }
    #     hr_attendance = request.env['hr.attendance'].sudo()
    #     hr_at = hr_attendance.search([(
    #         'employee_id', '=', user.employee_id.id,
    #         'check_in', '<', current_time,
    #         'check_out', '=', False,
    #     )], order="id desc",)
    #     _logger.info(f"Attendance created")
    #     return json.dumps({
    #         'success': True, 
    #         'data': {
    #             'attendance_id': hr_at.id,
    #             }
    #         })
             

    