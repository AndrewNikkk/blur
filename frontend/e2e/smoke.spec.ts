import { expect, test } from "@playwright/test";

test.describe("Core user flows", () => {
  test("home page renders and opens login page", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByRole("link", { name: "Войти" })).toBeVisible();

    await page.getByRole("link", { name: "Войти" }).click();
    await expect(page.getByRole("heading", { name: "Вход в систему" })).toBeVisible();
  });

  test("unknown route shows 404 page", async ({ page }) => {
    await page.goto("/non-existent-page");
    await expect(page.getByRole("heading", { name: "Страница не найдена" })).toBeVisible();
  });

  test("home page shows privacy tip card", async ({ page }) => {
    await page.goto("/");

    const privacyCard = page.getByLabel("Совет по защите данных");
    await expect(privacyCard).toBeVisible();
    await expect(privacyCard.getByRole("heading", { name: "Совет по безопасности", exact: true })).toBeVisible();
  });

  test("user can login upload process and download file (mocked API)", async ({ page }) => {
    const uploadedFile = {
      id: 1,
      filename: "left-arrow.png",
      original_filename: "left-arrow.png",
      file_size: 1234,
      mime_type: "image/png",
      status: "uploaded",
      user_id: 1,
      session_id: null,
      created_at: new Date().toISOString(),
      processed_at: null,
      processed_file_path: null,
    };

    const processedFile = {
      ...uploadedFile,
      filename: "left-arrow_blured.png",
      status: "processed",
      processed_at: new Date().toISOString(),
      processed_file_path: "processed/left-arrow_blured.png",
    };

    let downloadUrlRequested = false;

    await page.route("**/api/external/privacy-tip", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          title: "Локальный совет по безопасности",
          content: "Проверяйте файлы перед публикацией.",
          source: "local-fallback",
          fetched_at: new Date().toISOString(),
          fallback: true,
        }),
      });
    });

    await page.route("**/api/auth/login", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          access_token: "mock-access-token",
          refresh_token: "mock-refresh-token",
          token_type: "bearer",
        }),
      });
    });

    await page.route("**/api/files/upload", async (route) => {
      await route.fulfill({
        status: 201,
        contentType: "application/json",
        body: JSON.stringify(uploadedFile),
      });
    });

    await page.route("**/api/files/1/process", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(processedFile),
      });
    });

    await page.route("**/api/files", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify([processedFile]),
      });
    });

    await page.route("**/api/files/1/download-url", async (route) => {
      downloadUrlRequested = true;
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          url: "http://localhost:9000/file-processor/processed/left-arrow_blured.png",
          filename: "left-arrow_blured.png",
          expires_in: 3600,
        }),
      });
    });

    await page.goto("/login");
    await page.getByPlaceholder("Введите логин").fill("e2e_user");
    await page.getByPlaceholder("Введите пароль").fill("password123");
    await page.getByRole("button", { name: "Войти" }).click();

    await expect(page).toHaveURL("/");

    await page.locator('input[type="file"]').setInputFiles("src/assets/left-arrow.png");
    await expect(page.getByText("left-arrow.png")).toBeVisible();

    await page.getByRole("button", { name: "Обработать" }).click();
    await expect(page.getByTitle("Скачать файл")).toBeVisible();

    await page.getByTitle("Скачать файл").click();
    await expect.poll(() => downloadUrlRequested).toBe(true);
  });
});
