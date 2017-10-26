#! /usr/bin/env python
# -*- encoding: utf-8 -*-

MAPPING_TAX_GROUP = {
    '5.5': '5.5',
    '5,5': '5.5',
    '5,5%': '5.5',
    '5,50%': '5.5',
    '20': '20.0',
    '20,0%': '20.0',
    '20.0%': '20.0',
    '20,00%': '20.0',
}

MAPPING_COLUMN = {
    'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4,
    'F': 5, 'G': 6, 'H': 7, 'I': 8, 'J': 9,
    'K': 10, 'L': 11, 'M': 12, 'N': 13, 'O': 14,
    'P': 15, 'Q': 16, 'R': 17, 'S': 18, 'T': 19,
    'U': 20, 'V': 21, 'W': 22, 'X': 23, 'Y': 24,
    'Z': 25, 'AA': 26, 'AB': 27, 'AC': 28, 'AD': 29,
    'AE': 30}

MAPPING_UOM = {
    '': 1,
    '1PCE': 1,
    'piece': 1,
    u'Pi\xe8ce': 1,
    'Pi\xc3\xa8ce': 1,
    'pièce': 1,
    'Pièce': 1,
    '1 PCE': 1,
    'unité': 1,
    'unite': 1,
    '01KG': 2,
    'vrac': 2,
    'Vrac': 2,
    'kilo': 2,
    'Kilo': 2,
    'au kilo': 2,
    '01kg': 2,
    '1KG': 2,
    '1 kg': 2,
    '1 Kg': 2,
    'kg': 2,
    'Kg': 2,
    'KG': 2,
    'Colis': 139,
    'COLIS': 139,
    '5 kg': 131,
    '0,6kg': 146,
}

MAPPING_UOM_PO = {
    (2, 1.4): 39,
    (2, 1.5): 16,
    # (2, 1.6): , production only
    (2, 1.7): 141,
    # (2, 1.8): , production only
    (2, 2.0): 20,
    (2, 3.0): 76,
    (2, 4.0): 35,
    (2, 5.0): 131,
    (2, 6.0): 111,
    (2, 7.0): 144,
    # (2, 9.0): , production only
    (2, 10.0): 109,
    (2, 12.0): 9,
    (2, 15.0): 8,
    (2, 20.0): 95,
    (2, 25.0): 7,
}

MAPPING_TO_WEIGHT = {
    '': False,
    '1PCE': False,
    'piece': False,
    'unité': False,
    'unite': False,
    'pièce': False,
    'Pièce': False,
    '01KG': True,
    'vrac': True,
    'Vrac': True,
    '01kg': True,
    'Kg': True,
    '1KG': True,
    'KG': True,
    '1 kg': True,
    '1 Kg': True,
    'Kilo': True,
    'kilo': True,
    'au kilo': True,
    'kg': True,
    '5 kg': True,
}

MAPPING_COUNTRY = {
    '': False,
    'france': 76,
    'thailande': 219,
    'italie': 110,
}
