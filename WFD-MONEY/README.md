# WFD Money

Household cash-flow app: bills, income (actual and projected), debts, savings goals, spending caps, and a 30-day pay plan that tells you what to pay now, what to wait on, and where you are short.

- Frontend: static HTML/CSS/JS in this folder (no build step). Installable as a PWA on iPhone via Share → Add to Home Screen.
- Backend: Supabase project `wfd-command-center` (tables prefixed `fin_`, RPCs prefixed `fin_`). Data is scoped to the household via the existing `private.is_household_member` RLS helper, so both household logins see the same data.
- Deploy: Vercel project `wfd-money`. Root directory is this folder.

## Logic
`logic.js` is pure and unit-testable: date math, bill occurrences, 45-day forecast, and the greedy pay plan (confirmed income only; essentials first on ties; held bills search forward for the first day cash covers them).

## Rules baked in
- Only confirmed income counts toward the pay plan. Likely income is a forecast toggle. Maybe never counts.
- Credit cards live under Debts. Paying a bill or logging spend "with" a card raises the card balance.
- A bill linked to a debt reduces that debt when paid.
- A cash buffer (Accounts → Settings) is held back from the plan.
