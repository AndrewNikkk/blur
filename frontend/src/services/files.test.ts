import { beforeEach, describe, expect, it, vi } from "vitest";

const { apiGetMock, apiPostMock, apiDeleteMock } = vi.hoisted(() => ({
  apiGetMock: vi.fn(),
  apiPostMock: vi.fn(),
  apiDeleteMock: vi.fn(),
}));

vi.mock("./api", () => ({
  default: {
    get: apiGetMock,
    post: apiPostMock,
    delete: apiDeleteMock,
  },
}));

vi.mock("../utils/constants", () => ({
  API_URL: "http://localhost:8000",
}));

import { fileService } from "./files";

describe("fileService", () => {
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
    vi.unstubAllGlobals();
  });

  it("throws when download requested without auth/session", async () => {
    await expect(fileService.downloadFile(10, "x.jpg")).rejects.toThrow(
      "Требуется авторизация или session_id для скачивания файла",
    );
  });

  it("throws when view requested without auth/session", async () => {
    await expect(fileService.viewFile(10)).rejects.toThrow(
      "Требуется авторизация или session_id для просмотра файла",
    );
  });

  it("calls download-url with auth headers", async () => {
    localStorage.setItem("access_token", "acc");
    localStorage.setItem("session_id", "sid");

    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        url: "http://localhost:9000/file",
        filename: "server-name.png",
      }),
    });
    vi.stubGlobal("fetch", fetchMock);

    const clickMock = vi.fn();
    const anchor = document.createElement("a");
    anchor.click = clickMock;
    const createElementSpy = vi.spyOn(document, "createElement").mockReturnValue(anchor);

    await fileService.downloadFile(42, "client-name.png");

    expect(fetchMock).toHaveBeenCalledWith("http://localhost:8000/files/42/download-url", {
      method: "GET",
      headers: {
        Authorization: "Bearer acc",
        "X-Session-ID": "sid",
      },
    });
    expect(createElementSpy).toHaveBeenCalledWith("a");
    expect(anchor.download).toBe("client-name.png");
    expect(clickMock).toHaveBeenCalled();
  });

  it("opens new tab for view-url response", async () => {
    localStorage.setItem("session_id", "sid");

    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      text: async () => "",
      json: async () => ({ url: "http://localhost:9000/view-file" }),
    });
    vi.stubGlobal("fetch", fetchMock);

    const openMock = vi.fn();
    vi.stubGlobal("open", openMock);

    await fileService.viewFile(7);

    expect(fetchMock).toHaveBeenCalledWith("http://localhost:8000/files/7/view-url", {
      method: "GET",
      headers: {
        "X-Session-ID": "sid",
      },
    });
    expect(openMock).toHaveBeenCalledWith("http://localhost:9000/view-file", "_blank", "noopener,noreferrer");
  });
});
