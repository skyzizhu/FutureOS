import { chooseSelect } from "./control-helper";
import { fillRegistrationCode } from "./auth-helper";
import { test, expect } from "@playwright/test";
test("M6 local checkout, guided research, free original topic, periodic consent and refund", async ({
  page,
}) => {
  test.setTimeout(180000);
  const origin = "http://127.0.0.1:3100";
  // Persistent local DEMO worlds may retain a previous test's cooldown; isolate this fixture.
  await page.request.post("/api/admin/session", {
    headers: { Origin: origin },
    data: { token: "demo-admin-local-only" },
  });
  const demoMonitors = (
    await (await page.request.get("/api/admin/monitor/forecasts")).json()
  ).filter((f: { label: string }) => f.label === "DEMO");
  for (const monitor of demoMonitors) {
    const response = await page.request.put(
      `/api/admin/monitor/forecasts/${monitor.forecast_id}/policy`,
      {
        headers: { Origin: origin },
        data: { ...monitor.policy, cooldown_seconds: 0, max_daily_jobs: 100 },
      },
    );
    expect(response.ok()).toBe(true);
  }

  await page.goto("/auth/login");
  await page
    .getByLabel("邮箱", { exact: true })
    .fill(`m6-browser-${Date.now()}@example.invalid`);
  await page
    .getByLabel("密码", { exact: true })
    .fill("M6-browser-private-test-123!");
  await fillRegistrationCode(page);
  await page.getByRole("button", { name: "注册并继续" }).click();
  await chooseSelect(page.getByLabel("一级行业（必选）"), "technology");
  await chooseSelect(page.getByLabel("二级行业（必选）"), "software");
  await page.getByRole("button", { name: "保存画像", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "我的未来观察" }),
  ).toBeVisible();
  await page.goto("/billing");
  await chooseSelect(page.getByLabel("套餐", { exact: true }), "demo_monthly");
  await page
    .getByRole("checkbox", { name: "我知道这是本地沙盒模拟，不会真实扣款" })
    .check();
  await page.getByRole("button", { name: "创建模拟订单", exact: true }).click();
  await expect(
    page.getByRole("button", { name: "确认模拟付款", exact: true }),
  ).toBeVisible();
  await expect(page.getByText(/可用 0 · 预留 0 · 已消费 0/)).toBeVisible();
  await page.getByRole("button", { name: "确认模拟付款", exact: true }).click();
  await expect(page.getByText(/可用 10 · 预留 0 · 已消费 0/)).toBeVisible();
  const history = await (
    await page.request.get("/api/account/billing/history")
  ).json();
  const checkout = history.checkouts[0];
  const replay = await page.request.post(
    `/api/account/billing/checkouts/${checkout.checkout_id}/confirm`,
    { headers: { Origin: origin }, data: { explicit_sandbox_consent: true } },
  );
  expect(replay.ok()).toBe(true);
  expect(
    (await (await page.request.get("/api/account/billing/balance")).json())
      .available,
  ).toBe(10);
  await page.screenshot({
    path: "docs/milestones/evidence/M6-billing.png",
    fullPage: true,
  });
  await page.goto("/research");
  await page
    .getByRole("button", { name: "检查新主题范围与用量", exact: true })
    .click();
  await expect(
    page.getByRole("heading", { name: "这是新的研究范围", exact: true }),
  ).toBeVisible();
  await expect(page.getByText(/本次需要 1 份套餐额度/)).toBeVisible();
  await page
    .getByRole("checkbox", { name: "我已阅读并接受本次研究的范围与额度规则" })
    .check();
  await page.getByRole("button", { name: "确认提交研究", exact: true }).click();
  await expect(
    page.getByRole("heading", {
      name: "个人未来观察报告（合成演示）",
      exact: true,
    }),
  ).toBeVisible({ timeout: 90000 });
  expect(
    (await (await page.request.get("/api/account/billing/balance")).json())
      .consumed,
  ).toBe(1);
  expect(
    (await (await page.request.get("/api/account/me/entitlements")).json())
      .available,
  ).toBe(1);
  await page.goto("/research");
  await page
    .getByRole("button", { name: "检查新主题范围与用量", exact: true })
    .click();
  await expect(
    page.getByRole("heading", { name: "这是已完成的原主题，可免费复查" }),
  ).toBeVisible();
  await expect(page.getByText(/本次需要 0 份套餐额度/)).toBeVisible();
  await chooseSelect(
    page.getByLabel("使用的订阅", { exact: true }),
    history.subscriptions[0].id,
  );
  await page
    .getByRole("checkbox", {
      name: "我授权按所选订阅周期研究，每期使用1份套餐额度，与邮件偏好无关",
    })
    .check();
  await page
    .getByRole("button", { name: "授权开启周期研究", exact: true })
    .click();
  await expect(page.getByText(/周期研究已开启 · 下次/)).toBeVisible();
  await page.screenshot({
    path: "docs/milestones/evidence/M6-research.png",
    fullPage: true,
  });
  await page.goto("/notifications");
  await page.getByRole("button", { name: "关闭全部邮件", exact: true }).click();
  await expect(page.getByRole("status")).toContainText("已关闭全部邮件订阅");
  await page.goto("/research");
  await expect(page.getByText(/周期研究已开启 · 下次/)).toBeVisible();
  await page.getByRole("button", { name: "暂停周期研究", exact: true }).click();
  await expect(page.getByText("周期研究未开启", { exact: true })).toBeVisible();
  await page.goto("/billing");
  await page.getByRole("button", { name: "到期不续订", exact: true }).click();
  await expect(page.getByRole("status")).toContainText("已设置到期不续订");
  // Separate unused order demonstrates a refund without touching the used subscription.
  await chooseSelect(page.getByLabel("套餐", { exact: true }), "demo_pack");
  await page
    .getByRole("checkbox", { name: "我知道这是本地沙盒模拟，不会真实扣款" })
    .check();
  await page.getByRole("button", { name: "创建模拟订单", exact: true }).click();
  await page.getByRole("button", { name: "确认模拟付款", exact: true }).click();
  await expect(page.getByText(/可用 12 · 预留 0 · 已消费 1/)).toBeVisible();
  const unused = page
    .locator("article")
    .filter({
      has: page.getByRole("heading", {
        name: "沙盒研究包 · 已模拟付款",
        exact: true,
      }),
    });
  await unused
    .getByRole("button", { name: "模拟未使用订单退款", exact: true })
    .click();
  await expect(page.getByRole("status")).toContainText("未使用订单已模拟退款");
  await expect(page.getByText(/可用 9 · 预留 0 · 已消费 1/)).toBeVisible();
  await page.goto("/admin/costs");
  if (await page.getByLabel("管理员令牌").count()) {
    await page.getByLabel("管理员令牌").fill("demo-admin-local-only");
    await page.getByRole("button", { name: "进入工作台", exact: true }).click();
  }
  await expect(
    page.getByRole("heading", { name: "共享研究复用", exact: true }),
  ).toBeVisible();
  await expect(
    page.getByRole("heading", { name: "阶段观测", exact: true }),
  ).toBeVisible();
  await page.screenshot({
    path: "docs/milestones/evidence/M6-costs.png",
    fullPage: true,
  });

  for (const monitor of demoMonitors) {
    await page.request.put(
      `/api/admin/monitor/forecasts/${monitor.forecast_id}/policy`,
      { headers: { Origin: origin }, data: monitor.policy },
    );
  }
});
