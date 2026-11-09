import { chooseSelect } from "./control-helper";
import { test, expect } from "@playwright/test";
test("M3 independent review, DEMO publication and honest unresolved evaluation", async ({
  page,
}) => {
  await page.goto("/admin/research");
  await page.getByLabel("管理员令牌").fill("demo-admin-local-only");
  await page.getByRole("button", { name: "进入工作台" }).click();
  await page.getByRole("button", { name: "准备 DEMO 研究" }).click();
  await page.getByRole("button", { name: "创建内部草稿", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "内部原始草稿 A" }),
  ).toBeVisible({ timeout: 30000 });
  await page.goto("/admin/review");
  await expect(
    page.getByRole("heading", { name: "独立审查与发布" }),
  ).toBeVisible();
  await expect(page.locator("#review-draft option")).not.toHaveCount(1);
  await chooseSelect(page.getByLabel("待审草稿"), { index: 1 });
  await expect(
    page.getByRole("button", { name: "发布通过审查的版本" }),
  ).toHaveCount(0);
  await page.getByRole("button", { name: "运行独立审查" }).click();
  await expect(page.getByRole("heading", { name: "审查与裁决" })).toBeVisible();
  await expect(
    page.getByText("annotate · 允许进入发布", { exact: true }),
  ).toBeVisible();
  await page.getByRole("button", { name: "发布通过审查的版本" }).click();
  await expect(page.getByRole("status")).toContainText("DEMO 版本");
  await page.getByRole("button", { name: "冻结评估协议" }).click();
  await expect(page.getByRole("status")).toContainText("评估协议已冻结");
  await expect(page.getByText(/状态：inconclusive/).first()).toBeVisible();
  await page
    .getByRole("button", { name: "检查到期，缺数据时登记待验证" })
    .first()
    .click();
  await expect(
    page.getByText(/状态：unresolved_due_to_data/).first(),
  ).toBeVisible();
  await page.screenshot({
    path: "docs/milestones/evidence/M3-review.png",
    fullPage: true,
  });
});
