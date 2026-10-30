# Kiln

Personal strength training PWA. Replaces Fitbod.

- Recovery-based workout generation (Push/Pull/Legs, Upper/Lower, Full Body)
- Double progression + est. 1RM weight recommendations
- Rest timer, warm-ups, plate math, swap/add/reorder exercises
- History, PRs, muscle recovery, weekly volume, bodyweight trend
- Imports Fitbod / Strong / Hevy CSV exports; JSON backup + restore

No build step. Static files, deployed on Vercel. All data is stored on-device (localStorage).

## Tests

`npm test` runs the body-composition math tests (`tests/bodycomp.test.js`, Node's built-in test runner, no install needed).
