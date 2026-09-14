/* Pure money logic: date helpers, cash forecast, pay plan. No DOM, no network.
   Works in the browser (window.FinLogic) and in node (module.exports) for tests. */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.FinLogic = factory();
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  // ---- dates (all as 'YYYY-MM-DD' strings, local, no timezone drift) ----
  function pad(n) { return n < 10 ? '0' + n : '' + n; }
  function toISO(d) { return d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate()); }
  function parse(s) { var p = s.split('-'); return new Date(+p[0], +p[1] - 1, +p[2]); }
  function today() { return toISO(new Date()); }
  function addDays(s, n) { var d = parse(s); d.setDate(d.getDate() + n); return toISO(d); }
  function addMonths(s, n) {
    var d = parse(s), day = d.getDate();
    d.setDate(1); d.setMonth(d.getMonth() + n);
    var last = new Date(d.getFullYear(), d.getMonth() + 1, 0).getDate();
    d.setDate(Math.min(day, last));
    return toISO(d);
  }
  function diffDays(a, b) { return Math.round((parse(b) - parse(a)) / 86400000); }
  function nextDue(s, freq) {
    switch (freq) {
      case 'weekly': return addDays(s, 7);
      case 'biweekly': return addDays(s, 14);
      case 'monthly': return addMonths(s, 1);
      case 'quarterly': return addMonths(s, 3);
      case 'annual': return addMonths(s, 12);
      default: return null;
    }
  }
  function monthStart(s) { return s.slice(0, 8) + '01'; }
  function monthEnd(s) { return addDays(addMonths(monthStart(s), 1), -1); }

  // ---- money ----
  function fmt(cents, opts) {
    opts = opts || {};
    var neg = cents < 0, v = Math.abs(cents) / 100;
    var str = v.toLocaleString('en-US', { minimumFractionDigits: opts.whole ? 0 : 2, maximumFractionDigits: opts.whole ? 0 : 2 });
    return (neg ? '-' : '') + '$' + str;
  }
  function toCents(str) {
    if (str === null || str === undefined) return 0;
    var n = parseFloat(String(str).replace(/[^0-9.\-]/g, ''));
    return isNaN(n) ? 0 : Math.round(n * 100);
  }

  // ---- bill occurrences within a horizon ----
  // bills: [{id,name,amount_cents,frequency,next_due_date,active,essential,autopay,category}]
  function billOccurrences(bills, from, to) {
    var out = [];
    bills.forEach(function (b) {
      if (!b.active) return;
      var d = b.next_due_date, guard = 0;
      while (d && d <= to && guard++ < 200) {
        out.push({ bill: b, due: d, effective: d < from ? from : d, overdue: d < from });
        if (b.frequency === 'once') break;
        d = nextDue(d, b.frequency);
      }
    });
    out.sort(function (a, b) {
      if (a.effective !== b.effective) return a.effective < b.effective ? -1 : 1;
      if (a.bill.essential !== b.bill.essential) return a.bill.essential ? -1 : 1;
      return b.bill.amount_cents - a.bill.amount_cents;
    });
    return out;
  }

  // ---- liquid cash across accounts ----
  function liquidCash(accounts) {
    return accounts.reduce(function (s, a) {
      if (a.archived) return s;
      if (a.type === 'credit') return s;
      return s + a.balance_cents;
    }, 0);
  }
  function cardDebt(accounts) {
    return accounts.reduce(function (s, a) { return (!a.archived && a.type === 'credit') ? s + a.balance_cents : s; }, 0);
  }

  // ---- income events within horizon ----
  function incomeEvents(income, from, to, includeLikely) {
    return income.filter(function (i) {
      if (i.received_on) return false;
      if (i.expected_date > to) return false;
      if (i.confidence === 'confirmed') return true;
      if (i.confidence === 'likely') return !!includeLikely;
      return false;
    }).map(function (i) {
      return { income: i, date: i.expected_date < from ? from : i.expected_date };
    }).sort(function (a, b) { return a.date < b.date ? -1 : a.date > b.date ? 1 : 0; });
  }

  // ---- day-by-day forecast ----
  function forecast(opts) {
    var from = opts.today || today();
    var days = opts.days || 45;
    var to = addDays(from, days);
    var occ = billOccurrences(opts.bills, from, to);
    var inc = incomeEvents(opts.income, from, to, opts.includeLikely);
    var bal = opts.cash;
    var timeline = [];
    var minBal = bal, minDate = from, firstNeg = null;
    for (var i = 0; i <= days; i++) {
      var d = addDays(from, i), ins = 0, outs = 0, items = [];
      inc.forEach(function (e) { if (e.date === d) { ins += e.income.amount_cents; items.push({ kind: 'in', label: e.income.source, amount: e.income.amount_cents, confidence: e.income.confidence }); } });
      occ.forEach(function (o) { if (o.effective === d) { outs += o.bill.amount_cents; items.push({ kind: 'out', label: o.bill.name, amount: o.bill.amount_cents, overdue: o.overdue, essential: o.bill.essential }); } });
      bal = bal + ins - outs;
      if (bal < minBal) { minBal = bal; minDate = d; }
      if (bal < 0 && firstNeg === null) firstNeg = d;
      timeline.push({ date: d, balance: bal, ins: ins, outs: outs, items: items });
    }
    return { from: from, to: to, start: opts.cash, end: bal, minBalance: minBal, minDate: minDate, firstNegative: firstNeg, timeline: timeline,
      totalOut: occ.reduce(function (s, o) { return s + o.bill.amount_cents; }, 0),
      totalIn: inc.reduce(function (s, e) { return s + e.income.amount_cents; }, 0) };
  }

  // ---- pay plan ----
  // Greedy: walk bills chronologically (essentials first on ties). Confirmed income only.
  // A bill is "pay" if cash on its due date covers it after earlier planned payments.
  // Otherwise it is "held" and we search forward for the first day cash covers it.
  function payPlan(opts) {
    var from = opts.today || today();
    var days = opts.days || 30;
    var to = addDays(from, days);
    var occ = billOccurrences(opts.bills, from, to);
    var inc = incomeEvents(opts.income, from, to, false);
    var reserve = opts.reserve || 0;

    // cash available on each day (index by offset) before any bills, confirmed income only
    var avail = [];
    var running = opts.cash - reserve;
    for (var i = 0; i <= days; i++) {
      var d = addDays(from, i);
      inc.forEach(function (e) { if (e.date === d) running += e.income.amount_cents; });
      avail.push(running);
    }
    function spendFrom(idx, amt) { for (var k = idx; k <= days; k++) avail[k] -= amt; }

    var plan = [], held = [];
    occ.forEach(function (o) {
      var idx = diffDays(from, o.effective);
      if (avail[idx] >= o.bill.amount_cents) {
        spendFrom(idx, o.bill.amount_cents);
        plan.push({ occ: o, status: o.overdue ? 'overdue' : (idx <= 3 ? 'now' : 'scheduled'), payOn: o.effective, late: false });
      } else held.push(o);
    });
    held.forEach(function (o) {
      var idx = diffDays(from, o.effective), found = -1;
      for (var k = idx; k <= days; k++) { if (avail[k] >= o.bill.amount_cents) { found = k; break; } }
      if (found >= 0) {
        spendFrom(found, o.bill.amount_cents);
        var payOn = addDays(from, found);
        var src = inc.filter(function (e) { return e.date === payOn; }).map(function (e) { return e.income.source; });
        plan.push({ occ: o, status: 'wait', payOn: payOn, late: payOn > o.due, waitFor: src });
      } else {
        // Unfunded. Count only the part not covered by whatever cash is left, then consume it
        // so later unfunded bills don't measure against the same pool.
        var maxAvail = Math.max.apply(null, avail.slice(idx));
        var short = o.bill.amount_cents - Math.max(0, maxAvail);
        spendFrom(idx, o.bill.amount_cents);
        plan.push({ occ: o, status: 'short', payOn: null, late: true, shortBy: short });
      }
    });
    plan.sort(function (a, b) {
      // anything already past due stays pinned at the top, funded or not
      var ao = a.occ.overdue ? 0 : 1, bo = b.occ.overdue ? 0 : 1;
      if (ao !== bo) return ao - bo;
      var order = { overdue: 0, now: 1, wait: 2, scheduled: 3, short: 4 };
      if (order[a.status] !== order[b.status]) return order[a.status] - order[b.status];
      var ad = a.payOn || a.occ.effective, bd = b.payOn || b.occ.effective;
      return ad < bd ? -1 : ad > bd ? 1 : 0;
    });
    var shortTotal = plan.filter(function (p) { return p.status === 'short'; }).reduce(function (s, p) { return s + p.shortBy; }, 0);
    return { plan: plan, shortTotal: shortTotal, from: from, to: to };
  }

  // ---- budgets ----
  function budgetUsage(budgets, spend, monthISO) {
    var ms = monthStart(monthISO), me = monthEnd(monthISO);
    return budgets.filter(function (b) { return b.active; }).map(function (b) {
      var used = spend.filter(function (s) { return s.budget_id === b.id && s.spent_on >= ms && s.spent_on <= me; })
        .reduce(function (t, s) { return t + s.amount_cents; }, 0);
      return { budget: b, used: used, left: b.monthly_cap_cents - used, pct: b.monthly_cap_cents ? Math.min(1, used / b.monthly_cap_cents) : 0 };
    });
  }

  // ---- debt payoff estimate (months at current min payment, simple interest approx) ----
  function payoffMonths(balance, apr, payment) {
    if (balance <= 0) return 0;
    if (payment <= 0) return Infinity;
    var r = (apr || 0) / 100 / 12;
    if (r === 0) return Math.ceil(balance / payment);
    if (payment <= balance * r) return Infinity;
    return Math.ceil(-Math.log(1 - (balance * r) / payment) / Math.log(1 + r));
  }

  return { toISO: toISO, parse: parse, today: today, addDays: addDays, addMonths: addMonths, diffDays: diffDays, nextDue: nextDue,
    monthStart: monthStart, monthEnd: monthEnd, fmt: fmt, toCents: toCents, billOccurrences: billOccurrences, liquidCash: liquidCash,
    cardDebt: cardDebt, incomeEvents: incomeEvents, forecast: forecast, payPlan: payPlan, budgetUsage: budgetUsage, payoffMonths: payoffMonths };
});
