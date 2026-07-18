import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { MetricCard } from "./MetricCard";

describe("MetricCard", () => {
  it("renders label, value, and sub", () => {
    render(<MetricCard label="Success rate" value="80%" sub="95% CI" />);
    expect(screen.getByText("Success rate")).toBeInTheDocument();
    expect(screen.getByText("80%")).toBeInTheDocument();
    expect(screen.getByText("95% CI")).toBeInTheDocument();
  });
});
