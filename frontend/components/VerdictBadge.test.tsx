import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { VerdictBadge } from "./VerdictBadge";

describe("VerdictBadge", () => {
  it("shows PASS when passed", () => {
    render(<VerdictBadge passed />);
    expect(screen.getByText("PASS")).toBeInTheDocument();
  });

  it("shows REGRESSION when failed", () => {
    render(<VerdictBadge passed={false} />);
    expect(screen.getByText("REGRESSION")).toBeInTheDocument();
  });
});
