
Features
========

- Create product from csv file.
- Create supplier from csv file.
- Create Opportunities from csv file.

to use this tools :

- change your import in data_integration.py 
```
from per_activity.XXX_configuration import (
```

Add an extra file with your credentials named, cfg_secret_configuration

```
#! /usr/bin/env python
# -*- encoding: utf-8 -*-
# flake8: noqa
# pylint: skip-file

# TRIGRAMME - Configuration
odoo_configuration_user = {
    'url':  'https://xxx.xxx.xxx/',
    'login': 'XXX',
    'password': 'XXX',
    'database': 'XXX',
    'partner_file_path': False,
    'product_file_path': False,
    'lead_file_path': False,
    'product_create': False,
}
```
