import { test, expect } from "@playwright/test";
import { writeFileSync, mkdirSync } from "node:fs";
test("login protection survives BFF and displays retry guidance", async ({
  page,
}) => {
  test.setTimeout(90000);
  const email = `auth-protection-${Date.now()}@example.invalid`;
  const password = "Wrong-test-password-123!";
  mkdirSync(".local", { recursive: true });
  writeFileSync(".local/auth-browser-fixture.json", JSON.stringify({ email }), {
    mode: 0o600,
  });
  let limited = false;
  for (let i = 0; i < 11; i++) {
    const response = await page.request.post("/api/account/auth", {
      headers: { Origin: "http://127.0.0.1:3100" },
      data: { action: "login", email, password },
    });
    if (response.status() === 429) {
      expect(Number(response.headers()["retry-after"])).toBeGreaterThan(0);
      expect(response.headers()["cache-control"]).toBe("no-store");
      expect((await response.json()).code).toBe("AUTH_RATE_LIMITED");
      limited = true;
      break;
    }
    expect(response.status(), await response.text()).toBe(401);
  }
  expect(limited).toBe(true);
  expect(
    (await page.context().cookies()).some((c) => c.name === "futureos_session"),
  ).toBe(false);
  await page.goto("/auth/login");
  await page
    .getByRole("button", { name: "已有账号，去登录", exact: true })
    .click();
  await page.getByLabel("邮箱", { exact: true }).fill(email);
  await page.getByLabel("密码", { exact: true }).fill(password);
  await page.getByRole("button", { name: "登录", exact: true }).click();
  await expect(
    page.getByRole("alert").filter({ hasText: "登录尝试过多" }),
  ).toContainText("秒后重试");
});
