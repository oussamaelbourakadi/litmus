# Litmus — Frontend

Next.js (App Router) + TypeScript (strict) + Tailwind CSS. Part of the
[Litmus](../README.md) monorepo.

## Local development

```bash
npm install
npm run dev        # http://localhost:3000
```

Set `NEXT_PUBLIC_API_URL` (see `.env.example`) to point at the backend.

## Quality gates

```bash
npm run lint
npm run typecheck
npm run test
npm run build
```
