import { test, expect } from "@playwright/test";
test("M2 internal draft and offline replay", async ({ page }) => {
  await page.goto("/admin/research");
  await page.getByLabel("管理员令牌").fill("demo-admin-local-only");
  await page.getByRole("button", { name: "进入工作台" }).click();
  await expect(
    page.getByRole("heading", { name: "准备研究输入" }),
  ).toBeVisible();
  await page.getByRole("button", { name: "准备 DEMO 研究" }).click();
  await expect(page.getByLabel("研究输入 JSON")).toHaveValue(/DEMO/);
  await page.getByRole("button", { name: "创建内部草稿", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "内部原始草稿 A" }),
  ).toBeVisible({ timeout: 30000 });
  await expect(
    page.getByText("未审查 · 禁止正式发布", { exact: true }),
  ).toBeVisible();
  await expect(page.getByRole("heading", { name: "受阻路径" })).toBeVisible();
  await page.getByRole("button", { name: "离线重放草稿" }).click();
  await expect(page.getByRole("status")).toContainText("重放一致");
  await page.screenshot({
    path: "docs/milestones/evidence/M2-research.png",
    fullPage: true,
  });
});
