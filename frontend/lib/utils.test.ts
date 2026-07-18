import { describe, expect, it } from "vitest";

import { cn, formatPercent } from "./utils";

describe("cn", () => {
  it("joins truthy class names", () => {
    expect(cn("a", false, "b", null, undefined, "c")).toBe("a b c");
  });

  it("returns an empty string when nothing is truthy", () => {
    expect(cn(false, null, undefined)).toBe("");
  });
});

describe("formatPercent", () => {
  it("formats a ratio with one fraction digit by default", () => {
    expect(formatPercent(0.8123)).toBe("81.2%");
  });

  it("clamps values outside [0, 1]", () => {
    expect(formatPercent(1.5)).toBe("100.0%");
    expect(formatPercent(-0.2)).toBe("0.0%");
  });

  it("returns an em dash for NaN", () => {
    expect(formatPercent(Number.NaN)).toBe("—");
  });
});
