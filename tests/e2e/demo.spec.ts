import { test, expect } from "@playwright/test";
test("public discovery and separate administration shell", async ({ page }) => {
  await page.goto("/");
  await expect(
    page.getByRole("heading", { name: "预测行业未来，发现下一次机遇。" }),
  ).toBeVisible();
  await expect(
    page.getByRole("link", { name: "管理", exact: true }),
  ).toHaveCount(0);
  await expect(
    page.getByRole("button", { name: "添加到我的行业", exact: true }),
  ).toBeVisible();
  await page.getByRole("link", { name: "登录", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "欢迎使用 FutureOS" }),
  ).toBeVisible();
  await page.goto("/admin");
  await expect(page.getByText(/API 就绪/)).toBeVisible();
});
