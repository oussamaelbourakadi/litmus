# Security Policy

## Reporting a vulnerability

Litmus is a security-adjacent project (it red-teams AI systems), so we take the
security of the tool itself seriously.

Please **do not** open a public issue for security vulnerabilities. Instead,
report privately through GitHub's
[private vulnerability reporting](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing-information-about-vulnerabilities/privately-reporting-a-security-vulnerability)
on this repository.

We aim to acknowledge reports within 72 hours.

## Scope & principles

- No secrets are ever committed to the repository (`.env.example` only, enforced
  by gitleaks in CI).
- The platform runs with **no API key** by design (mock + local providers).
- Adversarial attack modules are strictly bounded and run in controlled contexts.
