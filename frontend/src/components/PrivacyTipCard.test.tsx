import { render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

const { getPrivacyTipMock } = vi.hoisted(() => ({
  getPrivacyTipMock: vi.fn(),
}));

vi.mock("../services/external", () => ({
  externalService: {
    getPrivacyTip: getPrivacyTipMock,
  },
}));

import { PrivacyTipCard } from "./PrivacyTipCard";

describe("PrivacyTipCard", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders fetched tip", async () => {
    getPrivacyTipMock.mockResolvedValueOnce({
      title: "Совет",
      content: "Скрывайте номер документа",
      source: "api-ninjas",
      fetched_at: new Date().toISOString(),
      fallback: false,
    });

    render(<PrivacyTipCard />);

    await waitFor(() => {
      expect(screen.getByText("Скрывайте номер документа")).toBeInTheDocument();
    });
  });

  it("renders error state", async () => {
    getPrivacyTipMock.mockRejectedValueOnce(new Error("fail"));

    render(<PrivacyTipCard />);

    await waitFor(() => {
      expect(screen.getByText(/Не удалось загрузить внешний совет/i)).toBeInTheDocument();
    });
  });
});
