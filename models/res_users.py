from datetime import datetime
from dateutil.parser import parse
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class res_users(models.Model):
    _inherit = 'res.users'
