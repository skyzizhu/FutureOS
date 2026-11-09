import { chooseSelect } from "./control-helper";
import { fillRegistrationCode } from "./auth-helper";
import { test, expect } from "@playwright/test";
test("M5 shared monitor publishes, private update is free, consented local mail unsubscribes", async ({
  page,
}) => {
  test.setTimeout(180000);
  const origin = "http://127.0.0.1:3100";
  await page.goto("/auth/login");
  await page
    .getByLabel("邮箱", { exact: true })
    .fill(`m5-browser-${Date.now()}@example.invalid`);
  await page
    .getByLabel("密码", { exact: true })
    .fill("M5-browser-private-test-123!");
  await fillRegistrationCode(page);
  await page.getByRole("button", { name: "注册并继续" }).click();
  await chooseSelect(page.getByLabel("一级行业（必选）"), "technology");
  await chooseSelect(page.getByLabel("二级行业（必选）"), "software");
  await page.getByRole("button", { name: "保存画像", exact: true }).click();
  await page.getByRole("tab", { name: "我的报告", exact: true }).click();
  await page
    .getByRole("button", { name: "生成首份免费报告", exact: true })
    .click();
  await expect(
    page.getByRole("heading", {
      name: "个人未来观察报告（合成演示）",
      exact: true,
    }),
  ).toBeVisible({ timeout: 90000 });
  const reportId = new URL(page.url()).pathname.split("/").pop();
  const report = await (
    await page.request.get(`/api/account/reports/${reportId}`)
  ).json();
  await page.goto("/admin/monitor");
  await page.getByLabel("管理员令牌").fill("demo-admin-local-only");
  await page.getByRole("button", { name: "进入工作台" }).click();
  await expect(page.getByLabel("选择跟踪主题")).toBeVisible();
  const version = await (
    await page.request.get(
      `/api/account/forecasts/versions/${report.forecast_version_ids[0]}`,
    )
  ).json();
  const forecastId = version.version.forecast_id;
  const policy = await page.request.put(
    `/api/admin/monitor/forecasts/${forecastId}/policy`,
    {
      headers: { Origin: origin },
      data: { cooldown_seconds: 0, max_daily_jobs: 100 },
    },
  );
  expect(policy.ok(), await policy.text()).toBe(true);
  await chooseSelect(page.getByLabel("选择跟踪主题"), forecastId);
  await page.getByRole("button", { name: "加入 DEMO 变化并复查" }).click();
  await expect(page.getByText(/结果：published/).first()).toBeVisible({
    timeout: 60000,
  });
  await page.screenshot({
    path: "docs/milestones/evidence/M5-monitor.png",
    fullPage: true,
  });
  await page.goto("/notifications");
  await expect(async () => {
    await page.getByRole("button", { name: "刷新通知", exact: true }).click();
    await expect(
      page.getByRole("link", { name: "查看本次更新的固定报告版本" }).first(),
    ).toBeVisible();
  }).toPass({ timeout: 60000 });
  await page
    .getByRole("link", { name: "查看本次更新的固定报告版本" })
    .first()
    .click();
  await expect(
    page.getByRole("heading", { name: "本次更新说明" }),
  ).toBeVisible();
  const frozen = await (
    await page.request.get(
      `/api/account/reports/${reportId}/versions/${report.report_version_id}`,
    )
  ).json();
  expect(frozen).toEqual(report);
  const credit = await (
    await page.request.get("/api/account/me/entitlements")
  ).json();
  expect(credit.consumed).toBe(1);
  await page.goto("/notifications");
  await page.getByRole("checkbox", { name: "首次报告", exact: true }).check();
  await page
    .getByRole("checkbox", { name: "我明确同意按以上偏好接收报告邮件" })
    .check();
  await page.getByRole("button", { name: "保存邮件偏好" }).click();
  await expect(page.getByRole("status")).toContainText("邮件偏好已保存");
  await page.getByRole("button", { name: "确认模拟投递首份报告" }).click();
  await expect(page.getByRole("status")).toContainText(
    /模拟投递队列|复用原投递记录/,
  );
  await expect(async () => {
    const rows = await (
      await page.request.get("/api/account/me/mail-deliveries")
    ).json();
    expect(
      rows.some((r: { status: string }) => r.status === "delivered_local"),
    ).toBe(true);
  }).toPass({ timeout: 30000 });
  await page.getByRole("button", { name: "刷新通知", exact: true }).click();
  await page.getByRole("button", { name: "预览本地邮件" }).first().click();
  await page.screenshot({
    path: "docs/milestones/evidence/M5-notifications.png",
    fullPage: true,
  });
  await page.getByRole("link", { name: "退订邮件", exact: true }).click();
  await page.getByRole("button", { name: "确认退订全部邮件" }).click();
  await expect(page.getByRole("status")).toContainText("退订成功");
  const prefs = await (
    await page.request.get("/api/account/me/notification-preferences")
  ).json();
  expect(prefs.first_report_opt_in).toBe(false);
});
