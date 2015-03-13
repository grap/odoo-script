# -*- coding: utf-8 -*-
import erppeek

COMPTE_CLIENT = 389


def init_openerp(url, login, password, database):
    try:
        openerp = erppeek.Client(url)
        uid = openerp.login(login, password=password, database=database)
        return openerp, uid
    except:
        return False, False

openerp, uid = init_openerp(
    'http://localhost:8069',
    'admin',
    'admin',
    'admin',
)


def fix_account_invoice_state():
    
    ru = openerp.ResUsers.browse(uid)
    rc_lst = openerp.ResCompany.browse([
        ('fiscal_company', '=', 3),
    ])
    for rc in rc_lst:
        print "==============================================================="
        print "================= Company %s =================" % (rc.name)
        print "==============================================================="
        ru.write({'company_id': rc.id})

        # Get Invoice 'open' with balance = '0'
        ai_lst = openerp.AccountInvoice.browse([
            ('type', '=', 'out_invoice'),
            ('state', '=', 'open'),
            ('residual', '=', 0)
        ])

        if not ai_lst:
            continue
        for ai in ai_lst:
            total = 0
            print "*** Invoice '%s' # %s - (%s) Total %s" % (
                ai.name, ai.id, ai.date_invoice, ai.amount_total)
            # Vérifier si le paiement correspond bien au total de la facture
            for aml in ai.payment_ids:
                total += aml.credit - aml.debit
                print "-> payé avec %s (%s) - (%s - %s)" % (
                    aml.name, aml.date, aml.debit, aml.credit)
            if total != ai.amount_total < 0.0000001:
                print "WARNING invalid residual value."\
                    "Invoice %s. Paid %s (Diff: %s)" % (
                    ai.amount_total, total, ai.amount_total - total)
            else:
                print "FIXED (set to paid)"
                openerp.AccountInvoice.confirm_paid([ai.id])

fix_account_invoice_state()
