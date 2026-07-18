/**
 * Small presentation helpers. Kept pure and framework-free so they are unit
 * testable without a DOM.
 */

/** Join truthy class names into a single className string. */
export function cn(...classes: Array<string | false | null | undefined>): string {
  return classes.filter(Boolean).join(" ");
}

/** Format a 0..1 ratio as a percentage string, e.g. 0.8123 -> "81.2%". */
export function formatPercent(ratio: number, fractionDigits = 1): string {
  if (Number.isNaN(ratio)) return "—";
  const clamped = Math.min(1, Math.max(0, ratio));
  return `${(clamped * 100).toFixed(fractionDigits)}%`;
}

/** Format a signed delta ratio, e.g. -0.05 -> "-5.0%". */
export function formatSignedPercent(delta: number, fractionDigits = 1): string {
  if (Number.isNaN(delta)) return "—";
  const sign = delta > 0 ? "+" : "";
  return `${sign}${(delta * 100).toFixed(fractionDigits)}%`;
}

/** Format a latency in milliseconds. */
export function formatMs(ms: number): string {
  if (Number.isNaN(ms)) return "—";
  if (ms > 0 && ms < 1) return "<1 ms";
  return `${ms.toFixed(0)} ms`;
}

/** Format an estimated cost in USD. */
export function formatCost(usd: number): string {
  if (Number.isNaN(usd)) return "—";
  if (usd === 0) return "$0";
  return `$${usd.toFixed(4)}`;
}
