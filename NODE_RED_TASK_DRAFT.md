[App Development] Node-RED Connector

Develop the Node-RED Connector in maximum scope: all viable official Node-RED Admin API capabilities plus Imperal-side efficiency features. Complete official API discovery and preparation first; use typed inputs, secret-safe storage, explicit confirmation for destructive/runtime-impacting actions, compliant panel settings, action pricing, public Git repository, validation, Imperal deployment, and Marketplace review submission only when unblocked.

Acceptance gates:
- `CONNECTOR_DISCOVERY.md` records the full official capability map and Tier 1–3 scope.
- `PREPARATION.md` records users, P0, safety gates, panel UX and roadmap.
- All implementation handlers use typed models and do not expose secrets.
- Pricing uses the standard {0, 8, 16, 20, 40, 60} scale.
- Public Git remote is verified without secrets.
- `imperal validate .` succeeds before deploy/review.
