# Adversarial reference API guidelines

This autonomous security fixture extends the reference suite without changing the
nine Light/Heavy/private repositories or their common contract.

- Keep Python 3.12, root pinned manifests, and no APIZIT-internal imports.
- Preserve fixed resource bounds and default-disabled real STS/local peer probes.
- Never add secret reads, credential inspection/output, arbitrary URLs/paths/commands,
  AWS mutations, destructive actions, uncontrolled workloads or automatic deployment.
- Update tests, scenario READMEs and the platform SECURITY_TEST_APIS.md catalog together.
- CI must use SDK/HTTP doubles, never real AWS, credentials or third-party targets.
- Run Ruff, pytest, import/manifest checks and a local APIZIT scan before publication.
- Publish via codex/ branches, CI and pull requests. Dev launch is a separate campaign.
