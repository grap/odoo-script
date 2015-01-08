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
    'test',
    'resto_2015_01_07_a',
)

def fix_payment_move():
    rc_lst = openerp.ResCompany.browse([
        ('fiscal_company', '=', 3),
    ])
    aj_lst = openerp.AccountJournal.browse([
        ('company_id', '=', 3),
        ('code', 'in', ('CB', 'CH', 'CS', 'TR')),
    ])
    for rc in rc_lst:
#    if True:
#        rc = rc_lst[8]
        print "****** Company : %s ****************" % rc.name
        am_ids = []
        for aj in aj_lst:
            print "****** Journal : %s " % aj.name
            # For each journal
            am_lst = openerp.AccountMove.browse([
                ('company_id', '=', rc.id),
                ('journal_id', '=', aj.id),
                ('date', '>=', '01/01/2014'),
                ('date', '<=', '31/12/2014'),
                ('name', 'not ilike', '%/%/%/%'),
            ])
            for am in am_lst:
                if am.ref:
                    if am.ref == am.name[0:3] + '20' + am.name[3:]:
                        am_ids.append(am.id)
                else:
                    print "warning : %s" % am.name

            if am_ids: 
                am_lst = openerp.AccountMove.browse(am_ids)
                for am in am_lst:
                    print "**************"
                    print am
                    print am.name
                    print am.ref
                    print "Fixing %s (Ref: %s)" % (am.name, am.ref)
                    abs_lst = openerp.AccountBankStatement.browse([
                        ('name', '=', am.ref),
                    ])
                    assert len(abs_lst) == 1, "Account Bank Statement Not Found %s" % (am.ref)
                    abs = abs_lst[0]
                    keys = {}
                    for absl in abs.line_ids:
                        if absl.ref == False: # TODO
                            assert False, "Merde la ref"
                        key = (
                            absl.date,
                            absl.partner_id and absl.partner_id.id,
                            absl.type,
                            absl.account_id.id,
                            absl.ref)

                        if key not in keys.keys():
                            keys[key] = absl.amount
                        else:
                            keys[key] += absl.amount
                    print keys

                    # Create new Account Moves for each keys
                    i = 1
                    for key in keys:
                        ap_id = openerp.AccountPeriod.search([
                            ('name', '=', key[0][5:7] + '/' + key[0][0:4]),
                            ('company_id', '=', 3),
                        ])[0]
                        move_id = openerp.AccountMove.create({
                            'name': am.name + '/' + str(i),
                            'ref': key[4],
                            'date': key[0],
                            'company_id': rc.id,
                            'partner_id': key[1],
                            'journal_id': aj.id,
                            'period_id': ap_id,
                        })
                        value = keys[key]
                        if value > 0:
                            # Bank Line
                            openerp.AccountMoveLine.create({
                                'move_id': move_id.id,
                                'partner_id': key[1],
                                'name': am.name,
                                'account_id': aj.default_debit_account_id,
                                'debit': value,
                                'credit': 0,
                            })
                            # CounterPart Line 7 or 411
                            openerp.AccountMoveLine.create({
                                'move_id': move_id.id,
                                'partner_id': key[1],
                                'name': am.name,
                                'account_id': key[3],
                                'debit': 0,
                                'credit': value,
                            })
                        else:
                            # Bank Line
                            openerp.AccountMoveLine.create({
                                'move_id': move_id.id,
                                'partner_id': key[1],
                                'name': am.name,
                                'account_id': aj.default_debit_account_id,
                                'debit': 0,
                                'credit': - value,
                            })
                            # CounterPart Line 7 or 411
                            openerp.AccountMoveLine.create({
                                'move_id': move_id.id,
                                'partner_id': key[1],
                                'name': am.name,
                                'account_id': key[3],
                                'debit': - value,
                                'credit': 0,
                            })
                        # Validate new Account Move
                        print move_id
                        openerp.execute('account.move', 'button_validate', ([move_id.id]))
                        i += 1
                    # Drop old Account Move
                    openerp.AccountUnexportEbp.unexport(False, ({'active_ids': [am.id]}))
                    openerp.execute('account.move', 'button_cancel', ([am.id]))
                    openerp.AccountMove.unlink([am.id])


fix_payment_move()
