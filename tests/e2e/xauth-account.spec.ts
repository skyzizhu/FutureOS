import { test, expect } from "@playwright/test";
import { execFileSync } from "node:child_process";
import { fillRegistrationCode } from "./auth-helper";
test("email verified registration, session list and code verified password change", async ({
  page,
}) => {
  test.setTimeout(120000);
  const email = `email-browser-${Date.now()}@example.invalid`;
  const original = "Original-browser-password-123!";
  const changed = "Changed-browser-password-123!";
  await page.goto("/auth/login");
  await page.getByLabel("邮箱", { exact: true }).fill(email);
  await page.getByLabel("密码", { exact: true }).fill(original);
  await fillRegistrationCode(page);
  await page.getByRole("button", { name: "注册并继续", exact: true }).click();
  await expect(page.getByLabel("一级行业（必选）")).toBeVisible();
  const identity = await page.request.get("/api/account/auth");
  expect((await identity.json()).email_verified).toBe(true);
  expect(
    (await page.context().cookies()).some(
      (cookie) => cookie.name === "futureos_auth_device" && cookie.httpOnly,
    ),
  ).toBe(true);
  await page.goto("/account/security");
  await expect(
    page.getByText("当前会话", { exact: false }).first(),
  ).toBeVisible();
  await page
    .getByRole("link", { name: "通过邮箱验证码修改密码", exact: true })
    .click();
  await expect(
    page.getByRole("heading", { name: "忘记或修改密码", exact: true }),
  ).toBeVisible();
  await page.getByLabel("邮箱", { exact: true }).fill(email);
  await page.getByLabel("新密码", { exact: true }).fill(changed);
  const pending = page.waitForResponse(
    (r) =>
      r.url().endsWith("/api/account/auth") &&
      r.request().method() === "POST" &&
      r.request().postDataJSON()?.action === "email-code",
  );
  await page
    .getByRole("button", { name: "发送邮箱验证码", exact: true })
    .click();
  const sent = await pending;
  expect(sent.ok(), await sent.text()).toBe(true);
  const data = await sent.json();
  const code = execFileSync(
    "uv",
    ["run", "python", "-m", "scripts.auth_mail_preview", data.challenge_id],
    { encoding: "utf8" },
  ).trim();
  await page.getByLabel("邮箱验证码", { exact: true }).fill(code);
  await page
    .getByRole("button", { name: "验证并修改密码", exact: true })
    .click();
  await expect(page.getByRole("status")).toContainText("所有旧会话已失效");
  expect(
    (await page.context().cookies()).some((c) => c.name === "futureos_session"),
  ).toBe(false);
  await page.getByLabel("邮箱", { exact: true }).fill(email);
  await page.getByLabel("密码", { exact: true }).fill(changed);
  await page.getByRole("button", { name: "登录", exact: true }).click();
  await expect(page).toHaveURL(/\/dashboard/);
  const exported = await page.request.get("/api/account/me/export");
  expect(exported.ok()).toBe(true);
  const events: { action: string; fingerprint: string; fingerprint_kind: string }[] =
    (await exported.json()).auth_access_events;
  expect(events.map((event) => event.action).sort()).toEqual(["login", "register"]);
  expect(events.every((event) => event.fingerprint_kind === "browser")).toBe(true);
  expect(new Set(events.map((event) => event.fingerprint)).size).toBe(1);
  const oversized = await page.request.post("/api/account/auth", {
    headers: { Origin: new URL(page.url()).origin },
    data: { action: "login", padding: "大".repeat(1800) },
  });
  expect(oversized.status()).toBe(413);
});
