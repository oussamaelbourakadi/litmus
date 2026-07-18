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
