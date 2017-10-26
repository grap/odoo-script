#! /usr/bin/env python
# -*- encoding: utf-8 -*-

from unidecode import unidecode
import logging
import erppeek
import csv
from datetime import datetime

from mapping import MAPPING_COLUMN,\
    MAPPING_UOM, MAPPING_TO_WEIGHT, MAPPING_COUNTRY, MAPPING_TAX_GROUP,\
    MAPPING_UOM_PO

OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'


# #############################################################################
# Generic functions
# #############################################################################

def log(message, message_type=OKBLUE, error=False):
    message = "%s - %s" % (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"), message)
    print message_type + message + ENDC
    if message_type == FAIL:
        if error:
            raise error
        else:
            raise Exception('spam', 'eggs')


# #############################################################################
# Connection (Odoo, filesystem, ...)
# #############################################################################

def init_openerp(url, login, password, database):
    log("connecting to %s with the login %s ..." % (url, login))
    openerp = erppeek.Client(url)
    uid = openerp.login(login, password=password, database=database)
    user = openerp.ResUsers.browse(uid)
    tz = user.tz
    if openerp:
        log("Connection succeed", OKGREEN)
    else:
        log("connection failed", FAIL)
    return openerp, uid, tz


def open_csv_file(path):
    try:
        csvfile = open(path, 'rb')
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        return spamreader
    except Exception as err:
        log("Opening %s failed." % (path), FAIL, err)


def for_transco(string):
    if type(string) == unicode:
        res = unidecode(string)
    else:
        res = string
    res = res.lower().replace('é', 'e').replace('è', 'e').replace('ê', 'e')
    res = res.replace('à', 'a')
    return res


# #############################################################################
# Generic Method
# #############################################################################

# Get String Value
def get_str_value(row, count, column_name, decode=False):
    if not column_name:
        return ''

    if column_name not in MAPPING_COLUMN:
        log(
            "Column Mapping not done for '%s'" % (column_name), WARNING)
        return ''
    else:
        if row[MAPPING_COLUMN[column_name]]:
            if decode:
                return row[MAPPING_COLUMN[column_name]].strip().decode('utf-8')
            else:
                return row[MAPPING_COLUMN[column_name]].strip()
        else:
            return ''


# Get Float Value
def get_float_value(row, count, column_name):
    res = get_str_value(row, count, column_name)
    if not res:
        return 0
    else:
        try:
            return float(
                res.replace(' ', '').replace('€', '').replace(',', '.').
                replace('%', ''))
        except:
            log(
                "Count %d, column %s. %s is not a valid float value."
                " Default 0.0 value has been used used." % (
                    count, column_name, res), WARNING)
            return 0


# Get Boolean Value
def get_bool_value(row, count, column_name):
    if not column_name:
        return False

    if column_name not in MAPPING_COLUMN:
        log(
            "Column Mapping not done for '%s'" % (column_name), WARNING)
        return ''
    else:
        if row[MAPPING_COLUMN[column_name]]:
            return (row[MAPPING_COLUMN[column_name]].strip() != '')
        else:
            return False


# #############################################################################
# Data : tax.group
# #############################################################################

def get_tax_group_id(row, count, column_name, tax_groups, default_tax_group):
    res = get_str_value(row, count, column_name)
    if res and res in MAPPING_TAX_GROUP:
        return tax_groups[MAPPING_TAX_GROUP[res]]
    else:
        log(
            "'%s' is not a valid tax.group. line #%d."
            " Default '%s' value has been used." % (
                unidecode(res), count, default_tax_group), WARNING)
        return tax_groups[default_tax_group]


# #############################################################################
# Data : product.category
# #############################################################################

# product.category Global Vars
product_category_transco = {}
product_category_unknow_list = []


# Loading product.category
def load_product_category(openerp, default_category):
    log("Loading product.category model ...")
    categories = openerp.ProductCategory.browse([])
    for category in categories:
        product_category_transco[category.complete_name] = category.id
    product_category_transco[''] = default_category
    log("%d product.category loaded." % (len(categories)), OKGREEN)


# Get product.category
def get_product_category_id(row, count, column_name):
    res = get_str_value(row, count, column_name, decode=True)
    if res and res in product_category_transco:
        return product_category_transco.get(res)
    else:
        if unidecode(res) != '':
            if res not in product_category_unknow_list:
                product_category_unknow_list.append(res)
            log(
                "'%s' is not a valid product.category. line #%d."
                " The default one will be used" % (
                    unidecode(res), count), WARNING)
        return product_category_transco.get('')


def get_product_category_unknow_list():
    return product_category_unknow_list


# #############################################################################
# Data : pos.category
# #############################################################################


# pos.category Global Vars
pos_category_transco = {}


# Load pos.category
def load_pos_category(openerp):
    log("Loading pos.category model ...")
    pos_categories = openerp.PosCategory.browse([])
    for pos_category in pos_categories:
        complete_name_without = pos_category.complete_name.replace(' / ', '/')
        pos_category_transco[complete_name_without] = pos_category.id
        pos_category_transco[pos_category.complete_name] = pos_category.id
    log("%d pos.category loaded." % (len(pos_categories)), OKGREEN)


# Get product.category
def get_pos_category_id(
        row, count, column_name, default_pos_category_id, openerp):
    res = get_str_value(row, count, column_name, decode=True)
    if res:
        return create_pos_category_or_return(count, res, openerp)
    else:
        return default_pos_category_id


def create_pos_category_or_return(count, full_name, openerp):
    pos_category_id = pos_category_transco.get(full_name, False)

    if pos_category_id:
        return pos_category_id
    else:
        # Post category has not been found
        split = full_name.split('/')
        if len(split) > 1:
            # It is a view category
            parent_category_id = create_pos_category_or_return(
                count, '/'.join(split[:-1]), openerp)
        else:
            parent_category_id = False
        # Create a category (view or normal)
        log(
            "'%s' pos.category not found. line #%d."
            " Creating a new one" % (unidecode(full_name), count))
        pos_category = openerp.PosCategory.create({
            'parent_id': parent_category_id,
            'name': split[-1:][0],
        })
        complete_name_without = pos_category.complete_name.replace(' / ', '/')
        pos_category_transco[complete_name_without] = pos_category.id
        pos_category_transco[pos_category.complete_name] = pos_category.id
        log("%s pos.category created (#%d)." % (
            pos_category.complete_name, pos_category_id), OKGREEN)
    return pos_category.id


# #############################################################################
# Data : product.label
# #############################################################################


# product.label Global Vars
product_label_transco = {}
product_label_unknow_list = []


# Load product.label
def load_product_label(openerp):
    log("Loading product.label model ...")
    labels = openerp.ProductLabel.browse([])
    for label in labels:
        product_label_transco[for_transco(label.name)] = label.id
        product_label_transco[for_transco(label.code)] = label.id
    log("%d product.label loaded." % (len(labels)), OKGREEN)


# Get product.label
def get_product_label_id(row, count, column_name):
    res = get_str_value(row, count, column_name)
    key = for_transco(res)
    if not key:
        return False
    elif key in product_label_transco:
        return product_label_transco.get(key)
    else:
        log(
            "'%s' is not a valid product.label. line #%d."
            " The value has been ignored." % (
                key, count), WARNING)
        if key not in product_label_unknow_list:
            product_label_unknow_list.append(key)
        return False


def get_product_label_unknow_list():
    return product_label_unknow_list


# #############################################################################
# Data : res.partner
# #############################################################################

# res.partner Global Vars
res_partner_transco = {}


# Load res.partner
def load_res_partner(openerp):
    log("Loading res.partner model ...")
    partners = openerp.ResPartner.browse([])
    for partner in partners:
        res_partner_transco[for_transco(partner.name)] = partner.id
    log("%d res.partner loaded." % (len(partners)), OKGREEN)


# Get res.partner
def get_res_partner_id(row, count, column_name, openerp):
    res = get_str_value(row, count, column_name, decode=True)
    if res:
        partner_id = res_partner_transco.get(for_transco(res), False)
        if not partner_id:
            log(
                "'%s' res.partner not found. line #%d."
                " Creating a new one" % (unidecode(res), count), WARNING)
            partner_id = openerp.ResPartner.create({
                'name': res,
                'supplier': True,
                'customer': False,
                'active': True,
                'is_company': True,
            }).id
            res_partner_transco[for_transco(res)] = partner_id
            log("%s res.partner created (#%d)." % (
                unidecode(res), partner_id), OKGREEN)
        return partner_id
    return False


# #############################################################################
# Data : crm.case.stage
# #############################################################################

def get_crm_case_stage_id(
        row, count, column_name, crm_case_stages, default_crm_case_stage):
    res = get_str_value(row, count, column_name)
    key = for_transco(res)
    if key in crm_case_stages:
        return crm_case_stages[key]
    else:
        log(
            "'%s' is not a valid crm.case.stage. line #%d."
            " Default '%s' value has been used." % (
                unidecode(res), count, default_crm_case_stage), WARNING)
        return crm_case_stages[default_crm_case_stage]


# #############################################################################
# Settings : res.country
# #############################################################################

# Get res.country
def get_res_country_id(row, count, column_name):
    res = get_str_value(row, count, column_name, decode=True)
    if res:
        country_id = MAPPING_COUNTRY.get(res, False)
        if not country_id:
            log(
                "'%s' is not a valid res.country. line #%d."
                " The value has been ignored." % (
                    unidecode(res), count), WARNING)
        return country_id
    else:
        return False


# #############################################################################
# Settings : product.uom
# #############################################################################

product_uom_po_unknow_list = []


# Get product.uom
def get_product_uom_id(row, count, column_name):
    res = get_str_value(row, count, column_name)
    if res and res in MAPPING_UOM:
        return MAPPING_UOM[res]
    else:
        log(
            "'%s' is not a valid product.uom. line #%d."
            " Default 'Piece' UoM has been used." % (
                unidecode(res), count), WARNING)
        return MAPPING_UOM['']


# Get product.uom
def compute_product_uom_po_id(uom_id, invoice_qty):
    if invoice_qty == 1.0 or invoice_qty == 0.0:
        return uom_id
    if (uom_id, invoice_qty) in MAPPING_UOM_PO:
        return MAPPING_UOM_PO[(uom_id, invoice_qty)]
    else:
        log(
            "Unable to found uom_po_id from uom_id '%s' and invoice_qty '%s'"
            " Default uom id used." % (
                uom_id, invoice_qty), WARNING)
        if (uom_id, invoice_qty) not in product_uom_po_unknow_list:
            product_uom_po_unknow_list.append((uom_id, invoice_qty))
        return uom_id


def get_product_uom_po_unknow_list():
    return product_uom_po_unknow_list


# #############################################################################
# Settings : product.product 'to_weight' fields.
# #############################################################################

# Get product.product, to_weight
def get_product_to_weight(row, count, column_name):
    res = get_str_value(row, count, column_name)
    if res and res in MAPPING_TO_WEIGHT:
        return MAPPING_TO_WEIGHT[res]
    else:
        log(
            "'%s' is an unknown 'to_weight' product.uom. line #%d."
            " Default 'False' value has been used." % (
                unidecode(res), count), WARNING)
        return MAPPING_TO_WEIGHT['']
