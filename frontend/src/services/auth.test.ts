import { beforeEach, describe, expect, it, vi } from "vitest";

const { postMock, getMock, putMock, deleteMock } = vi.hoisted(() => ({
  postMock: vi.fn(),
  getMock: vi.fn(),
  putMock: vi.fn(),
  deleteMock: vi.fn(),
}));

vi.mock("./api", () => ({
  default: {
    post: postMock,
    get: getMock,
    put: putMock,
    delete: deleteMock,
  },
}));

import { authService } from "./auth";

describe("authService", () => {
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
  });

  it("stores tokens in localStorage on login", async () => {
    postMock.mockResolvedValueOnce({
      data: {
        access_token: "acc-token",
        refresh_token: "ref-token",
        token_type: "bearer",
      },
    });

    const result = await authService.login({ login: "u", password: "password123" });

    expect(result.access_token).toBe("acc-token");
    expect(localStorage.getItem("access_token")).toBe("acc-token");
    expect(localStorage.getItem("refresh_token")).toBe("ref-token");
  });

  it("clears tokens on logout even if API fails", async () => {
    localStorage.setItem("access_token", "x");
    localStorage.setItem("refresh_token", "y");
    postMock.mockRejectedValueOnce(new Error("network"));
    const consoleErrorSpy = vi.spyOn(console, "error").mockImplementation(() => undefined);

    await authService.logout();

    expect(localStorage.getItem("access_token")).toBeNull();
    expect(localStorage.getItem("refresh_token")).toBeNull();
    expect(consoleErrorSpy).toHaveBeenCalled();
    consoleErrorSpy.mockRestore();
  });

  it("returns authentication state by access token", () => {
    expect(authService.isAuthenticated()).toBe(false);
    localStorage.setItem("access_token", "token");
    expect(authService.isAuthenticated()).toBe(true);
  });
});
