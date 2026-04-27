import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

const { mockNavigate, loginMock } = vi.hoisted(() => ({
  mockNavigate: vi.fn(),
  loginMock: vi.fn(),
}));

vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual<typeof import("react-router-dom")>("react-router-dom");
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

vi.mock("../services/auth", () => ({
  authService: {
    login: loginMock,
    isAuthenticated: () => false,
  },
}));

vi.mock("../hooks/useSeo", () => ({
  useSeo: () => undefined,
}));

import { Login } from "./Login";

describe("Login component", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("shows validation error for empty fields", async () => {
    render(
      <MemoryRouter>
        <Login />
      </MemoryRouter>,
    );

    fireEvent.change(screen.getByPlaceholderText("Введите логин"), { target: { value: "user1" } });
    fireEvent.submit(screen.getByRole("button", { name: "Войти" }).closest("form")!);

    expect(await screen.findByText("Заполните все поля")).toBeInTheDocument();
  });

  it("navigates to home on successful login", async () => {
    loginMock.mockResolvedValueOnce({
      access_token: "a",
      refresh_token: "b",
      token_type: "bearer",
    });

    render(
      <MemoryRouter>
        <Login />
      </MemoryRouter>,
    );

    fireEvent.change(screen.getByPlaceholderText("Введите логин"), { target: { value: "user1" } });
    fireEvent.change(screen.getByPlaceholderText("Введите пароль"), { target: { value: "password123" } });
    fireEvent.click(screen.getByRole("button", { name: "Войти" }));

    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith("/");
    });
  });
});
