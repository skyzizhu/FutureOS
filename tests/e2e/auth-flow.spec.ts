import { test, expect, type Page } from "@playwright/test";
async function mockSecurity(page: Page) {
  await page.route("**/api/auth-config", (r) =>
    r.fulfill({
      json: {
        schema_version: "1.0",
        email_code_length: 4,
        email_transport: "local_preview",
        turnstile_enabled: true,
        turnstile_site_key: "flow-ui-test-site",
        demo_admin_enabled: false,
      },
    }),
  );
  await page.route(
    "https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit",
    (r) =>
      r.fulfill({
        contentType: "application/javascript",
        body: `
  window.__flowScriptLoads=(window.__flowScriptLoads||0)+1;
  const roots=new Map();
  window.turnstile={render(element,options){
   window.__flowRenders=(window.__flowRenders||0)+1;
   window.__flowOptions={appearance:options.appearance,language:options.language,retry:options.retry};
   const id='flow-'+window.__flowRenders;roots.set(id,element);
   const pass=document.createElement('button');pass.type='button';pass.textContent='完成测试安全检查';pass.onclick=()=>options.callback('test-ui-token-'+id);element.appendChild(pass);
   const fail=document.createElement('button');fail.type='button';fail.textContent='模拟检查失败';fail.onclick=()=>options['error-callback']();element.appendChild(fail);
   return id;
  },remove(id){const root=roots.get(id);if(root)root.replaceChildren();roots.delete(id);}};
 `,
      }),
  );
}
async function renderCount(page: Page) {
  return page.evaluate(() => Number(Reflect.get(window, "__flowRenders") || 0));
}
async function fillEmailAndPassword(page: Page) {
  await page
    .getByLabel("邮箱", { exact: true })
    .fill("flow-ui@example.invalid");
  await page.getByLabel("密码", { exact: true }).fill("Test-ui-password-123!");
}

test("missing mail proof gives focused feedback; password visibility never mounts CAPTCHA", async ({
  page,
}) => {
  await mockSecurity(page);
  let requests = 0;
  await page.route("**/api/account/auth", (r) => {
    requests++;
    return r.fulfill({ status: 500, json: { code: "UNEXPECTED_REQUEST" } });
  });
  await page.goto("/auth/login");
  await fillEmailAndPassword(page);
  await expect(page.getByLabel("邮箱验证码", { exact: true })).toBeDisabled();
  await expect(page.getByLabel("密码", { exact: true })).toHaveAttribute(
    "type",
    "password",
  );
  await page.getByRole("button", { name: "显示密码", exact: true }).click();
  await expect(page.getByLabel("密码", { exact: true })).toHaveAttribute(
    "type",
    "text",
  );
  await page.getByRole("button", { name: "隐藏密码", exact: true }).click();
  await expect(page.getByLabel("密码", { exact: true })).toHaveAttribute(
    "type",
    "password",
  );
  await page.getByRole("button", { name: "注册并继续", exact: true }).click();
  await expect(
    page.getByRole("alert").filter({ hasText: "请先点击" }),
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: "发送邮箱验证码", exact: true }),
  ).toBeFocused();
  await page.getByRole("button", { name: "注册并继续", exact: true }).click();
  expect(await renderCount(page)).toBe(0);
  expect(requests).toBe(0);
});

test("one security check sends one email request; bad code and password edits never restart it", async ({
  page,
}) => {
  await mockSecurity(page);
  const sent: Record<string, unknown>[] = [];
  await page.route("**/api/account/auth", async (r) => {
    const data = r.request().postDataJSON();
    sent.push(data);
    if (data.action === "email-code")
      return r.fulfill({
        json: {
          challenge_id: "00000000-0000-4000-8000-000000000099",
          delivery_mode: "local_preview",
          expires_in: 300,
          resend_after: 60,
        },
      });
    return r.fulfill({
      status: 401,
      json: { code: "EMAIL_CODE_INVALID", message: "验证码无效或已过期" },
    });
  });
  await page.goto("/auth/login");
  await fillEmailAndPassword(page);
  expect(await renderCount(page)).toBe(0);
  await page
    .getByRole("button", { name: "发送邮箱验证码", exact: true })
    .click();
  await expect(
    page.getByRole("button", { name: "完成测试安全检查", exact: true }),
  ).toBeVisible();
  expect(await renderCount(page)).toBe(1);
  expect(sent).toHaveLength(0);
  await page.getByRole("button", { name: "显示密码", exact: true }).click();
  expect(await renderCount(page)).toBe(1);
  await page
    .getByRole("button", { name: "完成测试安全检查", exact: true })
    .click();
  await expect(
    page.getByRole("status").filter({ hasText: "本地预览" }),
  ).toBeVisible();
  expect(sent).toHaveLength(1);
  expect(sent[0].human_token).toContain("test-ui-token");
  await expect(
    page.getByRole("region", { name: "安全检查", exact: true }),
  ).toHaveCount(0);
  await page.getByLabel("邮箱验证码", { exact: true }).fill("1234");
  await page
    .getByLabel("密码", { exact: true })
    .fill("Edited-ui-password-123!");
  await page.getByRole("button", { name: "注册并继续", exact: true }).click();
  await expect(
    page.getByRole("alert").filter({ hasText: "验证码无效" }),
  ).toBeVisible();
  await expect(page.getByLabel("邮箱验证码", { exact: true })).toBeFocused();
  expect(await renderCount(page)).toBe(1);
  expect(sent).toHaveLength(2);
  expect(sent[1].action).toBe("register");
  await expect(page.getByRole("button", { name: /秒后可重发/ })).toBeDisabled();
  const options = await page.evaluate(() =>
    Reflect.get(window, "__flowOptions"),
  );
  expect(options).toEqual({
    appearance: "interaction-only",
    language: "zh-cn",
    retry: "never",
  });
});

test("normal login has no widget; a server risk response starts exactly one check", async ({
  page,
}) => {
  await mockSecurity(page);
  let requests = 0;
  await page.route("**/api/account/auth", (r) => {
    requests++;
    const human = r.request().postDataJSON().human_token;
    if (requests === 1 || human)
      return r.fulfill({
        status: 401,
        json: { code: "AUTH_REQUIRED", message: "邮箱或密码不匹配" },
      });
    return r.fulfill({
      status: 403,
      json: {
        code: "HUMAN_VERIFICATION_REQUIRED",
        message: "请先完成动态验证",
      },
    });
  });
  await page.goto("/auth/login");
  await page
    .getByRole("button", { name: "已有账号，去登录", exact: true })
    .click();
  await fillEmailAndPassword(page);
  await page.getByRole("button", { name: "登录", exact: true }).click();
  await expect(
    page.getByRole("alert").filter({ hasText: "邮箱或密码不匹配" }),
  ).toBeVisible();
  expect(await renderCount(page)).toBe(0);
  await page.getByRole("button", { name: "登录", exact: true }).click();
  await expect(
    page.getByRole("button", { name: "完成测试安全检查", exact: true }),
  ).toBeVisible();
  expect(await renderCount(page)).toBe(1);
  await page
    .getByRole("button", { name: "完成测试安全检查", exact: true })
    .click();
  await expect(
    page.getByRole("alert").filter({ hasText: "邮箱或密码不匹配" }),
  ).toBeVisible();
  expect(requests).toBe(3);
  expect(await renderCount(page)).toBe(1);
});

test("challenge errors and cancel stay still until a deliberate retry", async ({
  page,
}) => {
  await mockSecurity(page);
  let requests = 0;
  await page.route("**/api/account/auth", (r) => {
    requests++;
    return r.fulfill({ status: 500, json: { code: "UNEXPECTED_REQUEST" } });
  });
  await page.goto("/auth/login");
  await fillEmailAndPassword(page);
  await page
    .getByRole("button", { name: "发送邮箱验证码", exact: true })
    .click();
  await page.getByRole("button", { name: "模拟检查失败", exact: true }).click();
  await expect(
    page.getByRole("alert").filter({ hasText: "安全验证暂不可用" }),
  ).toBeVisible();
  expect(await renderCount(page)).toBe(1);
  expect(requests).toBe(0);
  await page
    .getByRole("button", { name: "发送邮箱验证码", exact: true })
    .click();
  await expect(
    page.getByRole("button", { name: "取消安全检查", exact: true }),
  ).toBeVisible();
  expect(await renderCount(page)).toBe(2);
  await page.getByRole("button", { name: "取消安全检查", exact: true }).click();
  await expect(
    page.getByRole("alert").filter({ hasText: "已取消" }),
  ).toBeVisible();
  expect(await renderCount(page)).toBe(2);
  expect(requests).toBe(0);
});

test("expired mail code needs explicit resend; changing mailbox clears the old proof", async ({
  page,
}) => {
  await page.clock.install();
  await mockSecurity(page);
  let sends = 0;
  await page.route("**/api/account/auth", (r) => {
    sends++;
    return r.fulfill({
      json: {
        challenge_id: "00000000-0000-4000-8000-000000000099",
        delivery_mode: "local_preview",
        expires_in: 2,
        resend_after: 1,
      },
    });
  });
  await page.goto("/auth/login");
  await fillEmailAndPassword(page);
  await page
    .getByRole("button", { name: "发送邮箱验证码", exact: true })
    .click();
  await page
    .getByRole("button", { name: "完成测试安全检查", exact: true })
    .click();
  await expect(page.getByLabel("邮箱验证码", { exact: true })).toBeEnabled();
  await page.clock.fastForward(3000);
  await expect(page.getByLabel("邮箱验证码", { exact: true })).toBeDisabled();
  expect(await renderCount(page)).toBe(1);
  expect(sends).toBe(1);
  await page.getByRole("button", { name: "注册并继续", exact: true }).click();
  await expect(
    page.getByRole("alert").filter({ hasText: "已过期" }),
  ).toBeVisible();
  expect(sends).toBe(1);
  expect(await renderCount(page)).toBe(1);
  await page
    .getByLabel("邮箱", { exact: true })
    .fill("different@example.invalid");
  await expect(page.getByLabel("邮箱验证码", { exact: true })).toBeDisabled();
  await expect(
    page.getByRole("button", { name: "发送邮箱验证码", exact: true }),
  ).toBeEnabled();
  await page
    .getByRole("button", { name: "发送邮箱验证码", exact: true })
    .click();
  await expect(
    page.getByRole("button", { name: "完成测试安全检查", exact: true }),
  ).toBeVisible();
  expect(await renderCount(page)).toBe(2);
});

test("mobile keyboard validation stays inline and does not spend another security token", async ({
  page,
}) => {
  await page.setViewportSize({ width: 375, height: 900 });
  await mockSecurity(page);
  let requests = 0;
  await page.route("**/api/account/auth", (r) => {
    requests++;
    return r.fulfill({
      json: {
        challenge_id: "00000000-0000-4000-8000-000000000099",
        delivery_mode: "local_preview",
        expires_in: 300,
        resend_after: 60,
      },
    });
  });
  await page.goto("/auth/login");
  await page.getByLabel("邮箱", { exact: true }).fill("invalid-address");
  await page
    .getByRole("button", { name: "发送邮箱验证码", exact: true })
    .click();
  await expect(
    page.getByRole("alert").filter({ hasText: "有效的邮箱" }),
  ).toBeVisible();
  await expect(page.getByLabel("邮箱", { exact: true })).toBeFocused();
  expect(await renderCount(page)).toBe(0);
  await page
    .getByLabel("邮箱", { exact: true })
    .fill("long-but-valid-mobile-address@example.invalid");
  await page
    .getByRole("button", { name: "发送邮箱验证码", exact: true })
    .click();
  await page
    .getByRole("button", { name: "完成测试安全检查", exact: true })
    .click();
  await page.getByLabel("邮箱验证码", { exact: true }).fill("1234");
  await page.getByLabel("密码", { exact: true }).fill("short");
  await page.getByLabel("密码", { exact: true }).press("Enter");
  await expect(
    page.getByRole("alert").filter({ hasText: "12–128" }),
  ).toBeVisible();
  await expect(page.getByLabel("密码", { exact: true })).toBeFocused();
  expect(requests).toBe(1);
  expect(await renderCount(page)).toBe(1);
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBe(true);
});

test("administrator password flow requests security verification only when the server requires it", async ({
  page,
}) => {
  await mockSecurity(page);
  let requests = 0;
  await page.route("**/api/admin/auth/login", (r) => {
    requests++;
    if (!r.request().postDataJSON().human_token)
      return r.fulfill({
        status: 403,
        json: {
          code: "HUMAN_VERIFICATION_REQUIRED",
          message: "请先完成动态验证",
        },
      });
    return r.fulfill({
      json: {
        stage: "verify",
        challenge_token: "synthetic-long-challenge-token-for-ui-test",
      },
    });
  });
  await page.goto("/admin/login");
  await page
    .getByLabel("管理员邮箱", { exact: true })
    .fill("test-admin@example.invalid");
  await page
    .getByLabel("管理员密码", { exact: true })
    .fill("Synthetic-admin-password-123!");
  expect(await renderCount(page)).toBe(0);
  await page.getByRole("button", { name: "显示密码", exact: true }).click();
  await expect(page.getByLabel("管理员密码", { exact: true })).toHaveAttribute(
    "type",
    "text",
  );
  await page
    .getByRole("button", { name: "验证管理员密码", exact: true })
    .click();
  await expect(
    page.getByRole("button", { name: "完成测试安全检查", exact: true }),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "完成测试安全检查", exact: true })
    .click();
  await expect(
    page.getByRole("heading", { name: "验证第二因素", exact: true }),
  ).toBeVisible();
  expect(requests).toBe(2);
  expect(await renderCount(page)).toBe(1);
});
