# -*- encoding: utf-8 -*-

import erppeek
import ConfigParser, os

database_url = 'xxxxx'
database_name = 'xxx'
database_login = 'xx'
database_password = 'xxxx'
next_configuration_path = '/pro/grap/dev/odoo8/etc/openerp_test.cfg'

# Common Function
def log_out(text):
    print text

# Database Connexion
openerp = erppeek.Client(database_url)
uid = openerp.login(database_login, password=database_password, database=database_name)

# List installed modules
installed_module_list = openerp.IrModuleModule.browse([
    ('state', '=', 'installed'),
])

installed_module_names = [x.name for x in installed_module_list]
log_out("%d Modules installed" % len(installed_module_list))

# Get Available Modules
available_modules = {}
config = ConfigParser.ConfigParser()
config.readfp(open(next_configuration_path))
path_list = config.get('options', 'addons_path').split(',')
for directory in path_list:
    for item in os.listdir(directory):
        module_path = os.path.join(directory, item)
        manifest_path = os.path.join(module_path, '__openerp__.py')
        if os.path.exists(manifest_path):
            manifest_file = open(manifest_path)
            current_manifest = eval(manifest_file.read())
            module_item = {
                'name': item,
                'full_path': module_path,
                'installable': current_manifest.get('installable', True),
            }
            available_modules[item] = module_item

for installed_module in installed_module_names:
    to_uninstall = False
    if installed_module not in available_modules.keys():
        to_uninstall = True
        log_out("'%s' Module not found. Uninstalling ..." % installed_module)
    elif not available_modules[installed_module]['installable']:
        to_uninstall = True
        log_out("'%s' Module UNPORTED. Uninstalling ..." % installed_module)
    if to_uninstall:
        module = openerp.IrModuleModule.browse([('name', '=', installed_module)])[0]
        openerp.IrModuleModule.module_uninstall([module.id])
