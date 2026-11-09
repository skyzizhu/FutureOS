import { test, expect } from "@playwright/test";
test("M1 protected workbench, import and as-of view", async ({ page }) => {
  await page.goto("/admin/sources");
  await expect(page.getByRole("heading", { name: "管理员登录" })).toBeVisible();
  await expect(
    page.getByRole("button", { name: "导入来源", exact: true }),
  ).toHaveCount(0);
  await page.getByLabel("管理员令牌").fill("demo-user-local-only");
  await page.getByRole("button", { name: "进入工作台" }).click();
  await expect(
    page.getByText("管理员身份验证失败", { exact: true }),
  ).toContainText("管理员身份验证失败");
  await page.getByLabel("管理员令牌").fill("demo-admin-local-only");
  await page.getByRole("button", { name: "进入工作台" }).click();
  await expect(
    page.getByRole("heading", { name: "导入来源与证据" }),
  ).toBeVisible();
  await page.getByRole("button", { name: "导入来源", exact: true }).click();
  await expect(page.getByRole("status")).toContainText(/来源已导入|复用成功/);
  await expect(
    page.getByRole("heading", { name: "DEMO 合成资料", exact: true }),
  ).toBeVisible();
  await page
    .getByLabel("研究截止时间（带时区的 ISO 时间，可留空）")
    .fill("1900-01-01T00:00:00Z");
  await page.getByRole("button", { name: "刷新时间视图" }).click();
  await expect(
    page.getByText("此时间视图没有可获取的来源版本。", { exact: true }),
  ).toBeVisible();
  await page
    .getByLabel("研究截止时间（带时区的 ISO 时间，可留空）")
    .fill("2020-08-20T00:00:00Z");
  await page.getByRole("button", { name: "刷新时间视图" }).click();
  await expect(
    page.getByRole("heading", { name: "DEMO 合成资料", exact: true }),
  ).toBeVisible();
  await page.screenshot({
    path: "docs/milestones/evidence/M1-workbench.png",
    fullPage: true,
  });
  await page.getByRole("button", { name: "退出", exact: true }).click();
  await expect(page.getByRole("heading", { name: "管理员登录" })).toBeVisible();
});
