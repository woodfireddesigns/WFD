/* WFD Money: bills, income, debts, goals, budgets, cash-flow plan. Supabase-backed. */
(function () {
  'use strict';
  var SUPABASE_URL = 'https://aqeipagwuerfosxdgkie.supabase.co';
  var SUPABASE_KEY = 'sb_publishable_5xuWTfWdLloVXMWVAmGwZw_ZEk68Qu5';
  var REQUIRE_LOGIN = false; // open access for now; flip to true (and private.fin_open_access() to false) to require login
  var sb = supabase.createClient(SUPABASE_URL, SUPABASE_KEY);
  var L = FinLogic;

  // ---------- tiny DOM helpers ----------
  function $(s) { return document.querySelector(s); }
  function el(tag, attrs) {
    var e = document.createElement(tag);
    if (attrs) Object.keys(attrs).forEach(function (k) {
      var v = attrs[k];
      if (v === null || v === undefined || v === false) return;
      if (k === 'class') e.className = v;
      else if (k === 'html') e.innerHTML = v;
      else if (k.indexOf('on') === 0) e.addEventListener(k.slice(2), v);
      else if (k === 'style') e.style.cssText = v;
      else e.setAttribute(k, v === true ? '' : v);
    });
    for (var i = 2; i < arguments.length; i++) append(e, arguments[i]);
    return e;
  }
  function append(e, c) {
    if (c === null || c === undefined || c === false) return;
    if (Array.isArray(c)) { c.forEach(function (x) { append(e, x); }); return; }
    e.appendChild(c.nodeType ? c : document.createTextNode(String(c)));
  }
  function clear(e) { while (e.firstChild) e.removeChild(e.firstChild); return e; }
  var toastTimer;
  function toast(msg, isErr) {
    var t = $('#toast'); t.textContent = msg; t.style.color = isErr ? 'var(--red)' : ''; t.classList.add('on');
    clearTimeout(toastTimer); toastTimer = setTimeout(function () { t.classList.remove('on'); }, isErr ? 4200 : 2200);
  }
  function fmt(c, o) { return L.fmt(c, o); }
  var MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  var DOW = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  function fdate(s, withDow) { if (!s) return ''; var d = L.parse(s); return (withDow ? DOW[d.getDay()] + ' ' : '') + MONTHS[d.getMonth()] + ' ' + d.getDate(); }
  function relDue(s) {
    var n = L.diffDays(L.today(), s);
    if (n < -1) return Math.abs(n) + ' days late'; if (n === -1) return 'Yesterday'; if (n === 0) return 'Today'; if (n === 1) return 'Tomorrow';
    if (n < 7) return DOW[L.parse(s).getDay()]; return fdate(s);
  }
  function pct(n) { return Math.round(n * 100) + '%'; }
  function initial(s) { return (s || '?').trim().charAt(0).toUpperCase(); }

  // ---------- state ----------
  var S = { user: null, tab: 'today', accounts: [], bills: [], payments: [], income: [], debts: [], debtPayments: [], goals: [], budgets: [], spend: [], pending: [],
    prefs: loadPrefs(), sub: { bills: 'upcoming', income: 'expected' } };
  function loadPrefs() { try { return JSON.parse(localStorage.getItem('wfd-money-prefs') || '{}'); } catch (e) { return {}; } }
  function savePrefs() { try { localStorage.setItem('wfd-money-prefs', JSON.stringify(S.prefs)); } catch (e) {} }
  function reserveCents() { return S.prefs.reserve || 0; }

  // ---------- data ----------
  function q(p) { return p.then(function (r) { if (r.error) throw r.error; return r.data; }); }
  function loadAll() {
    var t = L.today(), back = L.addDays(t, -90), back60 = L.addDays(t, -60), ms = L.monthStart(L.addMonths(t, -7));
    return Promise.all([
      q(sb.from('fin_accounts').select('*').eq('archived', false).order('sort_order').order('name')),
      q(sb.from('fin_bills').select('*').eq('active', true).order('next_due_date')),
      q(sb.from('fin_bill_payments').select('*').gte('paid_on', back).order('paid_on', { ascending: false }).order('created_at', { ascending: false })),
      q(sb.from('fin_income').select('*').or('received_on.is.null,expected_date.gte.' + back60).order('expected_date')),
      q(sb.from('fin_debts').select('*').eq('active', true).order('balance_cents', { ascending: false })),
      q(sb.from('fin_debt_payments').select('*').gte('paid_on', back).order('paid_on', { ascending: false })),
      q(sb.from('fin_goals').select('*').eq('active', true).order('created_at')),
      q(sb.from('fin_budgets').select('*').eq('active', true).order('kind').order('sort_order').order('name')),
      q(sb.from('fin_spend').select('*').gte('spent_on', ms).order('spent_on', { ascending: false }).order('created_at', { ascending: false })),
      q(sb.from('fin_pending').select('*').is('cleared_on', null).order('expects_on', { nullsFirst: false }))
    ]).then(function (r) {
      S.accounts = r[0]; S.bills = r[1]; S.payments = r[2]; S.income = r[3]; S.debts = r[4]; S.debtPayments = r[5]; S.goals = r[6]; S.budgets = r[7]; S.spend = r[8]; S.pending = r[9];
    });
  }
  function refresh() { return loadAll().then(render).catch(function (e) { toast(e.message || 'Load failed', true); }); }
  function acct(id) { return S.accounts.find(function (a) { return a.id === id; }); }
  function debt(id) { return S.debts.find(function (d) { return d.id === id; }); }
  function bill(id) { return S.bills.find(function (b) { return b.id === id; }); }
  function budget(id) { return S.budgets.find(function (b) { return b.id === id; }); }
  function cashAccounts() { return S.accounts.filter(function (a) { return a.type !== 'credit'; }); }

  // Balances are whatever the bank says right now. Anything still moving lives in
  // fin_pending, so "available" is the balance plus what is landing minus what is
  // about to leave. source_debited means the money is already out of the sending
  // account, so only the receiving end is still outstanding.
  function pendingNet(accountId) {
    return S.pending.reduce(function (s, p) {
      if (p.to_account_id === accountId) return s + p.amount_cents;
      if (p.from_account_id === accountId && !p.source_debited) return s - p.amount_cents;
      return s;
    }, 0);
  }
  function pendingNetAll() {
    return cashAccounts().reduce(function (s, a) { return s + pendingNet(a.id); }, 0);
  }
  // A bill being paid right now is already priced into available cash by its pending row.
  // Leave it in the pay plan too and the same money comes off the balance twice.
  function billsNotInFlight() {
    var paying = S.pending.filter(function (p) { return p.bill_id; }).map(function (p) { return p.bill_id; });
    return paying.length ? S.bills.filter(function (b) { return paying.indexOf(b.id) < 0; }) : S.bills;
  }
  function cards() { return S.debts.filter(function (d) { return d.kind === 'credit_card'; }); }

  // ---------- auth ----------
  var recovering = false;
  function showAuth(on) { $('#auth').hidden = !on; $('#app').classList.toggle('on', !on); }
  $('#auth-form').addEventListener('submit', function (ev) {
    ev.preventDefault(); var m = $('#auth-msg'); m.className = 'auth-msg'; m.textContent = 'Signing in…';
    sb.auth.signInWithPassword({ email: $('#auth-email').value.trim(), password: $('#auth-pass').value }).then(function (r) {
      if (r.error) { m.className = 'auth-msg err'; m.textContent = r.error.message; } else m.textContent = '';
    });
  });
  $('#auth-forgot').addEventListener('click', function () {
    var email = $('#auth-email').value.trim(), m = $('#auth-msg'); m.className = 'auth-msg';
    if (!email) { m.className = 'auth-msg err'; m.textContent = 'Enter your email first.'; return; }
    sb.auth.resetPasswordForEmail(email, { redirectTo: location.origin + '/' }).then(function (r) {
      m.className = r.error ? 'auth-msg err' : 'auth-msg'; m.textContent = r.error ? r.error.message : 'Reset link sent. Open it on this device.';
    });
  });
  $('#reset-form').addEventListener('submit', function (ev) {
    ev.preventDefault(); var m = $('#auth-msg'); m.className = 'auth-msg';
    sb.auth.updateUser({ password: $('#reset-pass').value }).then(function (r) {
      if (r.error) { m.className = 'auth-msg err'; m.textContent = r.error.message; return; }
      recovering = false; $('#reset-form').hidden = true; $('#auth-form').hidden = false; m.textContent = ''; history.replaceState(null, '', '/'); boot(r.data.user);
    });
  });
  sb.auth.onAuthStateChange(function (event, session) {
    if (event === 'PASSWORD_RECOVERY') { recovering = true; showAuth(true); $('#auth-form').hidden = true; $('#reset-form').hidden = false; $('#auth-msg').textContent = 'Choose a new password.'; return; }
    if (session && session.user && !recovering) boot(session.user);
    else if (!session) { S.user = null; if (REQUIRE_LOGIN) showAuth(true); }
  });
  var booted = false;
  function boot(user) {
    S.user = user; $('#who').textContent = user.email; showAuth(false);
    if (booted) return; booted = true;
    refresh();
  }
  if (REQUIRE_LOGIN) sb.auth.getSession().then(function (r) { if (!(r.data && r.data.session)) showAuth(true); });
  else { showAuth(false); $('#who').textContent = 'Open access'; booted = true; refresh(); }

  // ---------- navigation ----------
  var ICON = {
    today: '<svg viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="17" rx="3"/><path d="M3 9h18M8 2v4M16 2v4"/></svg>',
    bills: '<svg viewBox="0 0 24 24"><path d="M6 2h12v20l-3-2-3 2-3-2-3 2z"/><path d="M9 8h6M9 12h6"/></svg>',
    income: '<svg viewBox="0 0 24 24"><path d="M12 20V4M5 11l7-7 7 7"/></svg>',
    debts: '<svg viewBox="0 0 24 24"><rect x="2" y="5" width="20" height="14" rx="3"/><path d="M2 10h20M6 15h4"/></svg>',
    plan: '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>',
    accounts: '<svg viewBox="0 0 24 24"><path d="M3 10l9-6 9 6"/><path d="M5 10v9M19 10v9M9 10v9M15 10v9M3 19h18"/></svg>',
    spend: '<svg viewBox="0 0 24 24"><path d="M4 19V9M10 19V5M16 19v-7M22 19H2"/></svg>'
  };
  var TABS = [['today', 'Today'], ['bills', 'Bills'], ['spend', 'Spend'], ['income', 'Income'], ['debts', 'Debts'], ['plan', 'Plan'], ['accounts', 'Accounts']];
  function buildNav() {
    var nav = clear($('#nav')), side = clear($('#side-nav'));
    TABS.forEach(function (t) {
      nav.appendChild(el('button', { class: S.tab === t[0] ? 'on' : '', onclick: function () { go(t[0]); }, html: ICON[t[0]] + '<span>' + t[1] + '</span>' }));
      side.appendChild(el('button', { class: 'navlink' + (S.tab === t[0] ? ' on' : ''), onclick: function () { go(t[0]); }, html: ICON[t[0]] + '<span>' + t[1] + '</span>' }));
    });
  }
  function go(tab) { S.tab = tab; render(); window.scrollTo(0, 0); }

  // ---------- render ----------
  function render() {
    buildNav();
    var v = clear($('#view')), t = L.today(), d = L.parse(t);
    $('#today-date').textContent = DOW[d.getDay()] + ', ' + MONTHS[d.getMonth()] + ' ' + d.getDate();
    $('#title').textContent = TABS.find(function (x) { return x[0] === S.tab; })[1];
    var fab = $('#fab'); fab.hidden = false; fab.onclick = null;
    if (S.tab === 'today') { fab.hidden = true; renderToday(v); }
    else if (S.tab === 'bills') { fab.onclick = function () { billForm(); }; renderBills(v); }
    else if (S.tab === 'income') { fab.onclick = function () { incomeForm(); }; renderIncome(v); }
    else if (S.tab === 'debts') { fab.onclick = function () { debtForm(); }; renderDebts(v); }
    else if (S.tab === 'spend') { fab.onclick = function () { spendForm(); }; renderSpend(v); }
    else if (S.tab === 'plan') { fab.onclick = planMenu; renderPlan(v); }
    else if (S.tab === 'accounts') { fab.onclick = function () { accountForm(); }; renderAccounts(v); }
  }

  function stat(label, value, sub, cls, side) {
    return el('div', { class: 'stat' + (side ? ' ' + side : '') }, el('div', { class: 'l' }, label), el('div', { class: 'v ' + (cls || '') }, value), sub ? el('div', { class: 's' }, sub) : null);
  }
  function card(title, body, right) {
    var c = el('div', { class: 'card' + (title === null ? ' tight' : '') });
    if (title) c.appendChild(el('div', { class: 'card-h' }, el('h3', null, title), right || null));
    append(c, body); return c;
  }
  function listCard(title, rows, emptyMsg, right) {
    var c = el('div', { class: 'card tight' });
    if (title) c.appendChild(el('div', { class: 'card-h', style: 'padding:12px 16px 0' }, el('h3', null, title), right || null));
    if (!rows.length) c.appendChild(el('div', { class: 'empty' }, emptyMsg)); else append(c, rows);
    return c;
  }
  // which side of the house a bill belongs to: the account it pays from decides, else the category
  function billSide(b) {
    var a = b.pay_from_account_id && acct(b.pay_from_account_id);
    if (a) return a.is_business ? 'biz' : 'per';
    return b.category === 'Business' ? 'biz' : 'per';
  }
  function row(o) {
    return el('div', { class: 'row' + (o.side ? ' ' + o.side : ''), onclick: o.onclick },
      el('div', { class: 'ic', style: o.icStyle || '' }, o.ic || initial(o.title)),
      el('div', { class: 'body' }, el('div', { class: 't' }, o.title), el('div', { class: 'sub' }, o.sub)),
      el('div', { class: 'amt ' + (o.amtClass || '') }, o.amt, o.amtSub ? el('div', { class: 'sub' }, o.amtSub) : null));
  }

  // ---------- MONEY IN FLIGHT ----------
  // one word, so the expected date survives on a phone instead of being ellipsed away
  function shortAcct(a) { return a ? a.name.replace(/\s*\(.*\)/, '').replace(/\s*checking$/i, '') : 'account'; }
  function pendingRow(p) {
    var into = acct(p.to_account_id), from = acct(p.from_account_id), incoming = !!into;
    var where = incoming ? 'into ' + shortAcct(into) : 'out of ' + shortAcct(from);
    var when = !p.expects_on ? 'No date set'
      : p.expects_on < L.today() ? 'Due ' + fdate(p.expects_on) + ', still not in'
      : fdate(p.expects_on, true);
    return row({
      title: p.description, sub: when + ' · ' + where,
      amt: (incoming ? '+' : '-') + fmt(p.amount_cents), amtClass: incoming ? 'pos' : 'neg',
      side: (into || from) ? ((into || from).is_business ? 'biz' : 'per') : '',
      ic: incoming ? '↓' : '↑',
      onclick: function () { pendingDetail(p); }
    });
  }
  function pendingDetail(p) {
    formSheet(p.description, [
      { k: 'cleared_on', label: 'Cleared on', type: 'date', v: L.today(), req: true, half: true },
      { k: 'amount_cents', label: 'Amount that actually moved', type: 'money', v: p.amount_cents, req: true, half: true }
    ], function (d) { return clearPending(p, d.cleared_on, d.amount_cents); },
       function () { return q(sb.from('fin_pending').delete().eq('id', p.id)).then(function () { toast('Removed'); }); },
       'Mark cleared');
  }
  // clearing is what moves the real balances, so a pending row is never counted twice
  function clearPending(p, on, cents) {
    var into = acct(p.to_account_id), from = acct(p.from_account_id);
    var first = p.bill_id
      // a bill payment goes through the same path as paying from the Bills tab, so it
      // lands in payment history and rolls the due date forward
      ? rpc('fin_pay_bill', { p_bill: p.bill_id, p_amount_cents: cents, p_paid_on: on,
          p_account: p.source_debited ? null : p.from_account_id, p_debt: null,
          p_note: p.description })
      : Promise.resolve();
    return first.then(function () {
      var jobs = [q(sb.from('fin_pending').update({ cleared_on: on, amount_cents: cents }).eq('id', p.id))];
      if (into) jobs.push(q(sb.from('fin_accounts').update({ balance_cents: into.balance_cents + cents }).eq('id', into.id)));
      // fin_pay_bill already moved the money for a linked bill; only adjust here otherwise
      if (!p.bill_id && from && !p.source_debited) jobs.push(q(sb.from('fin_accounts').update({ balance_cents: from.balance_cents - cents }).eq('id', from.id)));
      return Promise.all(jobs);
    }).then(function () { toast('Cleared. Balances updated.'); });
  }
  function pendingForm() {
    var accts = [['', 'Not set']].concat(cashAccounts().map(function (a) { return [a.id, a.name]; }));
    formSheet('Money in flight', [
      { k: 'description', label: 'What is it', type: 'text', v: '', req: true, ph: 'Transfer to M&T, mortgage payment' },
      { k: 'amount_cents', label: 'Amount', type: 'money', v: 0, req: true, half: true },
      { k: 'expects_on', label: 'Expected by', type: 'date', v: L.addDays(L.today(), 1), req: true, half: true },
      { k: 'kind', label: 'Type', type: 'select', v: 'transfer', opts: [['transfer', 'Transfer between accounts'], ['payment', 'Payment going out'], ['deposit', 'Deposit coming in']], half: true },
      { k: 'from_account_id', label: 'Out of', type: 'select', v: '', opts: accts, half: true },
      { k: 'to_account_id', label: 'Into', type: 'select', v: '', opts: accts, half: true },
      { k: 'bill_id', label: 'Paying a bill (optional)', type: 'select', v: '', opts: [['', 'No']].concat(S.bills.map(function (b) { return [b.id, b.name]; })) },
      { k: 'source_debited', label: 'Already gone from the sending account', type: 'check', v: true },
      { k: 'note', label: 'Note', type: 'textarea', v: '' }
    ], function (d) {
      d.from_account_id = d.from_account_id || null;
      d.to_account_id = d.to_account_id || null;
      d.bill_id = d.bill_id || null;
      d.initiated_on = L.today();
      return q(sb.from('fin_pending').insert(d)).then(function () { toast('Tracking it'); });
    });
  }

  // ---------- TODAY ----------
  function renderToday(v) {
    // plan and forecast run on available cash, not bank balances: a transfer still in
    // transit is spendable, a payment that has not cleared yet is not.
    var t = L.today(), cash = L.liquidCash(S.accounts) + pendingNetAll(), reserve = reserveCents();
    var open = billsNotInFlight();
    var plan = L.payPlan({ today: t, cash: cash, bills: open, income: S.income, days: 30, reserve: reserve });
    var fc = L.forecast({ today: t, cash: cash - reserve, bills: open, income: S.income, days: 45, includeLikely: !!S.prefs.includeLikely });
    var due14 = L.billOccurrences(open, t, L.addDays(t, 14)).reduce(function (s, o) { return s + o.bill.amount_cents; }, 0);
    var confirmed30 = 0, likely30 = 0;
    S.income.forEach(function (i) { if (i.received_on || i.expected_date > L.addDays(t, 30)) return; if (i.confidence === 'confirmed') confirmed30 += i.amount_cents; else if (i.confidence === 'likely') likely30 += i.amount_cents; });
    var overdue = plan.plan.filter(function (p) { return p.status === 'overdue'; });

    if (!S.accounts.length && !S.bills.length) {
      v.appendChild(el('div', { class: 'notice' }, el('b', null, 'Start here'), 'Add your accounts with current balances, then your bills and expected income. The plan builds itself from there.'));
      v.appendChild(el('div', { class: 'btnrow' }, el('button', { class: 'btn primary', onclick: function () { accountForm(); } }, 'Add account'), el('button', { class: 'btn', onclick: function () { billForm(); } }, 'Add bill'), el('button', { class: 'btn', onclick: function () { incomeForm(); } }, 'Add income')));
    }

    function sideCash(biz) {
      var ids = cashAccounts().filter(function (a) { return !!a.is_business === biz; }).map(function (a) { return a.id; });
      var o = { bank: 0, in: 0, out: 0 };
      cashAccounts().forEach(function (a) { if (ids.indexOf(a.id) >= 0) o.bank += a.balance_cents; });
      S.pending.forEach(function (p) {
        if (ids.indexOf(p.to_account_id) >= 0) o.in += p.amount_cents;
        if (ids.indexOf(p.from_account_id) >= 0 && !p.source_debited) o.out += p.amount_cents;
      });
      return o;
    }
    // headline is what he can actually spend; the gross movements go underneath, not the
    // net, because "+$58 in flight" hides a $2,508 arrival and a $2,450 departure
    function cashSub(c, fallback) {
      var parts = [];
      if (c.in) parts.push('+' + fmt(c.in, { whole: true }) + ' landing');
      if (c.out) parts.push('-' + fmt(c.out, { whole: true }) + ' leaving');
      return parts.length ? fmt(c.bank, { whole: true }) + ' at the bank · ' + parts.join(' · ') : fallback;
    }
    var per = sideCash(false), biz = sideCash(true);
    var perCash = per.bank + per.in - per.out, bizCash = biz.bank + biz.in - biz.out;
    v.appendChild(el('div', { class: 'hero five' },
      stat('Personal cash', fmt(perCash, { whole: true }), cashSub(per, reserve ? fmt(reserve, { whole: true }) + ' buffer held back' : 'joint checking'), perCash < 0 ? 'neg' : '', 'per'),
      stat('Business cash', fmt(bizCash, { whole: true }), cashSub(biz, 'business checking'), bizCash < 0 ? 'neg' : '', 'biz'),
      stat('Due next 14 days', fmt(due14, { whole: true }), overdue.length ? overdue.length + ' overdue' : 'nothing overdue', overdue.length ? 'neg' : ''),
      stat('Income, next 30 days', fmt(confirmed30, { whole: true }), likely30 ? '+ ' + fmt(likely30, { whole: true }) + ' likely' : 'confirmed only', 'pos'),
      stat('Lowest point', fmt(fc.minBalance, { whole: true }), fc.minBalance < 0 ? 'goes negative ' + fdate(fc.firstNegative) : 'on ' + fdate(fc.minDate), fc.minBalance < 0 ? 'neg' : fc.minBalance < 50000 ? 'warn' : 'pos')));

    // money in motion
    if (S.pending.length) {
      v.appendChild(listCard('In flight', S.pending.map(pendingRow), '',
        el('button', { class: 'pill', onclick: function () { pendingForm(); } }, '+ Add')));
    }

    // pay plan
    var items = plan.plan.map(function (p) {
      var o = p.occ, b = o.bill, sub, pill;
      if (p.status === 'overdue') { sub = Math.abs(L.diffDays(t, o.due)) + ' days late. Pay now.'; pill = ['red', 'Overdue']; }
      else if (p.status === 'now') { sub = 'Due ' + relDue(o.due) + '. Cash covers it.'; pill = ['amber', 'Pay now']; }
      else if (p.status === 'scheduled') { sub = 'Due ' + fdate(o.due, true) + (b.autopay ? '. Autopay.' : '. Covered.'); pill = ['green', b.autopay ? 'Autopay' : 'Covered']; }
      else if (p.status === 'wait') { sub = 'Due ' + fdate(o.due) + '. Pay ' + fdate(p.payOn) + (p.waitFor && p.waitFor.length ? ' after ' + p.waitFor.join(', ') : '') + (p.late ? ' (late)' : ''); pill = [p.late ? 'yellow' : 'blue', p.late ? 'Wait, late' : 'Wait']; }
      else if (o.overdue) { sub = Math.abs(L.diffDays(t, o.due)) + ' days late. Need ' + fmt(p.shortBy) + ' to clear it.'; pill = ['red', 'Past due']; }
      else { sub = 'Due ' + fdate(o.due) + '. Short by ' + fmt(p.shortBy) + '.'; pill = ['red', 'Short']; }
      var when = L.parse(p.payOn || o.effective);
      return el('div', { class: 'plan-item ' + billSide(b), onclick: function () { billDetail(b); } },
        el('div', { class: 'when' }, el('b', null, when.getDate()), el('span', null, MONTHS[when.getMonth()])),
        el('div', { class: 'body' }, el('div', { class: 't' }, b.name, !b.essential ? el('span', { class: 'dim small' }, '  · flexible') : null), el('div', { class: 'sub' }, sub)),
        el('div', { class: 'amt' }, fmt(b.amount_cents), el('div', null, el('span', { class: 'pill ' + pill[0] }, pill[1]))));
    });
    v.appendChild(listCard('Pay plan, next 30 days', items, 'No bills in the next 30 days.'));

    // forecast
    var fcCard = card('Cash forecast, 45 days', [chart(fc), el('div', { class: 'chart-legend' }, el('span', null, fdate(fc.from)), el('span', null, 'ends ' + fmt(fc.end, { whole: true })), el('span', null, fdate(fc.to)))],
      el('button', { class: 'pill ' + (S.prefs.includeLikely ? 'blue' : ''), onclick: function () { S.prefs.includeLikely = !S.prefs.includeLikely; savePrefs(); render(); } }, S.prefs.includeLikely ? 'incl. likely income' : 'confirmed only'));
    v.appendChild(fcCard);

    // upcoming income
    var inc = S.income.filter(function (i) { return !i.received_on; }).slice(0, 5).map(incomeRow);
    v.appendChild(listCard('Expected income', inc, 'No expected income logged. Add invoices and projected payments.', el('button', { class: 'pill', onclick: function () { go('income'); } }, 'All')));

    // budgets snapshot
    if (S.budgets.length) {
      var usage = L.budgetUsage(S.budgets, S.spend, t), ess = usage.filter(function (u) { return u.budget.kind === 'essential'; }), non = usage.filter(function (u) { return u.budget.kind !== 'essential'; });
      function sum(arr, k) { return arr.reduce(function (s, u) { return s + (k === 'cap' ? u.budget.monthly_cap_cents : u.used); }, 0); }
      v.appendChild(card('Spending this month', [budgetLine('Essentials', sum(ess, 'used'), sum(ess, 'cap')), budgetLine('Non-essentials', sum(non, 'used'), sum(non, 'cap'))],
        el('button', { class: 'pill', onclick: function () { spendForm(); } }, '+ Log spend')));
    }
  }
  function budgetLine(label, used, cap) {
    var p = cap ? Math.min(1, used / cap) : 0, over = used > cap;
    return el('div', { style: 'margin-bottom:12px' }, el('div', { style: 'display:flex;justify-content:space-between' }, el('span', null, label), el('span', { class: over ? 'neg' : 'muted' }, fmt(used, { whole: true }) + ' / ' + fmt(cap, { whole: true }))),
      el('div', { class: 'bar' }, el('i', { class: over ? 'over' : '', style: 'width:' + pct(p) })));
  }
  function chart(fc) {
    var W = 600, H = 120, pad = 6, tl = fc.timeline, n = tl.length;
    var vals = tl.map(function (d) { return d.balance; }).concat([0, fc.start]);
    var mn = Math.min.apply(null, vals), mx = Math.max.apply(null, vals); if (mx === mn) mx = mn + 1;
    function x(i) { return pad + (i / (n - 1)) * (W - pad * 2); }
    function y(vv) { return pad + (1 - (vv - mn) / (mx - mn)) * (H - pad * 2); }
    var pts = tl.map(function (d, i) { return x(i).toFixed(1) + ',' + y(d.balance).toFixed(1); }).join(' ');
    var area = 'M' + x(0) + ',' + y(0) + ' L' + pts.replace(/ /g, ' L') + ' L' + x(n - 1) + ',' + y(0) + ' Z';
    var minI = tl.findIndex(function (d) { return d.date === fc.minDate; });
    var svg = '<svg class="chart" viewBox="0 0 ' + W + ' ' + H + '" preserveAspectRatio="none">' +
      '<defs><linearGradient id="g" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#e9a23b" stop-opacity=".35"/><stop offset="1" stop-color="#e9a23b" stop-opacity="0"/></linearGradient></defs>' +
      '<path d="' + area + '" fill="url(#g)"/>' +
      '<line x1="0" x2="' + W + '" y1="' + y(0) + '" y2="' + y(0) + '" stroke="#f0605d" stroke-dasharray="4 4" stroke-width="1" opacity=".7"/>' +
      '<polyline points="' + pts + '" fill="none" stroke="#e9a23b" stroke-width="2" vector-effect="non-scaling-stroke"/>' +
      (minI >= 0 ? '<circle cx="' + x(minI) + '" cy="' + y(fc.minBalance) + '" r="4" fill="' + (fc.minBalance < 0 ? '#f0605d' : '#e6c351') + '"/>' : '') + '</svg>';
    return el('div', { html: svg });
  }

  // ---------- BILLS ----------
  function renderBills(v) {
    var seg = el('div', { class: 'seg', style: 'margin-bottom:12px' },
      el('button', { class: S.sub.bills === 'upcoming' ? 'on' : '', onclick: function () { S.sub.bills = 'upcoming'; render(); } }, 'Upcoming'),
      el('button', { class: S.sub.bills === 'paid' ? 'on' : '', onclick: function () { S.sub.bills = 'paid'; render(); } }, 'Paid'));
    v.appendChild(seg);
    var t = L.today();
    if (S.sub.bills === 'upcoming') {
      var monthly = S.bills.reduce(function (s, b) { var m = { weekly: 4.33, biweekly: 2.17, monthly: 1, quarterly: 1 / 3, annual: 1 / 12, once: 0 }[b.frequency] || 0; return s + b.amount_cents * m; }, 0);
      v.appendChild(el('div', { class: 'hero' }, stat('Monthly bill load', fmt(monthly, { whole: true }), S.bills.length + ' active bills'),
        stat('Essentials', fmt(S.bills.filter(function (b) { return b.essential; }).reduce(function (s, b) { return s + (b.frequency === 'monthly' ? b.amount_cents : 0); }, 0), { whole: true }), 'monthly essentials')));
      var groups = [['Overdue', function (b) { return b.next_due_date < t; }], ['This week', function (b) { return b.next_due_date >= t && b.next_due_date <= L.addDays(t, 7); }],
        ['Next 30 days', function (b) { return b.next_due_date > L.addDays(t, 7) && b.next_due_date <= L.addDays(t, 30); }], ['Later', function (b) { return b.next_due_date > L.addDays(t, 30); }]];
      var any = false;
      groups.forEach(function (g) {
        var bs = S.bills.filter(g[1]); if (!bs.length) return; any = true;
        v.appendChild(listCard(g[0], bs.map(billRow), ''));
      });
      if (!any) v.appendChild(listCard(null, [], 'No bills yet. Tap + to add one.'));
    } else {
      var rows = S.payments.map(function (p) {
        var b = bill(p.bill_id), name = b ? b.name : 'Bill';
        return row({ title: name, sub: 'Paid ' + fdate(p.paid_on) + ' for ' + fdate(p.due_date) + (p.from_account_id && acct(p.from_account_id) ? ' from ' + acct(p.from_account_id).name : p.from_debt_id && debt(p.from_debt_id) ? ' on ' + debt(p.from_debt_id).name : ''), amt: fmt(p.amount_cents), amtClass: 'muted',
          onclick: function () { confirmSheet('Undo this payment?', name + ' ' + fmt(p.amount_cents) + ' paid ' + fdate(p.paid_on) + '. The bill goes back to due and balances are restored.', 'Undo payment', function () { return rpc('fin_unpay_bill', { p_payment: p.id }).then(function () { toast('Payment undone'); }); }); } });
      });
      v.appendChild(listCard('Last 90 days', rows, 'No payments recorded yet.'));
    }
  }
  function billRow(b) {
    var late = b.next_due_date < L.today();
    return row({ title: b.name, sub: (late ? 'Late. Was due ' : 'Due ') + fdate(b.next_due_date, true) + ' · ' + b.frequency + (b.autopay ? ' · autopay' : '') + (b.essential ? '' : ' · flexible'),
      amt: fmt(b.amount_cents), amtClass: late ? 'neg' : '', icStyle: late ? 'color:var(--red);background:rgba(240,96,93,.14)' : '', side: billSide(b), onclick: function () { billDetail(b); } });
  }
  function billDetail(b) {
    var hist = S.payments.filter(function (p) { return p.bill_id === b.id; }).slice(0, 6);
    var linked = b.debt_id && debt(b.debt_id);
    openSheet(b.name, [
      el('div', { class: 'kv' }, el('span', null, 'Amount'), el('span', null, fmt(b.amount_cents))),
      el('div', { class: 'kv' }, el('span', null, 'Next due'), el('span', { class: b.next_due_date < L.today() ? 'neg' : '' }, fdate(b.next_due_date, true) + ' · ' + relDue(b.next_due_date))),
      el('div', { class: 'kv' }, el('span', null, 'Frequency'), el('span', null, b.frequency + (b.autopay ? ' · autopay' : ''))),
      el('div', { class: 'kv' }, el('span', null, 'Priority'), el('span', null, b.essential ? 'Essential' : 'Flexible')),
      b.category ? el('div', { class: 'kv' }, el('span', null, 'Category'), el('span', null, b.category)) : null,
      b.pay_from_account_id && acct(b.pay_from_account_id) ? el('div', { class: 'kv' }, el('span', null, 'Pays from'), el('span', null, acct(b.pay_from_account_id).name)) : null,
      linked ? el('div', { class: 'kv' }, el('span', null, 'Reduces debt'), el('span', null, linked.name)) : null,
      b.notes ? el('div', { class: 'kv' }, el('span', null, 'Notes'), el('span', { style: 'text-align:right;max-width:70%' }, b.notes)) : null,
      el('div', { class: 'actions', style: 'margin-top:14px' }, el('button', { class: 'btn primary', onclick: function () { payForm(b); } }, 'Mark paid'), el('button', { class: 'btn', onclick: function () { billForm(b); } }, 'Edit')),
      el('div', { class: 'actions' }, el('button', { class: 'btn', onclick: function () { skipBill(b); } }, b.frequency === 'once' ? 'Remove' : 'Skip this one')),
      hist.length ? el('div', { class: 'hist' }, el('div', { class: 'tiny muted', style: 'margin-bottom:4px' }, 'Recent payments'), hist.map(function (p) { return el('div', { class: 'kv' }, el('span', null, 'Paid ' + fdate(p.paid_on) + ' for ' + fdate(p.due_date)), el('span', null, fmt(p.amount_cents))); })) : null
    ]);
  }
  function skipBill(b) {
    if (b.frequency === 'once') return confirmSheet('Remove ' + b.name + '?', 'The bill is archived. Past payments stay in history.', 'Remove', function () { return q(sb.from('fin_bills').update({ active: false }).eq('id', b.id)).then(function () { toast('Removed'); }); });
    confirmSheet('Skip ' + b.name + ' for ' + fdate(b.next_due_date) + '?', 'Moves the next due date forward one cycle without recording a payment.', 'Skip', function () {
      return q(sb.from('fin_bills').update({ next_due_date: L.nextDue(b.next_due_date, b.frequency) }).eq('id', b.id)).then(function () { toast('Skipped'); });
    });
  }
  var CATEGORIES = ['Housing', 'Utilities', 'Insurance', 'Vehicle', 'Phone & Internet', 'Subscriptions', 'Debt payment', 'Business', 'Family', 'Taxes', 'Other'];
  function billForm(b) {
    var isNew = !b; b = b || {};
    formSheet(isNew ? 'New bill' : 'Edit bill', [
      { k: 'name', label: 'Name', type: 'text', v: b.name, req: true, ph: 'Electric, Rent, Amex minimum' },
      { k: 'amount_cents', label: 'Amount', type: 'money', v: b.amount_cents, req: true, half: true },
      { k: 'next_due_date', label: 'Next due', type: 'date', v: b.next_due_date || L.today(), req: true, half: true },
      { k: 'frequency', label: 'Repeats', type: 'select', v: b.frequency || 'monthly', opts: [['monthly', 'Monthly'], ['weekly', 'Weekly'], ['biweekly', 'Every 2 weeks'], ['quarterly', 'Quarterly'], ['annual', 'Yearly'], ['once', 'One time']], half: true },
      { k: 'category', label: 'Category', type: 'select', v: b.category || 'Other', opts: CATEGORIES.map(function (c) { return [c, c]; }), half: true },
      { k: 'pay_from_account_id', label: 'Pays from (optional)', type: 'select', v: b.pay_from_account_id || '', opts: [['', 'Not set']].concat(cashAccounts().map(function (a) { return [a.id, a.name]; })), half: true },
      { k: 'debt_id', label: 'Reduces a debt (optional)', type: 'select', v: b.debt_id || '', opts: [['', 'No']].concat(S.debts.map(function (d) { return [d.id, d.name]; })), half: true },
      { k: 'essential', label: 'Essential (late fee, shutoff, credit hit, or family needs it)', type: 'check', v: b.essential !== false },
      { k: 'autopay', label: 'On autopay', type: 'check', v: !!b.autopay },
      { k: 'notes', label: 'Notes', type: 'textarea', v: b.notes }
    ], function (data) {
      data.pay_from_account_id = data.pay_from_account_id || null; data.debt_id = data.debt_id || null;
      var p = isNew ? q(sb.from('fin_bills').insert(data)) : q(sb.from('fin_bills').update(data).eq('id', b.id));
      return p.then(function () { toast(isNew ? 'Bill added' : 'Saved'); });
    }, isNew ? null : function () { return skipBill(b); });
  }
  function payForm(b) {
    formSheet('Pay ' + b.name, [
      { k: 'amount', label: 'Amount', type: 'money', v: b.amount_cents, req: true, half: true },
      { k: 'paid_on', label: 'Paid on', type: 'date', v: L.today(), req: true, half: true },
      { k: 'from', label: 'Paid with', type: 'select', v: b.pay_from_account_id ? 'a:' + b.pay_from_account_id : '', opts: payWithOptions() },
      { k: 'note', label: 'Note', type: 'text', v: '' }
    ], function (d) {
      var src = splitSource(d.from);
      return rpc('fin_pay_bill', { p_bill: b.id, p_amount_cents: d.amount, p_paid_on: d.paid_on, p_account: src.account, p_debt: src.debt, p_note: d.note || null }).then(function () { toast(b.name + ' paid'); });
    }, null, 'Mark paid');
  }
  function payWithOptions() {
    return [['', 'Not tracked (no balance change)']].concat(cashAccounts().map(function (a) { return ['a:' + a.id, a.name + ' (' + fmt(a.balance_cents, { whole: true }) + ')']; }))
      .concat(cards().map(function (d) { return ['d:' + d.id, d.name + ' (card)']; }));
  }
  function splitSource(v) { if (!v) return { account: null, debt: null }; return v.charAt(0) === 'a' ? { account: v.slice(2), debt: null } : { account: null, debt: v.slice(2) }; }

  // ---------- INCOME ----------
  function renderIncome(v) {
    v.appendChild(el('div', { class: 'seg', style: 'margin-bottom:12px' },
      el('button', { class: S.sub.income === 'expected' ? 'on' : '', onclick: function () { S.sub.income = 'expected'; render(); } }, 'Expected'),
      el('button', { class: S.sub.income === 'received' ? 'on' : '', onclick: function () { S.sub.income = 'received'; render(); } }, 'Received')));
    var t = L.today();
    if (S.sub.income === 'expected') {
      var pend = S.income.filter(function (i) { return !i.received_on; });
      var sums = { confirmed: 0, likely: 0, maybe: 0 }; pend.forEach(function (i) { sums[i.confidence] += i.amount_cents; });
      v.appendChild(el('div', { class: 'hero' }, stat('Confirmed', fmt(sums.confirmed, { whole: true }), 'counts in the plan', 'pos'), stat('Likely', fmt(sums.likely, { whole: true }), 'forecast toggle only'), stat('Maybe', fmt(sums.maybe, { whole: true }), 'never counted')));
      var late = pend.filter(function (i) { return i.expected_date < t; }), soon = pend.filter(function (i) { return i.expected_date >= t; });
      if (late.length) v.appendChild(listCard('Past expected date', late.map(incomeRow), ''));
      v.appendChild(listCard('Upcoming', soon.map(incomeRow), 'Nothing expected. Add invoices sent, retainers, projected client payments.'));
    } else {
      var rec = S.income.filter(function (i) { return i.received_on; }).sort(function (a, b) { return a.received_on < b.received_on ? 1 : -1; });
      var thisMonth = rec.filter(function (i) { return i.received_on >= L.monthStart(t); }).reduce(function (s, i) { return s + (i.received_cents || i.amount_cents); }, 0);
      v.appendChild(el('div', { class: 'hero' }, stat('Received this month', fmt(thisMonth, { whole: true }), '', 'pos')));
      v.appendChild(listCard('Received', rec.map(incomeRow), 'Nothing received yet.'));
    }
  }
  function incomeRow(i) {
    var pillCls = { confirmed: 'green', likely: 'blue', maybe: '' }[i.confidence];
    var sub = i.received_on ? 'Received ' + fdate(i.received_on) + (i.deposit_account_id && acct(i.deposit_account_id) ? ' into ' + acct(i.deposit_account_id).name : '') : 'Expected ' + fdate(i.expected_date, true) + (i.expected_date < L.today() ? ' (past)' : '');
    return el('div', { class: 'row', onclick: function () { incomeDetail(i); } },
      el('div', { class: 'ic', style: 'color:var(--green);background:rgba(76,195,138,.12)' }, initial(i.source)),
      el('div', { class: 'body' }, el('div', { class: 't' }, i.source), el('div', { class: 'sub' }, sub)),
      el('div', { class: 'amt pos' }, fmt(i.received_cents || i.amount_cents), !i.received_on ? el('div', null, el('span', { class: 'pill ' + pillCls }, i.confidence)) : null));
  }
  function incomeDetail(i) {
    openSheet(i.source, [
      el('div', { class: 'kv' }, el('span', null, 'Amount'), el('span', null, fmt(i.amount_cents))),
      el('div', { class: 'kv' }, el('span', null, 'Expected'), el('span', null, fdate(i.expected_date, true))),
      el('div', { class: 'kv' }, el('span', null, 'Confidence'), el('span', null, i.confidence)),
      i.received_on ? el('div', { class: 'kv' }, el('span', null, 'Received'), el('span', { class: 'pos' }, fmt(i.received_cents) + ' on ' + fdate(i.received_on))) : null,
      i.notes ? el('div', { class: 'kv' }, el('span', null, 'Notes'), el('span', { style: 'text-align:right;max-width:70%' }, i.notes)) : null,
      el('div', { class: 'actions', style: 'margin-top:14px' },
        i.received_on ? el('button', { class: 'btn', onclick: function () { confirmSheet('Undo received?', 'Removes the deposit from the account balance.', 'Undo', function () { return rpc('fin_unreceive_income', { p_income: i.id }).then(function () { toast('Undone'); }); }); } }, 'Undo received')
          : el('button', { class: 'btn primary', onclick: function () { receiveForm(i); } }, 'Mark received'),
        el('button', { class: 'btn', onclick: function () { incomeForm(i); } }, 'Edit'))
    ]);
  }
  function incomeForm(i) {
    var isNew = !i; i = i || {};
    formSheet(isNew ? 'Expected income' : 'Edit income', [
      { k: 'source', label: 'Source', type: 'text', v: i.source, req: true, ph: 'Niam Sports invoice #12, OOB paddle sales' },
      { k: 'amount_cents', label: 'Amount', type: 'money', v: i.amount_cents, req: true, half: true },
      { k: 'expected_date', label: 'Expected on', type: 'date', v: i.expected_date || L.today(), req: true, half: true },
      { k: 'confidence', label: 'Confidence', type: 'select', v: i.confidence || 'likely', opts: [['confirmed', 'Confirmed (invoice approved, date known)'], ['likely', 'Likely (verbal yes, in progress)'], ['maybe', 'Maybe (proposal out, pipeline)']] },
      { k: 'deposit_account_id', label: 'Deposits to', type: 'select', v: i.deposit_account_id || '', opts: [['', 'Not set']].concat(cashAccounts().map(function (a) { return [a.id, a.name]; })) },
      { k: 'notes', label: 'Notes', type: 'textarea', v: i.notes }
    ], function (d) {
      d.deposit_account_id = d.deposit_account_id || null;
      var p = isNew ? q(sb.from('fin_income').insert(d)) : q(sb.from('fin_income').update(d).eq('id', i.id));
      return p.then(function () { toast(isNew ? 'Income added' : 'Saved'); });
    }, isNew ? null : function () { return confirmSheet('Delete ' + i.source + '?', 'Removes it from the plan.', 'Delete', function () { return q(sb.from('fin_income').delete().eq('id', i.id)).then(function () { toast('Deleted'); }); }); });
  }
  function receiveForm(i) {
    formSheet('Received: ' + i.source, [
      { k: 'amount', label: 'Amount received', type: 'money', v: i.amount_cents, req: true, half: true },
      { k: 'on', label: 'Received on', type: 'date', v: L.today(), req: true, half: true },
      { k: 'account', label: 'Deposited to', type: 'select', v: i.deposit_account_id || '', opts: [['', 'Not tracked (no balance change)']].concat(cashAccounts().map(function (a) { return [a.id, a.name]; })) }
    ], function (d) {
      return rpc('fin_receive_income', { p_income: i.id, p_amount_cents: d.amount, p_received_on: d.on, p_account: d.account || null }).then(function () { toast('Received ' + fmt(d.amount)); });
    }, null, 'Mark received');
  }

  // ---------- DEBTS ----------
  function renderDebts(v) {
    var total = S.debts.reduce(function (s, d) { return s + d.balance_cents; }, 0), mins = S.debts.reduce(function (s, d) { return s + d.min_payment_cents; }, 0);
    var paid30 = S.debtPayments.filter(function (p) { return p.paid_on >= L.addDays(L.today(), -30); }).reduce(function (s, p) { return s + p.amount_cents; }, 0);
    v.appendChild(el('div', { class: 'hero' }, stat('Total owed', fmt(total, { whole: true }), S.debts.length + ' debts', total ? 'neg' : ''), stat('Minimums / month', fmt(mins, { whole: true }), ''), stat('Paid last 30 days', fmt(paid30, { whole: true }), '', 'pos')));
    var groups = [['Taxes', 'tax'], ['Credit cards', 'credit_card'], ['Loans', 'loan'], ['Other', 'other']];
    var any = false;
    groups.forEach(function (g) {
      var ds = S.debts.filter(function (d) { return d.kind === g[1]; }); if (!ds.length) return; any = true;
      v.appendChild(listCard(g[0], ds.map(debtRow), ''));
    });
    if (!any) v.appendChild(listCard(null, [], 'No debts logged. Add taxes owed, cards, loans.'));
  }
  function debtRow(d) {
    var months = L.payoffMonths(d.balance_cents, d.apr, d.min_payment_cents);
    var sub = (d.min_payment_cents ? 'min ' + fmt(d.min_payment_cents, { whole: true }) : 'no minimum set') + (d.apr ? ' · ' + d.apr + '% APR' : '') + (d.min_payment_cents ? ' · ' + (months === Infinity ? 'never at minimum' : '~' + months + ' mo at minimum') : '');
    return row({ title: d.name, sub: sub, amt: fmt(d.balance_cents), amtClass: 'neg', onclick: function () { debtDetail(d); } });
  }
  function debtDetail(d) {
    var hist = S.debtPayments.filter(function (p) { return p.debt_id === d.id; }).slice(0, 6);
    var linkedBills = S.bills.filter(function (b) { return b.debt_id === d.id; });
    openSheet(d.name, [
      el('div', { class: 'kv' }, el('span', null, 'Balance'), el('span', { class: 'neg' }, fmt(d.balance_cents))),
      el('div', { class: 'kv' }, el('span', null, 'Minimum'), el('span', null, fmt(d.min_payment_cents))),
      d.apr ? el('div', { class: 'kv' }, el('span', null, 'APR'), el('span', null, d.apr + '%')) : null,
      d.target_payoff_date ? el('div', { class: 'kv' }, el('span', null, 'Target payoff'), el('span', null, fdate(d.target_payoff_date) + ' · needs ' + fmt(Math.ceil(d.balance_cents / Math.max(1, Math.ceil(L.diffDays(L.today(), d.target_payoff_date) / 30))), { whole: true }) + '/mo')) : null,
      linkedBills.length ? el('div', { class: 'kv' }, el('span', null, 'Bill'), el('span', null, linkedBills.map(function (b) { return b.name + ' due ' + fdate(b.next_due_date); }).join(', '))) : el('div', { class: 'kv' }, el('span', null, 'Bill'), el('button', { class: 'pill amber', onclick: function () { billForm({ name: d.name + ' payment', amount_cents: d.min_payment_cents, debt_id: d.id, category: 'Debt payment', essential: true }); } }, '+ Add minimum as a bill')),
      d.notes ? el('div', { class: 'kv' }, el('span', null, 'Notes'), el('span', { style: 'text-align:right;max-width:70%' }, d.notes)) : null,
      el('div', { class: 'actions', style: 'margin-top:14px' }, el('button', { class: 'btn primary', onclick: function () { debtPayForm(d); } }, 'Record payment'), el('button', { class: 'btn', onclick: function () { debtForm(d); } }, 'Edit')),
      hist.length ? el('div', { class: 'hist' }, el('div', { class: 'tiny muted', style: 'margin-bottom:4px' }, 'Recent payments'), hist.map(function (p) { return el('div', { class: 'kv' }, el('span', null, fdate(p.paid_on) + (p.note ? ' · ' + p.note : '')), el('span', null, fmt(p.amount_cents))); })) : null
    ]);
  }
  function debtForm(d) {
    var isNew = !d; d = d || {};
    formSheet(isNew ? 'New debt' : 'Edit debt', [
      { k: 'name', label: 'Name', type: 'text', v: d.name, req: true, ph: 'IRS 2025, Amex, Truck loan' },
      { k: 'kind', label: 'Type', type: 'select', v: d.kind || 'credit_card', opts: [['credit_card', 'Credit card'], ['tax', 'Taxes owed'], ['loan', 'Loan'], ['other', 'Other']], half: true },
      { k: 'balance_cents', label: 'Balance owed', type: 'money', v: d.balance_cents, req: true, half: true },
      { k: 'min_payment_cents', label: 'Minimum payment', type: 'money', v: d.min_payment_cents, half: true },
      { k: 'apr', label: 'APR %', type: 'number', v: d.apr, half: true, step: '0.01' },
      { k: 'target_payoff_date', label: 'Target payoff (optional)', type: 'date', v: d.target_payoff_date || '', half: true },
      isNew ? { k: '_due', label: 'Minimum due next', type: 'date', v: L.today(), half: true } : null,
      isNew ? { k: '_bill', label: 'Add the minimum payment as a monthly bill', type: 'check', v: true } : null,
      { k: 'notes', label: 'Notes', type: 'textarea', v: d.notes }
    ].filter(Boolean), function (data) {
      var mkBill = data._bill, due = data._due; delete data._bill; delete data._due;
      data.apr = data.apr === '' || data.apr === null ? null : Number(data.apr); data.target_payoff_date = data.target_payoff_date || null;
      if (isNew) return q(sb.from('fin_debts').insert(data).select().single()).then(function (nd) {
        if (mkBill && data.min_payment_cents > 0) return q(sb.from('fin_bills').insert({ name: data.name + ' payment', amount_cents: data.min_payment_cents, frequency: 'monthly', next_due_date: due || L.today(), essential: true, category: 'Debt payment', debt_id: nd.id }));
      }).then(function () { toast('Debt added'); });
      return q(sb.from('fin_debts').update(data).eq('id', d.id)).then(function () { toast('Saved'); });
    }, isNew ? null : function () { return confirmSheet('Remove ' + d.name + '?', 'Archives the debt. Linked bills stay unless you remove them.', 'Remove', function () { return q(sb.from('fin_debts').update({ active: false }).eq('id', d.id)).then(function () { toast('Removed'); }); }); });
  }
  function debtPayForm(d) {
    formSheet('Pay toward ' + d.name, [
      { k: 'amount', label: 'Amount', type: 'money', v: d.min_payment_cents, req: true, half: true },
      { k: 'on', label: 'Paid on', type: 'date', v: L.today(), req: true, half: true },
      { k: 'account', label: 'Paid from', type: 'select', v: '', opts: [['', 'Not tracked (no balance change)']].concat(cashAccounts().map(function (a) { return [a.id, a.name]; })) },
      { k: 'note', label: 'Note', type: 'text', v: 'Extra payment' }
    ], function (x) {
      return rpc('fin_pay_debt', { p_debt: d.id, p_amount_cents: x.amount, p_paid_on: x.on, p_account: x.account || null, p_note: x.note || null }).then(function () { toast('Payment recorded'); });
    }, null, 'Record');
  }

  // ---------- PLAN (goals + budgets) ----------
  // ---------- SPEND ----------
  function renderSpend(v) {
    var t = L.today();
    var series = L.spendMonths(S.spend, t, 6).filter(function (m) { return m.count || m.month === L.monthStart(t); });
    var cur = series[series.length - 1] || { total: 0, count: 0 };
    var prev = series.length > 1 ? series[series.length - 2] : null;
    var caps = S.budgets.reduce(function (a, b) { return a + b.monthly_cap_cents; }, 0);
    var proj = L.projectMonth(cur.total, t);
    var done = series.filter(function (m) { return m.count && m.month !== L.monthStart(t); });
    var avg = done.length ? Math.round(done.reduce(function (a, m) { return a + m.total; }, 0) / done.length) : 0;

    v.appendChild(el('div', { class: 'hero' },
      stat('Spent this month', fmt(cur.total, { whole: true }), cur.count + ' transactions', cur.total > caps ? 'neg' : ''),
      stat('Monthly budget', fmt(caps, { whole: true }), cur.total > caps ? fmt(cur.total - caps, { whole: true }) + ' over' : fmt(caps - cur.total, { whole: true }) + ' left', cur.total > caps ? 'neg' : 'pos'),
      stat('On pace for', fmt(proj.projected, { whole: true }), fmt(proj.perDay, { whole: true }) + '/day, day ' + proj.day + ' of ' + proj.days, proj.projected > caps ? 'warn' : 'pos'),
      stat('Typical month', fmt(avg, { whole: true }), done.length ? 'average of ' + done.length + ' full months' : 'not enough history', '')));

    // month over month
    if (series.length > 1) {
      v.appendChild(card('Month over month', [barChart(series, caps), el('div', { class: 'chart-legend' },
        el('span', null, monthLabel(series[0].month)), el('span', null, 'dashed line = budget'), el('span', null, monthLabel(series[series.length - 1].month))),
        el('div', { class: 'tiny muted', style: 'margin-top:8px' }, 'A month only counts everything if a full statement covering it has been loaded. Part-month bars read low.')]));
    }

    // categories with trend
    var tr = L.spendTrend(S.budgets, S.spend, t, 3);
    ['essential', 'non_essential'].forEach(function (kind) {
      var us = tr.filter(function (u) { return u.budget.kind === kind; })
                 .sort(function (a, b) { return b.used - a.used; });
      var rows = us.map(function (u) {
        var arrow = !u.avg ? null : u.delta > u.avg * 0.08 ? ['neg', '▲ ' + fmt(u.delta, { whole: true }) + ' vs usual']
                  : u.delta < -u.avg * 0.08 ? ['pos', '▼ ' + fmt(-u.delta, { whole: true }) + ' vs usual'] : ['muted', 'on pace'];
        return el('div', { class: 'row', style: 'display:block', onclick: function () { budgetDetail(u.budget); } },
          el('div', { style: 'display:flex;justify-content:space-between;gap:10px' },
            el('div', { class: 't' }, u.budget.name, u.count ? el('span', { class: 'dim small' }, '  ' + u.count + 'x') : null),
            el('div', { class: 'amt ' + (u.left < 0 ? 'neg' : '') }, fmt(u.used, { whole: true }), el('span', { class: 'muted' }, ' / ' + fmt(u.cap, { whole: true })))),
          el('div', { class: 'bar' }, el('i', { class: u.left < 0 ? 'over' : '', style: 'width:' + pct(u.pct) })),
          el('div', { class: 'sub', style: 'margin-top:6px;display:flex;justify-content:space-between;gap:8px' },
            el('span', null, u.left < 0 ? fmt(-u.left, { whole: true }) + ' over cap' : fmt(u.left, { whole: true }) + ' left'),
            arrow ? el('span', { class: arrow[0] }, arrow[1]) : null));
      });
      v.appendChild(listCard(kind === 'essential' ? 'Essentials' : 'Non-essentials', rows,
        'No caps set. Tap + Cap to add one.', el('button', { class: 'pill', onclick: function () { budgetForm({ kind: kind }); } }, '+ Cap')));
    });

    // biggest single purchases this month
    var ms = L.monthStart(t);
    var big = S.spend.filter(function (s) { return s.spent_on >= ms; })
      .slice().sort(function (a, b) { return b.amount_cents - a.amount_cents; }).slice(0, 5).map(spendRow);
    if (big.length) v.appendChild(listCard('Biggest this month', big, ''));

    var recent = S.spend.slice(0, 12).map(spendRow);
    v.appendChild(listCard('Recent transactions', recent, 'Nothing logged yet.',
      el('button', { class: 'pill amber', onclick: function () { spendForm(); } }, '+ Log')));
  }
  function spendRow(s) {
    var b = budget(s.budget_id);
    return row({ title: s.note || (b ? b.name : 'Spend'), sub: fdate(s.spent_on) + (b ? ' · ' + b.name : ''),
      amt: fmt(s.amount_cents), amtClass: 'muted', side: s.from_account_id && acct(s.from_account_id) && acct(s.from_account_id).is_business ? 'biz' : 'per',
      onclick: function () { confirmSheet('Delete this spend?', fmt(s.amount_cents) + ' on ' + fdate(s.spent_on) + '. Balances are restored.', 'Delete', function () { return rpc('fin_delete_spend', { p_spend: s.id }).then(function () { toast('Deleted'); }); }); } });
  }
  function monthLabel(iso) { return MONTHS[parseInt(iso.slice(5, 7), 10) - 1] + ' ' + iso.slice(2, 4); }
  function barChart(series, cap) {
    var W = 600, H = 130, pad = 8, n = series.length;
    var mx = Math.max.apply(null, series.map(function (m) { return m.total; }).concat([cap, 1]));
    var bw = (W - pad * 2) / n, gap = Math.min(14, bw * 0.28);
    var capY = pad + (1 - cap / mx) * (H - pad * 2 - 16);
    var bars = series.map(function (m, i) {
      var h = (m.total / mx) * (H - pad * 2 - 16);
      var x = pad + i * bw + gap / 2, y = H - pad - 16 - h;
      var over = m.total > cap;
      return '<rect x="' + x.toFixed(1) + '" y="' + y.toFixed(1) + '" width="' + (bw - gap).toFixed(1) + '" height="' + Math.max(1, h).toFixed(1) +
        '" rx="3" fill="' + (over ? '#f0605d' : '#e9a23b') + '" opacity="' + (i === n - 1 ? '1' : '.65') + '"/>' +
        '<text x="' + (x + (bw - gap) / 2).toFixed(1) + '" y="' + (H - 4) + '" text-anchor="middle" font-size="10" fill="#8b8b8b">' + monthLabel(m.month) + '</text>';
    }).join('');
    var svg = '<svg class="chart" viewBox="0 0 ' + W + ' ' + H + '" preserveAspectRatio="none">' + bars +
      '<line x1="0" x2="' + W + '" y1="' + capY.toFixed(1) + '" y2="' + capY.toFixed(1) + '" stroke="#6aa6f8" stroke-dasharray="5 4" stroke-width="1.5" opacity=".8"/></svg>';
    return el('div', { html: svg });
  }

  function renderPlan(v) {
    var t = L.today();
    var goalRows = S.goals.map(function (g) {
      var p = g.target_cents ? Math.min(1, g.saved_cents / g.target_cents) : 0, left = g.target_cents - g.saved_cents;
      var months = g.target_date ? Math.max(1, Math.ceil(L.diffDays(t, g.target_date) / 30)) : null;
      var need = months && left > 0 ? Math.ceil(left / months) : null;
      return el('div', { class: 'row', style: 'display:block', onclick: function () { goalDetail(g); } },
        el('div', { style: 'display:flex;justify-content:space-between;gap:10px' }, el('div', { class: 't' }, g.name), el('div', { class: 'amt' }, fmt(g.saved_cents, { whole: true }), el('span', { class: 'muted' }, ' / ' + fmt(g.target_cents, { whole: true })))),
        el('div', { class: 'bar' }, el('i', { class: p >= 1 ? 'green' : '', style: 'width:' + pct(p) })),
        el('div', { class: 'sub', style: 'margin-top:6px' }, p >= 1 ? 'Funded' : (need ? fmt(need, { whole: true }) + '/mo to hit ' + fdate(g.target_date) : g.monthly_contribution_cents ? fmt(g.monthly_contribution_cents, { whole: true }) + '/mo planned' : fmt(left, { whole: true }) + ' to go')));
    });
    v.appendChild(listCard('Saving for', goalRows, 'No savings goals. Add a tax set-aside, emergency buffer, equipment fund.', el('button', { class: 'pill', onclick: function () { goalForm(); } }, '+ Goal')));

    v.appendChild(el('div', { class: 'notice' }, el('b', null, 'Spending lives on the Spend tab'), 'Budgets, categories and month-over-month trends moved there.'));
  }
  function planMenu() {
    openSheet('Add', [el('div', { class: 'actions', style: 'flex-direction:column' },
      el('button', { class: 'btn primary', onclick: function () { spendForm(); } }, 'Log spending'),
      el('button', { class: 'btn', onclick: function () { goalForm(); } }, 'New savings goal'),
      el('button', { class: 'btn', onclick: function () { budgetForm(); } }, 'New spending cap'))]);
  }
  function goalDetail(g) {
    openSheet(g.name, [
      el('div', { class: 'kv' }, el('span', null, 'Saved'), el('span', { class: 'pos' }, fmt(g.saved_cents))),
      el('div', { class: 'kv' }, el('span', null, 'Target'), el('span', null, fmt(g.target_cents) + (g.target_date ? ' by ' + fdate(g.target_date) : ''))),
      g.notes ? el('div', { class: 'kv' }, el('span', null, 'Notes'), el('span', { style: 'text-align:right;max-width:70%' }, g.notes)) : null,
      el('div', { class: 'actions', style: 'margin-top:14px' }, el('button', { class: 'btn primary', onclick: function () { contributeForm(g); } }, 'Add money'), el('button', { class: 'btn', onclick: function () { goalForm(g); } }, 'Edit'))
    ]);
  }
  function goalForm(g) {
    var isNew = !g; g = g || {};
    formSheet(isNew ? 'New goal' : 'Edit goal', [
      { k: 'name', label: 'Name', type: 'text', v: g.name, req: true, ph: 'Tax set-aside, 1 month buffer, Paddle inventory' },
      { k: 'target_cents', label: 'Target', type: 'money', v: g.target_cents, req: true, half: true },
      { k: 'saved_cents', label: 'Saved so far', type: 'money', v: g.saved_cents, half: true },
      { k: 'target_date', label: 'By when (optional)', type: 'date', v: g.target_date || '', half: true },
      { k: 'monthly_contribution_cents', label: 'Planned per month', type: 'money', v: g.monthly_contribution_cents, half: true },
      { k: 'notes', label: 'Notes', type: 'textarea', v: g.notes }
    ], function (d) {
      d.target_date = d.target_date || null;
      var p = isNew ? q(sb.from('fin_goals').insert(d)) : q(sb.from('fin_goals').update(d).eq('id', g.id));
      return p.then(function () { toast(isNew ? 'Goal added' : 'Saved'); });
    }, isNew ? null : function () { return confirmSheet('Remove ' + g.name + '?', 'Archives the goal.', 'Remove', function () { return q(sb.from('fin_goals').update({ active: false }).eq('id', g.id)).then(function () { toast('Removed'); }); }); });
  }
  function contributeForm(g) {
    formSheet('Add to ' + g.name, [
      { k: 'amount', label: 'Amount', type: 'money', v: g.monthly_contribution_cents || 0, req: true },
      { k: 'account', label: 'Moved from', type: 'select', v: '', opts: [['', 'Not tracked (no balance change)']].concat(cashAccounts().map(function (a) { return [a.id, a.name]; })) }
    ], function (d) { return rpc('fin_contribute_goal', { p_goal: g.id, p_amount_cents: d.amount, p_account: d.account || null }).then(function () { toast('Added ' + fmt(d.amount)); }); }, null, 'Add');
  }
  function budgetDetail(b) {
    var ms = L.monthStart(L.today());
    var items = S.spend.filter(function (s) { return s.budget_id === b.id && s.spent_on >= ms; });
    openSheet(b.name, [
      el('div', { class: 'kv' }, el('span', null, 'Monthly cap'), el('span', null, fmt(b.monthly_cap_cents))),
      el('div', { class: 'kv' }, el('span', null, 'Kind'), el('span', null, b.kind === 'essential' ? 'Essential' : 'Non-essential')),
      el('div', { class: 'actions', style: 'margin-top:14px' }, el('button', { class: 'btn primary', onclick: function () { spendForm(b); } }, 'Log spend'), el('button', { class: 'btn', onclick: function () { budgetForm(b); } }, 'Edit')),
      items.length ? el('div', { class: 'hist' }, el('div', { class: 'tiny muted', style: 'margin-bottom:4px' }, 'This month'), items.map(function (s) { return el('div', { class: 'kv' }, el('span', null, fdate(s.spent_on) + (s.note ? ' · ' + s.note : '')), el('span', null, fmt(s.amount_cents))); })) : null
    ]);
  }
  function budgetForm(b) {
    var isNew = !b || !b.id; b = b || {};
    formSheet(isNew ? 'Spending cap' : 'Edit cap', [
      { k: 'name', label: 'Name', type: 'text', v: b.name, req: true, ph: 'Groceries, Gas, Eating out' },
      { k: 'kind', label: 'Kind', type: 'select', v: b.kind || 'essential', opts: [['essential', 'Essential'], ['non_essential', 'Non-essential']], half: true },
      { k: 'monthly_cap_cents', label: 'Monthly cap', type: 'money', v: b.monthly_cap_cents, req: true, half: true }
    ], function (d) {
      var p = isNew ? q(sb.from('fin_budgets').insert(d)) : q(sb.from('fin_budgets').update(d).eq('id', b.id));
      return p.then(function () { toast('Saved'); });
    }, isNew ? null : function () { return confirmSheet('Remove ' + b.name + '?', 'Archives the cap. Logged spend stays.', 'Remove', function () { return q(sb.from('fin_budgets').update({ active: false }).eq('id', b.id)).then(function () { toast('Removed'); }); }); });
  }
  function spendForm(b) {
    if (!S.budgets.length) { toast('Add a spending cap first', true); return budgetForm(); }
    formSheet('Log spending', [
      { k: 'budget', label: 'Category', type: 'select', v: b ? b.id : S.budgets[0].id, opts: S.budgets.map(function (x) { return [x.id, x.name + (x.kind === 'essential' ? '' : ' (non-essential)')]; }) },
      { k: 'amount', label: 'Amount', type: 'money', v: '', req: true, half: true },
      { k: 'on', label: 'Date', type: 'date', v: L.today(), req: true, half: true },
      { k: 'from', label: 'Paid with', type: 'select', v: '', opts: payWithOptions() },
      { k: 'note', label: 'Note', type: 'text', v: '' }
    ], function (d) {
      var src = splitSource(d.from);
      return rpc('fin_log_spend', { p_budget: d.budget, p_amount_cents: d.amount, p_spent_on: d.on, p_account: src.account, p_debt: src.debt, p_note: d.note || null }).then(function () { toast('Logged ' + fmt(d.amount)); });
    }, null, 'Log');
  }

  // ---------- ACCOUNTS ----------
  function renderAccounts(v) {
    var cash = L.liquidCash(S.accounts);
    v.appendChild(el('div', { class: 'hero' }, stat('Cash on hand', fmt(cash, { whole: true }), 'all cash accounts', cash < 0 ? 'neg' : ''), stat('Buffer', fmt(reserveCents(), { whole: true }), 'held back from the plan')));
    var TYPE = { checking: 'Checking', savings: 'Savings', cash: 'Cash', other: 'Other', credit: 'Card' };
    var rows = S.accounts.map(function (a) {
      var flight = pendingNet(a.id);
      return row({ title: a.name, sub: TYPE[a.type] + (a.is_business ? ' · business' : ' · personal') + ' · updated ' + fdate(a.updated_at.slice(0, 10)), amt: fmt(a.balance_cents), amtClass: a.balance_cents < 0 ? 'neg' : '',
        amtSub: flight ? (flight > 0 ? '+' : '') + fmt(flight, { whole: true }) + ' in flight' : null, onclick: function () { accountForm(a); } });
    });
    v.appendChild(listCard('Accounts', rows, 'Add checking, savings, business checking. Credit cards go under Debts.'));
    v.appendChild(card('Settings', [
      el('div', { class: 'kv' }, el('span', null, 'Cash buffer the plan never spends'), el('button', { class: 'pill amber', onclick: bufferForm }, fmt(reserveCents(), { whole: true }))),
      el('div', { class: 'kv' }, el('span', null, 'Forecast includes likely income'), el('button', { class: 'pill ' + (S.prefs.includeLikely ? 'blue' : ''), onclick: function () { S.prefs.includeLikely = !S.prefs.includeLikely; savePrefs(); render(); } }, S.prefs.includeLikely ? 'On' : 'Off')),
      el('div', { class: 'kv' }, el('span', null, 'Access'), el('span', { class: 'small' }, S.user ? S.user.email : 'Open (no login)')),
      el('div', { class: 'actions', style: 'margin-top:12px' }, el('button', { class: 'btn', onclick: function () { refresh().then(function () { toast('Refreshed'); }); } }, 'Refresh'), S.user ? el('button', { class: 'btn danger', onclick: function () { sb.auth.signOut().then(function () { location.reload(); }); } }, 'Sign out') : null)
    ]));
    v.appendChild(el('div', { class: 'dim small', style: 'text-align:center;padding:8px 0 20px' }, 'On iPhone: Share → Add to Home Screen for the app icon.'));
  }
  function accountForm(a) {
    var isNew = !a; a = a || {};
    formSheet(isNew ? 'New account' : a.name, [
      { k: 'name', label: 'Name', type: 'text', v: a.name, req: true, ph: 'Business checking, Joint checking' },
      { k: 'type', label: 'Type', type: 'select', v: a.type || 'checking', opts: [['checking', 'Checking'], ['savings', 'Savings'], ['cash', 'Cash'], ['other', 'Other']], half: true },
      { k: 'balance_cents', label: 'Current balance', type: 'money', v: a.balance_cents, req: true, half: true, allowNeg: true },
      { k: 'is_business', label: 'Business account', type: 'check', v: !!a.is_business }
    ], function (d) {
      var p = isNew ? q(sb.from('fin_accounts').insert(d)) : q(sb.from('fin_accounts').update(d).eq('id', a.id));
      return p.then(function () { toast('Saved'); });
    }, isNew ? null : function () { return confirmSheet('Remove ' + a.name + '?', 'Archives the account.', 'Remove', function () { return q(sb.from('fin_accounts').update({ archived: true }).eq('id', a.id)).then(function () { toast('Removed'); }); }); });
  }
  function bufferForm() {
    formSheet('Cash buffer', [{ k: 'amount', label: 'Never let the plan spend below', type: 'money', v: reserveCents(), req: true }], function (d) { S.prefs.reserve = d.amount; savePrefs(); return Promise.resolve(); }, null, 'Save');
  }

  // ---------- sheets & forms ----------
  var sheetBg = $('#sheet-bg'), sheet = $('#sheet');
  function openSheet(title, body) {
    clear(sheet); sheet.appendChild(el('div', { class: 'grab' })); if (title) sheet.appendChild(el('h3', null, title)); append(sheet, body); sheetBg.classList.add('on'); document.body.style.overflow = 'hidden';
  }
  function closeSheet() { sheetBg.classList.remove('on'); document.body.style.overflow = ''; }
  sheetBg.addEventListener('click', function (e) { if (e.target === sheetBg) closeSheet(); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeSheet(); });

  function rpc(name, args) { return q(sb.rpc(name, args)); }

  function formSheet(title, fields, onSubmit, onDelete, submitLabel) {
    var form = el('form', { novalidate: true }), err = el('div', { class: 'formerr' }), grid = null;
    fields.forEach(function (f) {
      var input;
      if (f.type === 'select') { input = el('select', { name: f.k }); f.opts.forEach(function (o) { input.appendChild(el('option', { value: o[0], selected: String(f.v) === String(o[0]) ? true : null }, o[1])); }); }
      else if (f.type === 'textarea') input = el('textarea', { name: f.k, rows: 2 }, f.v || '');
      else if (f.type === 'check') input = el('input', { type: 'checkbox', name: f.k, checked: f.v ? true : null });
      else if (f.type === 'money') input = el('input', { type: 'text', inputmode: 'decimal', name: f.k, value: f.v === '' || f.v === undefined || f.v === null ? '' : (f.v / 100).toFixed(2), placeholder: '0.00' });
      else input = el('input', { type: f.type, name: f.k, value: f.v === undefined || f.v === null ? '' : f.v, placeholder: f.ph || null, step: f.step || null, inputmode: f.type === 'number' ? 'decimal' : null });
      var wrap = el('div', { class: 'field ' + (f.type === 'check' ? 'check' : f.type === 'money' ? 'money' : '') });
      if (f.type === 'check') { wrap.appendChild(input); wrap.appendChild(el('label', null, f.label)); }
      else { wrap.appendChild(el('label', null, f.label)); wrap.appendChild(input); }
      if (f.half) { if (!grid) { grid = el('div', { class: 'grid2' }); form.appendChild(grid); } grid.appendChild(wrap); }
      else { grid = null; form.appendChild(wrap); }
    });
    form.appendChild(err);
    var submit = el('button', { class: 'btn primary', type: 'submit' }, submitLabel || 'Save');
    form.appendChild(el('div', { class: 'actions' }, el('button', { class: 'btn', type: 'button', onclick: closeSheet }, 'Cancel'), submit));
    if (onDelete) form.appendChild(el('div', { class: 'del' }, el('button', { class: 'btn danger sm', type: 'button', onclick: function () { onDelete(); } }, 'Remove')));
    form.addEventListener('submit', function (ev) {
      ev.preventDefault(); err.textContent = '';
      var data = {};
      for (var i = 0; i < fields.length; i++) {
        var f = fields[i], inp = form.elements[f.k], val;
        if (f.type === 'check') val = !!inp.checked;
        else if (f.type === 'money') { val = L.toCents(inp.value); if (f.req && !inp.value.trim()) { err.textContent = f.label + ' is required.'; inp.focus(); return; } if (val < 0 && !f.allowNeg) { err.textContent = f.label + ' cannot be negative.'; return; } }
        else { val = inp.value.trim(); if (f.req && !val) { err.textContent = f.label + ' is required.'; inp.focus(); return; } }
        data[f.k] = val;
      }
      submit.disabled = true;
      Promise.resolve().then(function () { return onSubmit(data); }).then(function () { closeSheet(); return refresh(); })
        .catch(function (e) { err.textContent = e.message || 'Something went wrong.'; submit.disabled = false; });
    });
    openSheet(title, form);
    var first = form.querySelector('input[type=text],input[type=email]'); if (first && !first.value && window.innerWidth > 900) first.focus();
  }
  function confirmSheet(title, msg, label, action) {
    var btn = el('button', { class: 'btn primary', onclick: function () { btn.disabled = true; action().then(function () { closeSheet(); return refresh(); }).catch(function (e) { toast(e.message || 'Failed', true); btn.disabled = false; }); } }, label);
    openSheet(title, [el('p', { class: 'muted', style: 'margin:0 0 14px' }, msg), el('div', { class: 'actions' }, el('button', { class: 'btn', onclick: closeSheet }, 'Cancel'), btn)]);
  }

  // ---------- PWA ----------
  if ('serviceWorker' in navigator && location.protocol === 'https:') navigator.serviceWorker.register('./sw.js').catch(function () {});
  document.addEventListener('visibilitychange', function () { if (!document.hidden && (S.user || !REQUIRE_LOGIN)) refresh(); });
})();
