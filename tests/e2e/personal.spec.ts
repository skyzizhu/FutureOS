import { chooseSelect } from "./control-helper";
import { fillRegistrationCode } from "./auth-helper";
import { test, expect } from "@playwright/test";
test("M4 registration, minimum profile, one free private report and consented local email", async ({
  page,
  browser,
}) => {
  test.setTimeout(120000);
  const email = `m4-browser-${Date.now()}@example.invalid`;
  const password = "M4-browser-private-test-123!";
  await page.goto("/dashboard");
  await expect(page.getByRole("heading", { name: "请先登录" })).toBeVisible();
  await page.getByRole("link", { name: "登录或注册" }).click();
  await page.getByLabel("邮箱", { exact: true }).fill(email);
  await page.getByLabel("密码", { exact: true }).fill(password);
  await page.route("**/api/account/auth", async (route) => {
    const response = await route.fetch();
    if (route.request().method() === "POST")
      expect(await response.text()).not.toContain("access_token");
    await route.fulfill({ response });
  });
  await fillRegistrationCode(page);
  await page.getByRole("button", { name: "注册并继续" }).click();
  await expect(
    page.getByRole("heading", { name: "先选与你相关的行业" }),
  ).toBeVisible();
  const cookie = (await page.context().cookies()).find(
    (c) => c.name === "futureos_session",
  );
  expect(cookie?.httpOnly).toBe(true);
  expect(cookie?.sameSite).toBe("Strict");
  const csrf = await page.request.put("/api/account/me/profile", {
    headers: { Origin: "http://evil.invalid" },
    data: { industry_l1_code: "technology", industry_l2_code: "software" },
  });
  expect(csrf.status()).toBe(403);
  await chooseSelect(page.getByLabel("一级行业（必选）"), "technology");
  await chooseSelect(page.getByLabel("二级行业（必选）"), "software");
  await page.getByRole("button", { name: "保存画像", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "我的未来观察" }),
  ).toBeVisible();
  await page.getByRole("tab", { name: "我的报告", exact: true }).click();
  await expect(
    page.getByText("可用 1 · 预留 0 · 已使用 0", { exact: true }),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "生成首份免费报告", exact: true })
    .click();
  await expect(
    page.getByRole("heading", {
      name: "个人未来观察报告（合成演示）",
      exact: true,
    }),
  ).toBeVisible({ timeout: 90000 });
  await expect(
    page.getByRole("heading", { name: "与你相关的变化" }),
  ).toBeVisible();
  await expect(page.getByText(/停止条件：/).first()).toBeVisible();
  const reportUrl = page.url();
  await page.getByRole("button", { name: "预览邮件摘要", exact: true }).click();
  await expect(
    page.getByRole("button", { name: "授权并模拟发送首次报告" }),
  ).toBeDisabled();
  await page.getByLabel("确认当前账号邮箱").fill(email);
  await page.getByRole("checkbox").check();
  await page.getByRole("button", { name: "授权并模拟发送首次报告" }).click();
  await expect(page.getByRole("status")).toContainText("未发送真实邮件");
  await page.screenshot({
    path: "docs/milestones/evidence/M4-private-report.png",
    fullPage: true,
  });
  await page
    .getByRole("link", { name: "查看固定预测版本、来源与历史案例" })
    .first()
    .click();
  await expect(
    page.getByRole("heading", { name: "支持证据与反证" }),
  ).toBeVisible();
  await expect(
    page.getByRole("heading", { name: "历史类比与失败案例" }),
  ).toBeVisible();
  await page.screenshot({
    path: "docs/milestones/evidence/M4-forecast.png",
    fullPage: true,
  });
  const stranger = await browser.newContext();
  const other = await stranger.newPage();
  await other.goto(reportUrl);
  await expect(other.getByRole("heading", { name: "请先登录" })).toBeVisible();
  await stranger.close();
  await page.goto("/dashboard");
  await page.getByRole("tab", { name: "我的报告", exact: true }).click();
  await expect(
    page.getByText("可用 0 · 预留 0 · 已使用 1", { exact: true }),
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: "生成首份免费报告", exact: true }),
  ).toBeDisabled();
  await page.getByRole("link", { name: "建议中心", exact: true }).click();
  await page
    .getByRole("button", { name: "不适用", exact: true })
    .first()
    .click();
  await expect(page.getByRole("status")).toContainText("反馈已保存");
  await page.goto("/settings");
  await page.getByRole("button", { name: "退出登录", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "欢迎使用 FutureOS" }),
  ).toBeVisible();
  await page.goto(reportUrl);
  await expect(page.getByRole("heading", { name: "请先登录" })).toBeVisible();
});
