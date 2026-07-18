import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { EmptyState, ErrorState } from "./ui";

describe("state components", () => {
  it("EmptyState renders its message", () => {
    render(<EmptyState message="nothing here yet" />);
    expect(screen.getByText("nothing here yet")).toBeInTheDocument();
  });

  it("ErrorState renders its message", () => {
    render(<ErrorState message="something broke" />);
    expect(screen.getByText(/something broke/)).toBeInTheDocument();
  });
});
