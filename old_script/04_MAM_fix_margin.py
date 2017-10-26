#! /usr/bin/env python
# -*- encoding: utf-8 -*-

from unidecode import unidecode
from datetime import datetime
import base64
import erppeek
import csv

from cfg_secret_configuration import odoo_configuration_user


###############################################################################
# Odoo
###############################################################################
# Connection Odoo
def init_openerp(url, login, password, database):
    openerp = erppeek.Client(url)
    uid = openerp.login(login, password=password, database=database)
    user = openerp.ResUsers.browse(uid)
    tz = user.tz
    return openerp, uid, tz

openerp, uid, tz = init_openerp(
    odoo_configuration_user['url'],
    odoo_configuration_user['login'],
    odoo_configuration_user['password'],
    odoo_configuration_user['database'])

###############################################################################
# Settings
###############################################################################

min_rate = 20
max_rate = 22.5

tax_group_mapping = {
    248: 1.465,     # 5.5%
    249: 1.667,     # 20%
}

###############################################################################
# Script
###############################################################################

# Get all products

products = openerp.ProductProduct.browse([
    ('standard_margin_rate', '>=', min_rate),
    ('standard_margin_rate', '<', max_rate)])

count = 0

print "found %d products" % (len(products))

for product in products:
    count += 1
    coeff = tax_group_mapping.get(product.tax_group_id.id, False)
    if not coeff:
        print "Skipped product %d %s (tax group %d - %s)" % (
            product.id, product.name, product.tax_group_id.id,
            product.tax_group_id.name)
    else:
        product.write({'list_price': product.standard_price * coeff})
        print "(%d / %d) - Managed new price for %s" % (
            count, len(products), product.name)
