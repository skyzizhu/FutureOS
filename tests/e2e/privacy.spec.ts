import { chooseSelect } from "./control-helper";
import { fillRegistrationCode } from "./auth-helper";
import { test, expect } from "@playwright/test";
test("M7 export, script text safety, reauthenticated erasure and honest readiness", async ({
  page,
}) => {
  test.setTimeout(120000);
  const email = `m7-browser-${Date.now()}@example.invalid`;
  const password = "M7-private-deletion-test-123!";
  await page.goto("/auth/login");
  await page.getByLabel("邮箱", { exact: true }).fill(email);
  await page.getByLabel("密码", { exact: true }).fill(password);
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
  ).toBeVisible({ timeout: 60000 });
  const reportUrl = page.url();
  await page.goto("/settings");
  const downloadPromise = page.waitForEvent("download");
  await page
    .getByRole("button", { name: "导出我的画像与报告", exact: true })
    .click();
  const download = await downloadPromise;
  expect(download.suggestedFilename()).toBe("futureos-private-export.json");
  await page.getByText("删除我的个人数据与本地账号", { exact: true }).click();
  await page.getByLabel("输入当前密码确认删除").fill(password);
  await page
    .getByRole("checkbox", { name: "我确认永久删除当前账号的个人数据" })
    .check();
  await page
    .getByRole("button", { name: "确认删除个人数据", exact: true })
    .click();
  await expect(
    page.getByRole("heading", { name: "个人数据已删除", exact: true }),
  ).toBeVisible();
  expect(
    (await page.context().cookies()).some((c) => c.name === "futureos_session"),
  ).toBe(false);
  await page.goto(reportUrl);
  await expect(
    page.getByRole("heading", { name: "请先登录", exact: true }),
  ).toBeVisible();
  await page.goto("/admin/readiness");
  await page.getByLabel("管理员令牌").fill("demo-admin-local-only");
  await page.getByRole("button", { name: "进入工作台", exact: true }).click();
  await expect(
    page.getByText("暂不批准生产发布", { exact: true }),
  ).toBeVisible();
  await page.screenshot({
    path: "docs/milestones/evidence/M7-readiness.png",
    fullPage: true,
  });
  const token = `m7-xss-${Date.now()}`;
  const source = await page.request.post("/api/admin/sources/ingest", {
    headers: { Origin: "http://127.0.0.1:3100" },
    data: {
      url: `https://example.invalid/${token}`,
      title: `<img src=x onerror="window.__m7xss=1">${token}`,
      publisher: "Own security fixture",
      source_type: "manual",
      availability_basis: "observed_now",
      content: "<script>window.__m7xss=1</script> synthetic source",
      usage_permission: "authorized_full",
      license_note: "Own synthetic security fixture",
      reliability_note: "Synthetic only",
      domain_tags: ["technology"],
      label: "DEMO",
      claims: [],
    },
  });
  expect(source.ok(), await source.text()).toBe(true);
  await page.goto("/admin/sources");
  await expect(
    page.getByText(`<img src=x onerror="window.__m7xss=1">${token}`, {
      exact: true,
    }),
  ).toBeVisible();
  expect(
    await page.evaluate(() => Reflect.get(window, "__m7xss")),
  ).toBeUndefined();
  const headers = (await page.request.get("/settings")).headers();
  expect(headers["x-content-type-options"]).toBe("nosniff");
  expect(headers["content-security-policy"]).toContain(
    "frame-ancestors 'none'",
  );
});
