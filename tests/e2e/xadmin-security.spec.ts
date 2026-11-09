import { chooseSelect } from "./control-helper";
import { test, expect, type Page } from "@playwright/test";
import { execFileSync } from "node:child_process";
import { readFileSync } from "node:fs";
function totp(secret: string) {
  return execFileSync(
    "uv",
    [
      "run",
      "python",
      "-c",
      "import pyotp,sys;print(pyotp.TOTP(sys.stdin.read().strip()).now())",
    ],
    { input: secret, encoding: "utf8" },
  ).trim();
}
async function enroll(page: Page) {
  await expect(
    page.getByRole("heading", { name: "绑定认证器", exact: true }),
  ).toBeVisible();
  const secret = await page
    .getByLabel("认证器密钥", { exact: true })
    .inputValue();
  await page.getByLabel("6位动态码", { exact: true }).fill(totp(secret));
  await page.getByRole("button", { name: "验证并继续", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "请保存一次性恢复码", exact: true }),
  ).toBeVisible();
  expect(
    (await page.getByLabel("恢复码", { exact: true }).textContent())
      ?.trim()
      .split("\n"),
  ).toHaveLength(10);
  await page
    .getByRole("button", { name: "我已保存，进入管理台", exact: true })
    .click();
}
test("controlled owner enrollment, MFA cookies, viewer authorization and server logout", async ({
  page,
  browser,
}) => {
  test.setTimeout(120000);
  // The native supervisor/CI points this entire browser suite at an isolated _test DB.
  execFileSync(
    "uv",
    [
      "run",
      "python",
      "-m",
      "scripts.admin_bootstrap",
      "--output",
      ".local/e2e/admin-bootstrap.token",
    ],
    { stdio: "pipe" },
  );
  const token = readFileSync(".local/e2e/admin-bootstrap.token", "utf8").trim();
  const password = "Admin-browser-fixture-password-123!";
  await page.goto("/admin/login");
  await page.getByRole("button", { name: "初始化管理员", exact: true }).click();
  await page.getByLabel("初始化凭证", { exact: true }).fill(token);
  await page
    .getByLabel("管理员邮箱", { exact: true })
    .fill("owner-browser@example.invalid");
  await page.getByLabel("管理员密码", { exact: true }).fill(password);
  await page
    .getByRole("button", { name: "创建所有者并绑定认证器", exact: true })
    .click();
  await expect(
    page.getByRole("heading", { name: "绑定认证器", exact: true }),
  ).toBeVisible();
  expect(
    (await page.context().cookies()).some((c) => c.name === "futureos_admin"),
  ).toBe(false);
  await enroll(page);
  const cookie = (await page.context().cookies()).find(
    (c) => c.name === "futureos_admin",
  );
  expect(cookie?.httpOnly).toBe(true);
  expect(cookie?.sameSite).toBe("Strict");
  await page.goto("/admin/security");
  await expect(page.getByRole("heading", { name: "用户注册与登录记录" })).toBeVisible();
  await expect(
    page.getByText("o***@example.invalid", { exact: false }).first(),
  ).toBeVisible();
  await page
    .getByLabel("新管理员邮箱", { exact: true })
    .fill("viewer-browser@example.invalid");
  await page.getByLabel("初始密码", { exact: true }).fill(password);
  await chooseSelect(page.getByLabel("权限组", { exact: true }), "viewer");
  await page
    .getByRole("button", { name: "创建管理员账号", exact: true })
    .click();
  await expect(page.getByRole("status")).toContainText("管理员已创建");
  const context = await browser.newContext();
  const viewer = await context.newPage();
  await viewer.goto("http://127.0.0.1:3100/admin/login");
  await viewer
    .getByLabel("管理员邮箱", { exact: true })
    .fill("viewer-browser@example.invalid");
  await viewer.getByLabel("管理员密码", { exact: true }).fill(password);
  await viewer
    .getByRole("button", { name: "验证管理员密码", exact: true })
    .click();
  await enroll(viewer);
  expect((await viewer.request.get("/api/admin/readiness")).status()).toBe(200);
  expect(
    (await viewer.request.get("/api/admin/security/admins")).status(),
  ).toBe(403);
  expect(
    (
      await viewer.request.post("/api/admin/research/demo-inputs", {
        headers: { Origin: "http://127.0.0.1:3100" },
      })
    ).status(),
  ).toBe(403);
  await context.close();
  await page.getByRole("button", { name: "退出管理会话", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "管理员安全登录", exact: true }),
  ).toBeVisible();
  expect(
    (await page.context().cookies()).some((c) => c.name === "futureos_admin"),
  ).toBe(false);
  expect(
    (
      await page.request.get("http://127.0.0.1:8100/api/v1/admin/readiness", {
        headers: { Authorization: `Bearer ${cookie?.value}` },
      })
    ).status(),
  ).toBe(401);
  await page.screenshot({
    path: "docs/milestones/evidence/account-security-admin-login.png",
    fullPage: true,
  });
});
