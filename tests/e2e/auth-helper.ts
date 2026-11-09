import { expect, type Page } from "@playwright/test";
import { execFileSync } from "node:child_process";
export async function fillRegistrationCode(page: Page) {
  const pending = page.waitForResponse(
    (r) =>
      r.url().endsWith("/api/account/auth") &&
      r.request().method() === "POST" &&
      r.request().postDataJSON()?.action === "email-code",
  );
  await page
    .getByRole("button", { name: "发送邮箱验证码", exact: true })
    .click();
  const response = await pending;
  expect(response.ok(), await response.text()).toBe(true);
  const data = await response.json();
  expect(data.delivery_mode).toBe("local_preview");
  const code = execFileSync(
    "uv",
    ["run", "python", "-m", "scripts.auth_mail_preview", data.challenge_id],
    { encoding: "utf8" },
  ).trim();
  expect(code).toMatch(/^\d{4}$/);
  await page.getByLabel("邮箱验证码", { exact: true }).fill(code);
}
