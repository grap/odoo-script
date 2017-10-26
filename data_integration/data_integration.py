#! /usr/bin/env python
# -*- encoding: utf-8 -*-

from unidecode import unidecode

from cfg_secret_configuration import odoo_configuration_user

from tools import init_openerp,\
    log, OKGREEN, WARNING,\
    get_product_uom_id, compute_product_uom_po_id,\
    get_tax_group_id, get_product_to_weight,\
    get_res_country_id,\
    get_str_value, get_float_value, get_bool_value,\
    load_product_category, get_product_category_id,\
    get_product_category_unknow_list,\
    load_pos_category, get_pos_category_id,\
    get_product_label_unknow_list,\
    get_product_uom_po_unknow_list,\
    load_product_label, get_product_label_id,\
    load_res_partner, get_res_partner_id,\
    get_crm_case_stage_id,\
    open_csv_file

from per_activity.HAL_configuration import (
    COMPANY_ID,

    PRODUCT_FIRST_LINE,
    DEFAULT_POS_CATEG_ID, TAX_GROUPS, DEFAULT_TAX_GROUP,
    DEFAULT_PRODUCT_CATEGORY, COLUMN_PRODUCT_NAME, COLUMN_PRODUCT_UOM_ID,
    COLUMN_PRODUCT_CATEG_ID,
    COLUMN_PRODUCT_POS_CATEG_ID, COLUMN_PRODUCT_SUPPLIER_NAME,
    COLUMN_PRODUCT_SUPPLIER_PRODUCT_CODE, COLUMN_PRODUCT_SUPPLIER_PRODUCT_NAME,
    COLUMN_PRODUCT_SUPPLIER_GROSS_PRICE, COLUMN_PRODUCT_SUPPLIER_DISCOUNT,
    COLUMN_PRODUCT_SUPPLIER_PACKAGE_QTY, COLUMN_PRODUCT_MAKER,
    COLUMN_PRODUCT_EAN_13, COLUMN_PRODUCT_VOLUME, COLUMN_PRODUCT_NET_WEIGHT,
    COLUMN_PRODUCT_COUNTRY_ID, COLUMN_PRODUCT_TAX_GROUP_ID,
    COLUMN_PRODUCT_STANDARD_PRICE,
    COLUMN_PRODUCT_SUPPLIER_INVOICE_QTY, COLUMN_PRODUCT_SALE_PRICE,
    COLUMN_PRODUCT_SALE_ALTERNATIVE, COLUMN_PRODUCT_LABEL_1,
    COLUMN_PRODUCT_LABEL_2, COLUMN_PRODUCT_LABEL_3,

    PARTNER_FIRST_LINE,
    COLUMN_PARTNER_NAME, COLUMN_PARTNER_EMAIL, COLUMN_PARTNER_PHONE,
    COLUMN_PARTNER_FAX,
    COLUMN_PARTNER_MOBILE, COLUMN_PARTNER_WEBSITE, COLUMN_PARTNER_VAT,
    COLUMN_PARTNER_STREET, COLUMN_PARTNER_ZIP, COLUMN_PARTNER_CITY,
    COLUMN_PARTNER_COUNTRY_ID, COLUMN_PARTNER_COMMENT,
    COLUMN_PARTNER_IS_CUSTOMER, COLUMN_PARTNER_IS_SUPPLIER,
    COLUMN_PARTNER_IS_INDIVIDUAL,

    LEAD_FIRST_LINE,
    DEFAULT_CRM_CASE_STAGE, CRM_CASE_STAGES, DEFAULT_LEAD_TYPE,
    COLUMN_LEAD_NAME, COLUMN_LEAD_EMAIL, COLUMN_LEAD_PHONE,
    COLUMN_LEAD_MOBILE, COLUMN_LEAD_COUNTRY_ID, COLUMN_LEAD_STAGE,
    COLUMN_LEAD_STREET, COLUMN_LEAD_ZIP, COLUMN_LEAD_CITY,
    COLUMN_LEAD_DESCRIPTION
)


# #############################################################################
# Odoo
# #############################################################################

# Connection
openerp, uid, tz = init_openerp(
    odoo_configuration_user['url'],
    odoo_configuration_user['login'],
    odoo_configuration_user['password'],
    odoo_configuration_user['database'])


# #############################################################################
# Partner Creation
# #############################################################################
if odoo_configuration_user.get('partner_file_path', False):
    log("Trying to  process Partner %s file" % (
        odoo_configuration_user['partner_file_path']))
    spamreader = open_csv_file(odoo_configuration_user['partner_file_path'])
    count = 0
    for row in spamreader:
        count += 1
        if count >= PARTNER_FIRST_LINE:
            log("Handling line #%d ..." % (count))
            partner_vals = {
                'company_id': COMPANY_ID,
                'name': get_str_value(row, count, COLUMN_PARTNER_NAME),
                'email': get_str_value(row, count, COLUMN_PARTNER_EMAIL),
                'phone': get_str_value(row, count, COLUMN_PARTNER_PHONE),
                'fax': get_str_value(row, count, COLUMN_PARTNER_FAX),
                'mobile': get_str_value(row, count, COLUMN_PARTNER_MOBILE),
                'website': get_str_value(row, count, COLUMN_PARTNER_WEBSITE),
                'vat': get_str_value(row, count, COLUMN_PARTNER_VAT),
                'street': get_str_value(row, count, COLUMN_PARTNER_STREET),
                'zip': get_str_value(row, count, COLUMN_PARTNER_ZIP),
                'city': get_str_value(row, count, COLUMN_PARTNER_CITY),
                'comment': get_str_value(row, count, COLUMN_PARTNER_COMMENT),
                'country_id': get_res_country_id(
                    row, count, COLUMN_PARTNER_COUNTRY_ID),
                'customer': get_bool_value(
                    row, count, COLUMN_PARTNER_IS_CUSTOMER),
                'supplier': get_bool_value(
                    row, count, COLUMN_PARTNER_IS_SUPPLIER),
                'is_company': not get_bool_value(
                    row, count, COLUMN_PARTNER_IS_INDIVIDUAL),
            }
            partner = openerp.ResPartner.create(partner_vals)
            log("Partner Created #%d %s" % (
                partner.id, unidecode(partner.name)), OKGREEN)

# #############################################################################
# Product Creation
# #############################################################################
if odoo_configuration_user.get('product_file_path', False):
    # Loading Data
    load_product_category(openerp, DEFAULT_PRODUCT_CATEGORY)
    load_pos_category(openerp)
    load_product_label(openerp)
    load_res_partner(openerp)
    incorrect_barcode_dict = {}

    log("Trying to process Product %s file" % (
        odoo_configuration_user['product_file_path']))
    spamreader = open_csv_file(odoo_configuration_user['product_file_path'])
    count = 0
    for row in spamreader:
        count += 1
        if count >= PRODUCT_FIRST_LINE:
            log("Handling line #%d ..." % (count))
            if get_str_value(row, count, COLUMN_PRODUCT_NAME) == '':
                continue

            # Handle Labels
            label_ids = []
            label_1 = get_product_label_id(row, count, COLUMN_PRODUCT_LABEL_1)
            if label_1:
                label_ids.append(label_1)
            label_2 = get_product_label_id(row, count, COLUMN_PRODUCT_LABEL_2)
            if label_2:
                label_ids.append(label_2)
            label_3 = get_product_label_id(row, count, COLUMN_PRODUCT_LABEL_3)
            if label_3:
                label_ids.append(label_3)

            invoice_qty = get_float_value(
                row, count, COLUMN_PRODUCT_SUPPLIER_INVOICE_QTY)

            # Handle uom id. (normal and Purchase)
            uom_id = get_product_uom_id(row, count, COLUMN_PRODUCT_UOM_ID)
            uom_po_id = compute_product_uom_po_id(uom_id, invoice_qty)

            # Get standard price if given
            standard_price = get_float_value(
                row, count, COLUMN_PRODUCT_STANDARD_PRICE)

            if not standard_price:
                # otherwise, compute standard price based on purchase price
                standard_price = (
                    get_float_value(
                        row, count, COLUMN_PRODUCT_SUPPLIER_GROSS_PRICE) *
                    (100 - get_float_value(
                        row, count, COLUMN_PRODUCT_SUPPLIER_DISCOUNT)) / 100)

                if invoice_qty:
                    standard_price = standard_price / invoice_qty

            product_vals = {
                'company_id': COMPANY_ID,
                'name': get_str_value(
                    row, count, COLUMN_PRODUCT_NAME),
                'ean13': get_str_value(
                    row, count, COLUMN_PRODUCT_EAN_13),
                'uom_id': uom_id,
                'to_weight': get_product_to_weight(
                    row, count, COLUMN_PRODUCT_UOM_ID),
                'uom_po_id': uom_po_id,
                'standard_price': standard_price,
                'list_price': (
                    get_float_value(
                        row, count, COLUMN_PRODUCT_SALE_PRICE) or
                    get_float_value(
                        row, count, COLUMN_PRODUCT_SALE_ALTERNATIVE)),
                'active': True,
                'sale_ok': True,
                'purchase_ok': True,
                'tax_group_id': get_tax_group_id(
                    row, count, COLUMN_PRODUCT_TAX_GROUP_ID, TAX_GROUPS,
                    DEFAULT_TAX_GROUP),
                'volume': get_float_value(
                    row, count, COLUMN_PRODUCT_VOLUME),
                'weight_net': get_float_value(
                    row, count, COLUMN_PRODUCT_NET_WEIGHT),
                'categ_id': get_product_category_id(
                    row, count, COLUMN_PRODUCT_CATEG_ID),
                'country_id': get_res_country_id(
                    row, count, COLUMN_PRODUCT_COUNTRY_ID),
                'label_ids': label_ids,
                'pos_categ_id': get_pos_category_id(
                    row, count, COLUMN_PRODUCT_POS_CATEG_ID,
                    DEFAULT_POS_CATEG_ID, openerp),
                'maker_description': get_str_value(
                    row, count, COLUMN_PRODUCT_MAKER),
            }
            if get_str_value(row, count, COLUMN_PRODUCT_SUPPLIER_NAME):
                partner_id = get_res_partner_id(
                        row, count, COLUMN_PRODUCT_SUPPLIER_NAME, openerp)
                if partner_id:
                    pass
                    product_vals['seller_ids'] = [[0, False, {
                        'sequence': 1,
                        'name': partner_id,
                        'company_id': COMPANY_ID,
                        'product_name': get_str_value(
                            row, count, COLUMN_PRODUCT_SUPPLIER_PRODUCT_NAME),
                        'product_code': get_str_value(
                            row, count, COLUMN_PRODUCT_SUPPLIER_PRODUCT_CODE),
                        'min_qty': get_float_value(
                            row, count,
                            COLUMN_PRODUCT_SUPPLIER_PACKAGE_QTY) or 0,
                        'package_qty': get_float_value(
                            row, count,
                            COLUMN_PRODUCT_SUPPLIER_PACKAGE_QTY) or 1,
                        'delay': 0,
                        'pricelist_ids': [[0, False, {
                            'min_quantity': 0,
                            'price': get_float_value(
                                row, count,
                                COLUMN_PRODUCT_SUPPLIER_GROSS_PRICE),
                            'discount': get_float_value(
                                row, count,
                                COLUMN_PRODUCT_SUPPLIER_DISCOUNT),
                        }]],
                    }]]
                else:
                    log(
                        "Partner %s not found in the database."
                        " Supplier info has been skipped" % (get_str_value(
                            row, count, COLUMN_PRODUCT_SUPPLIER_NAME)),
                        WARNING)

            if odoo_configuration_user.get('product_create', False):
                try:
                    # Create Product
                    product = openerp.ProductProduct.create(product_vals)
                    # Force write to compute correctly margin
                    openerp.ProductProduct.write(
                        [product.id],
                        {'list_price': product_vals['list_price']})
                    log("Product Created #%d %s-%s" % (
                        product.id, unidecode(product.default_code),
                        unidecode(product.name)),
                        OKGREEN)
                except Exception as err:
                    if 'EAN13 Barcode' in err.faultCode:
                        log("Incorrect Barcode %s. Retrying without ..." % (
                            product_vals['ean13']),
                            WARNING)
                        incorrect_barcode_dict[product_vals['ean13']] =\
                            product_vals['name']
                        # Trying again to create Product
                        product_vals['ean13'] = False
                        product = openerp.ProductProduct.create(product_vals)
                        # Force write to compute correctly margin
                        openerp.ProductProduct.write(
                            [product.id],
                            {'list_price': product_vals['list_price']})
                        log("Product Created #%d %s-%s" % (
                            product.id, unidecode(product.default_code),
                            unidecode(product.name)),
                            OKGREEN)
                    else:
                        raise err
                    pass
    product_category_list = get_product_category_unknow_list()
    product_label_list = get_product_label_unknow_list()
    product_uom_po_unknow_list = get_product_uom_po_unknow_list()
    if product_category_list:
        log(
            "Unknown product.category found:\n%s\n" % (
                '\n'.join(product_category_list)),
            WARNING)
    if product_label_list:
        log(
            "Unknown product.label found: \n%s\n" % (
                '\n'.join(product_label_list)),
            WARNING)
    if incorrect_barcode_dict:
        incorrect_barcode_list =\
            ["%s - %s" % (k, v) for k, v in incorrect_barcode_dict.iteritems()]
        log(
            "Incorrect Barcode found: \n%s\n" % (
                '\n'.join(incorrect_barcode_list)),
            WARNING)
    if product_uom_po_unknow_list:
        log("Incorrect combination uom po found: \n", WARNING)
        for x in product_uom_po_unknow_list:
            log(" - %s" % (str(x)), WARNING)

# #############################################################################
# Partner Creation
# #############################################################################
if odoo_configuration_user.get('lead_file_path', False):
    log("Trying to  process Lead %s file" % (
        odoo_configuration_user['lead_file_path']))
    spamreader = open_csv_file(odoo_configuration_user['lead_file_path'])
    count = 0
    for row in spamreader:
        count += 1
        if count >= LEAD_FIRST_LINE:
            log("Handling line #%d ..." % (count))
            lead_vals = {
                'company_id': COMPANY_ID,
                'stage_id': get_crm_case_stage_id(
                    row, count, COLUMN_LEAD_STAGE, CRM_CASE_STAGES,
                    DEFAULT_CRM_CASE_STAGE),
                'type': DEFAULT_LEAD_TYPE,
                'name': get_str_value(row, count, COLUMN_LEAD_NAME),
                'email_from': get_str_value(row, count, COLUMN_LEAD_EMAIL),
                'phone': get_str_value(row, count, COLUMN_LEAD_PHONE),
                'mobile': get_str_value(row, count, COLUMN_LEAD_MOBILE),
                'street': get_str_value(row, count, COLUMN_LEAD_STREET),
                'zip': get_str_value(row, count, COLUMN_LEAD_ZIP),
                'city': get_str_value(row, count, COLUMN_LEAD_CITY),
                'state_id': False,
                'country_id': get_res_country_id(
                    row, count, COLUMN_LEAD_COUNTRY_ID),
                'description': get_str_value(
                    row, count, COLUMN_LEAD_DESCRIPTION),
            }
            lead = openerp.CrmLead.create(lead_vals)
            log("Lead Created #%d %s" % (
                lead.id, unidecode(lead.name)), OKGREEN)
