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
# CONSTANTE
###############################################################################

BARCODE_RULE = 10

###############################################################################
# Script
###############################################################################

products = openerp.ProductProduct.browse([('scale_group_id', '!=', False)])

print "product found %d" % len(products)

for product in products:
    generating_base = False
    setting_barcode_rule = False
    old_barcode = product.ean13
    if not product.barcode_rule_id:
        openerp.ProductProduct.write([product.id], {'barcode_rule_id': BARCODE_RULE})
        generating_base = True
    if not product.barcode_base:
        openerp.ProductProduct.generate_base([product.id])
        setting_barcode_rule = True
    openerp.ProductProduct.generate_barcode([product.id])
    new_product = products = openerp.ProductProduct.browse([product.id])
    print "%s - %s --> %s" % (product.name, old_barcode, new_product.ean13)
    if generating_base:
        print "   generating_base"
        print "   setting_barcode_rule"
