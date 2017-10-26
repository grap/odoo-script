# -*- coding: utf-8 -*-

from unidecode import unidecode
from datetime import datetime
import base64
import erppeek
import csv

from cfg_secret_configuration import odoo_configuration_user


###############################################################################
# Odoo
###############################################################################
# Common Function
def log_out(text):
    print text

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
# Uninstall obsolete Modules
###############################################################################

to_uninstall = [
    # Official modules
    'base_status', 

    # OCA, without Impact
    'web_popup_large', 'web_confirm_window_close', 'email_template_dateutil',

    # GRAP, without impact
    'pos_improve_images', 'pos_second_header', 'sale_reporting',
    'pos_keep_draft_orders', 'pos_improve_header', 'pos_improve_posbox',
    'account_delete_move_null_amount', 'account_mass_drop_moves',
    'account_move_period_date_conform', 'account_tax_update',
    'grap_reporting', 'pos_remove_default_partner',
    'account_merge_moves_by_patterns', 'auth_generate_password',
    'intercompany_trade_purchase_discount',
    'intercompany_trade_purchase_order_reorder_lines',
    'intercompany_trade_purchase_sale',
    'intercompany_trade_sale_order_dates', 'intercompany_trade_stock',
    'module_parent_dependencies',
    'pos_street_market', 'base_calendar_fiscal_company',
    'pos_backup_draft_orders', 'pos_both_mode',
    'purchase_compute_order_pos', 'purchase_compute_order_sale',
    'purchase_compute_order', 'product_get_cost_field',
    'product_stock_cost_field_report', 'sale_fiscal_company',
    'sale_order_mass_action', 'stock_picking_mass_assign',
]

#???'manage_accounts_integrity', 

    # document_page : module pour gérer les how to de GRAP. TODO, chercher
    # grap_change_account_move_line / pos_multiple_cash_control / pos_tax: TODO, merger dans le nouveau module OCA
    # mobile_app_inventory : TODO ? Check in V8.
    # process ??? TODO Check
    # sale_visible_tax ??? TODO Check

modules = openerp.IrModuleModule.browse([('state', '!=', 'uninstalled'), ('name', 'in', to_uninstall)])
for module in modules:
    log_out("Uninstall %s" % (module.name))
    module.module_uninstall()


###############################################################################
# Delete non existing uninstalled Modules
###############################################################################

to_delete = [
    'account_delete_move_null_amount', 'tree_view_record_id',
    'account_invoice_pricelist',
    ]

modules = openerp.IrModuleModule.browse([('state', '=', 'uninstalled'), ('name', 'in', to_delete)])
for module in modules:
    log_out("Delete uninstalled %s" % (module.name))
    module.unlink()


###############################################################################
# Clean Dashboard Tiles
###############################################################################

models = openerp.IrModel.search([('model', 'in', ('stock.picking.in', 'stock.picking.out'))])
tiles = openerp.TileTile.browse([('model_id', 'in', models)])
for tile in tiles:
    log_out("Drop tile %s" % (tile.name))
    tile.unlink()

# clean a bug on pos.order form
# delete from ir_ui_view where id = 1554;
# clean an bug on product.product form (cost_price not found)
# delete from ir_ui_view where id = 1761;

# TO CHECK select * from ir_ui_view where id not in (select res_id from ir_model_data where model='ir.ui.view');
