[App Development] Node-RED Connector

Develop Node-RED Connector at maximum scope: full viable coverage of Node-RED’s official Admin HTTP API and documented runtime capabilities, plus Imperal-side efficiency tooling. The user explicitly approved the maximum-release form in the initial request.

Required delivery:
- Complete official API discovery and PREPARATION before implementation.
- Use typed parameter models, BYOK Admin API access, secret-safe storage and multi-connection isolation.
- Cover flows, runtime, nodes/modules, credentials metadata, projects and settings where exposed by the connected Node-RED runtime.
- Add Imperal value-add: runtime health audit, inactive/unmanaged flow inventory, dependency/risk summaries, safe flow deployment preview and explicit confirmation gates for runtime-affecting or destructive actions.
- Build panels following the UI standard; exactly one final sidebar secondary button: App settings.
- Price all actions before deployment using the standard 0/8/16/20/40/60 scale.
- Run syntax tests, handler tests, `imperal build .` and `imperal validate .`.
- Verify a public Git remote and ensure no secrets are committed.
- Deploy to Imperal and submit to Marketplace review only when validation/deploy is unblocked.

Acceptance criteria: functional coverage is documented against official Node-RED references; no secret values are returned; destructive actions use platform confirmation; public Git and Marketplace submission are evidenced in the task.
