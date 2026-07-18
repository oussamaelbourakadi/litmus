import { afterEach, describe, expect, it, vi } from "vitest";

import { createProject, listProjects } from "./api";

function mockFetch(data: unknown, ok = true, status = 200) {
  return vi.fn().mockResolvedValue({
    ok,
    status,
    statusText: "OK",
    json: async () => data,
  } as unknown as Response);
}

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("api client", () => {
  it("listProjects returns the parsed array", async () => {
    vi.stubGlobal(
      "fetch",
      mockFetch([{ id: "1", name: "P", slug: "p", description: null }]),
    );
    const projects = await listProjects();
    expect(projects).toHaveLength(1);
    expect(projects[0]?.slug).toBe("p");
  });

  it("createProject issues a POST and returns the project", async () => {
    const fetchMock = mockFetch({ id: "2", name: "X", slug: "x", description: null });
    vi.stubGlobal("fetch", fetchMock);

    const project = await createProject({ name: "X", slug: "x" });
    expect(project.id).toBe("2");

    const call = fetchMock.mock.calls[0];
    expect(call?.[1]?.method).toBe("POST");
  });

  it("throws with the server detail on an error response", async () => {
    vi.stubGlobal("fetch", mockFetch({ detail: "boom" }, false, 400));
    await expect(listProjects()).rejects.toThrow("boom");
  });
});
