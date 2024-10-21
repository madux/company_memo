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
         
class PortalDashboard(http.Controller):
    @http.route(["/my/portal/dashboard"], type='http', auth='user', website=True, website_published=True)
    def dashboardPortal(self): 
        user = request.env.user
        current_time = datetime.now() 
        memo = request.env['memo.model'].sudo()
        memo_ids = memo.search([
            ('employee_id', '=', user.employee_id.id),
        ], order="id desc")
        vals = {  
            "user": user,
            "image": user.employee_id.image_512 or user.image_1920,
            "memo_ids": memo_ids,
            "closed_request": len(self.closed_files(memo_ids)),
            "open_request": len(self.closed_files(memo_ids)),
            "approved_request": len(self.approved_files(memo_ids)),
            "leave_remaining":  user.employee_id.allocation_remaining_display,
        }
        return request.render("portal_request.portal_dashboard_template_id", vals)
      
    def closed_files(self, memo):
        closed_memo_ids = memo.filtered(lambda se: se.state in ['Done'])
        return closed_memo_ids
    
    def open_files(self, memo):
        open_memo_ids = memo.filtered(lambda se: se.state not in ['Refuse', 'Done'])
        return open_memo_ids
    
    def approved_files(self, memo):
        approved_memo_ids = memo.filtered(lambda se: se.state not in ['Refuse', 'submit', 'Sent'])
        return approved_memo_ids
    