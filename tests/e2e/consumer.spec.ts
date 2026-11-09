import { chooseSelect } from "./control-helper";
import { test, expect } from "@playwright/test";
import { fillRegistrationCode } from "./auth-helper";

test("public discovery, industry browsing, search and mobile navigation", async ({
  page,
}) => {
  await page.setViewportSize({ width: 1440, height: 1024 });
  const standaloneResponse = page.waitForResponse((response) =>
    new URL(response.url()).searchParams.get("standalone") === "true",
  );
  await page.goto("/");
  expect(await (await standaloneResponse).json()).toEqual([]);
  const primaryNav = page.getByRole("navigation", { name: "主导航" });
  await expect(page.getByRole("link", { name: "FutureOS 首页" })).toBeVisible();
  await expect(page).toHaveTitle("FutureOS · 预见未来趋势，做更好的决定。");
  await expect(
    primaryNav.getByRole("link", { name: "发现", exact: true }),
  ).toHaveAttribute("aria-current", "page");
  await expect(
    page.getByRole("heading", { name: "预测行业未来，发现下一次机遇。" }),
  ).toBeVisible();
  for (const name of ["公开行业", "行业报告"]) {
    await expect(page.getByRole("region", { name, exact: true })).toBeVisible();
  }
  await expect(
    page.getByRole("region", { name: "独立公开报告", exact: true }),
  ).toHaveCount(0);
  const questionEntry = page.getByRole("textbox", {
    name: "你想研究的问题",
    exact: true,
  });
  await expect(questionEntry).toBeInViewport();
  const chatHero = page.getByRole("region", {
    name: "预测行业未来，发现下一次机遇。",
  });
  await expect(chatHero.getByRole("button")).toHaveCount(1);
  await expect(chatHero.getByRole("link")).toHaveCount(0);
  await expect(chatHero.getByText(/实时监听与邮件提醒待启用/)).toHaveCount(0);
  const chatPosition = await questionEntry.boundingBox();
  const industryPosition = await page
    .getByRole("heading", { name: "人工智能", exact: true })
    .boundingBox();
  expect(chatPosition!.y).toBeLessThan(industryPosition!.y);
  await expect(
    page.getByRole("heading", { name: "人工智能", exact: true }),
  ).toBeVisible();
  const carousel = page.getByRole("region", { name: "探索行业" });
  const rail = carousel.getByRole("group", { name: /行业 Banner/ });
  await expect(
    rail.getByRole("button", { name: "添加到我的行业", exact: true }),
  ).toBeVisible();
  await carousel.getByRole("button", { name: "下一个行业" }).click();
  await expect(carousel.getByRole("heading", { name: "新能源" })).toBeVisible();
  await expect(questionEntry).toHaveAttribute("placeholder", /新能源/);
  await expect(
    rail
      .getByRole("group", { name: /^2 \/ / })
      .getByRole("button", { name: "添加到我的行业", exact: true }),
  ).toBeVisible();
  await expect(
    page
      .getByRole("link")
      .filter({ hasText: "理解新能源变化，可以从哪些问题开始？" }),
  ).toBeVisible();
  await rail.focus();
  await page.keyboard.press("ArrowLeft");
  await expect(
    carousel.getByRole("heading", { name: "人工智能" }),
  ).toBeVisible();
  const viewport = (await rail.boundingBox())!;
  await page.mouse.move(viewport.x + viewport.width / 2, viewport.y + 50);
  await page.mouse.down();
  await page.mouse.move(
    viewport.x + viewport.width / 2 - 170,
    viewport.y + 50,
    {
      steps: 8,
    },
  );
  await page.mouse.up();
  await expect(carousel.getByRole("heading", { name: "新能源" })).toBeVisible();
  await carousel.getByRole("button", { name: "上一个行业" }).click();
  await expect(
    carousel.getByRole("heading", { name: "人工智能" }),
  ).toBeVisible();
  await expect(
    page.getByRole("link").filter({ hasText: "AI 编程，会怎样改变软件开发？" }),
  ).toBeVisible();
  await expect(
    page.getByRole("link", { name: "管理", exact: true }),
  ).toHaveCount(0);
  await page.getByRole("link", { name: "搜索公开报告", exact: true }).click();
  await expect(
    page.getByRole("searchbox", { name: "搜索公开报告", exact: true }),
  ).toBeFocused();
  const searchbox = page.getByRole("searchbox", {
    name: "搜索公开报告",
    exact: true,
  });
  await searchbox.fill("理解新能源变化");
  await expect(
    page.getByRole("link").filter({ hasText: "理解新能源变化，可以从哪些问题开始？" }),
  ).toBeVisible();
  await searchbox.fill("不存在的测试报告");
  await expect(
    page.getByRole("heading", { name: "没有找到相关报告" }),
  ).toBeVisible();
  await searchbox.fill("");
  await expect(
    page.getByRole("link").filter({ hasText: "AI 编程，会怎样改变软件开发？" }),
  ).toBeVisible();
  await searchbox.blur();
  await page.screenshot({
    path: "docs/milestones/evidence/consumer-home-desktop.png",
    fullPage: true,
  });
  const reportLink = page
    .getByRole("link")
    .filter({ hasText: "AI 编程，会怎样改变软件开发？" });
  await expect(reportLink.getByText(/\d+ 次阅读/)).toBeVisible();
  await expect(reportLink.getByText(/\d+ 人收藏/)).toBeVisible();
  const recorded = page.waitForResponse(
    (r) => r.url().endsWith("/read") && r.request().method() === "POST",
  );
  await page
    .getByRole("link")
    .filter({ hasText: "AI 编程，会怎样改变软件开发？" })
    .click();
  const firstRead = await (await recorded).json();
  await expect(
    page.getByText(`${firstRead.views_count} 次阅读`, { exact: true }),
  ).toBeVisible();
  const replayed = page.waitForResponse(
    (r) => r.url().endsWith("/read") && r.request().method() === "POST",
  );
  await page.reload();
  expect((await (await replayed).json()).views_count).toBe(
    firstRead.views_count,
  );

  await expect(
    page.getByRole("heading", { name: "这是一份阅读示例" }),
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: "收藏报告", exact: true }),
  ).toBeVisible();
  await page.getByRole("button", { name: "收藏报告", exact: true }).click();
  await expect(page).toHaveURL(/auth\/login\?mode=login&next=/);
  await expect(
    page.getByRole("heading", { name: "欢迎回来", exact: true }),
  ).toBeVisible();
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  await expect(
    page.getByRole("heading", { name: "人工智能", exact: true }),
  ).toBeVisible();
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBe(true);
  await expect(questionEntry).toBeInViewport();
  await questionEntry.fill("未来有哪些值得关注的行业机会？");
  await page.getByRole("button", { name: "开始研究对话", exact: true }).click();
  await expect(page).toHaveURL(/\/chat\?industry=.*question=/);
  await expect(
    page.getByRole("heading", {
      name: "你的问题，值得好好研究。",
      exact: true,
    }),
  ).toBeVisible();
  await page.goto("/");
  await page.setViewportSize({ width: 360, height: 844 });
  await expect(
    page.getByRole("banner").getByRole("link", { name: "注册", exact: true }),
  ).toBeVisible();
  expect(
    await page.evaluate(() => {
      const brand = document
        .querySelector(".site-brand")!
        .getBoundingClientRect();
      const actions = document
        .querySelector(".site-header-actions")!
        .getBoundingClientRect();
      return brand.right <= actions.left;
    }),
  ).toBe(true);
  await page.setViewportSize({ width: 390, height: 844 });
  const mobileToggle = page.getByRole("button", {
    name: "展开导航",
    exact: true,
  });
  await mobileToggle.focus();
  await page.keyboard.press("Enter");
  await expect(
    primaryNav.getByRole("link", { name: "发现", exact: true }),
  ).toBeFocused();
  await page.keyboard.press("Escape");
  await expect(mobileToggle).toBeFocused();
  await expect(mobileToggle).toHaveAttribute("aria-expanded", "false");
  await mobileToggle.click();
  await page.mouse.click(5, 300);
  await expect(mobileToggle).toHaveAttribute("aria-expanded", "false");
  await mobileToggle.click();
  await primaryNav.getByRole("link", { name: "行业", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "每个行业，都有值得追问的未来。" }),
  ).toBeVisible();
  await page.screenshot({
    path: "docs/milestones/evidence/consumer-industries-mobile.png",
    fullPage: true,
  });
});

test("consumer collection, encrypted chat recovery, report preview sharing and withdrawal", async ({
  page,
  browser,
}) => {
  test.setTimeout(150000);
  await page.goto("/auth/login");
  await page
    .getByLabel("邮箱", { exact: true })
    .fill(`consumer-${Date.now()}@example.invalid`);
  await page
    .getByLabel("密码", { exact: true })
    .fill("Consumer-local-test-123!");
  await fillRegistrationCode(page);
  await page.getByRole("button", { name: "注册并继续", exact: true }).click();
  await chooseSelect(page.getByLabel("一级行业（必选）"), "technology");
  await chooseSelect(page.getByLabel("二级行业（必选）"), "software");
  await page.getByRole("button", { name: "保存画像", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "我的未来观察" }),
  ).toBeVisible();
  const accountMenu = page.getByRole("button", { name: "账号菜单" });
  await accountMenu.click();
  await expect(
    page.getByRole("banner").getByRole("link", { name: "账号安全" }),
  ).toBeVisible();
  await page.keyboard.press("Escape");
  await expect(accountMenu).toBeFocused();
  await expect(
    page.getByRole("link", { name: "软件开发", exact: true }),
  ).toBeVisible();
  await page.getByRole("button", { name: "添加行业", exact: true }).click();
  await page.getByLabel("行业名称", { exact: true }).fill("AI 教育观察");
  await page
    .getByLabel("我想关注什么", { exact: true })
    .fill("观察教学工具与学习方式的变化。");
  await page.getByRole("button", { name: "创建行业", exact: true }).click();
  await expect(page.getByRole("status")).toContainText("默认仅自己可见");
  await page.getByRole("link", { name: "AI 教育观察", exact: true }).click();
  await page.getByRole("button", { name: "公开这个行业", exact: true }).click();
  await page.getByRole("button", { name: "确认公开", exact: true }).click();
  await expect(page.getByRole("status")).toContainText("公开设置已更新");
  await page.goto("/");
  await page
    .getByRole("button", { name: "添加到我的行业", exact: true })
    .click();
  await expect(
    page.getByRole("button", { name: "已添加到我的行业", exact: true }),
  ).toBeVisible();
  await page.getByRole("button", { name: "为你推荐", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "为你推荐的公开报告", exact: true }),
  ).toBeVisible();
  await page.getByRole("button", { name: "返回行业报告", exact: true }).click();
  await page
    .getByRole("link")
    .filter({ hasText: "AI 编程，会怎样改变软件开发？" })
    .click();
  await page.getByRole("button", { name: "收藏报告", exact: true }).click();
  await expect(
    page.getByRole("button", { name: "已收藏", exact: true }),
  ).toBeVisible();
  await page.getByRole("link", { name: "研究这个行业", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "你的问题，值得好好研究。" }),
  ).toBeVisible();
  await page.getByRole("button", { name: "发送问题", exact: true }).click();
  await expect(
    page.getByText("私有研究对话 · 自动保存", { exact: true }),
  ).toBeVisible();
  const chatUrl = page.url();
  await page
    .getByLabel("继续补充研究问题", { exact: true })
    .fill("我想先了解国内的软件开发行业");
  await page.getByRole("button", { name: "发送问题", exact: true }).click();
  await expect(
    page.getByText("我想先了解国内的软件开发行业", { exact: true }),
  ).toBeVisible();
  await page.reload();
  await expect(
    page.getByText("我想先了解国内的软件开发行业", { exact: true }),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "查看本次研究范围", exact: true })
    .click();
  await page
    .getByRole("checkbox", {
      name: "我了解本次使用演示资料，不会执行新的联网搜索。",
      exact: true,
    })
    .check();
  await page.getByRole("button", { name: "生成演示报告", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "这次报告已完成", exact: true }),
  ).toBeVisible({ timeout: 60000 });
  await page.screenshot({
    path: "docs/milestones/evidence/consumer-chat-desktop.png",
    fullPage: true,
  });
  await page.getByRole("link").filter({ hasText: "你的行业观察报告" }).click();
  await expect(page).toHaveURL(/\/reports\/[a-f0-9-]+$/);
  const privateReportUrl = page.url();
  await page.getByRole("button", { name: "公开报告", exact: true }).click();
  await page.getByRole("button", { name: "预览公开内容", exact: true }).click();
  await expect(
    page.getByRole("button", { name: "确认公开", exact: true }),
  ).toBeDisabled();
  await page
    .getByRole("checkbox", {
      name: "我已检查预览，愿意让其他人无需登录即可阅读以上内容。",
      exact: true,
    })
    .check();
  await page.getByRole("button", { name: "确认公开", exact: true }).click();
  await page.getByRole("link", { name: "查看公开报告", exact: true }).click();
  await expect(page).toHaveURL(/\/community\/reports\/[a-f0-9-]+$/);
  const sharedUrl = page.url();
  const readerContext = await browser.newContext();
  const reader = await readerContext.newPage();
  await reader.goto("/auth/login");
  await reader
    .getByLabel("邮箱", { exact: true })
    .fill(`social-reader-${Date.now()}@example.invalid`);
  await reader
    .getByLabel("密码", { exact: true })
    .fill("Social-reader-private-123!");
  await fillRegistrationCode(reader);
  await reader.getByRole("button", { name: "注册并继续", exact: true }).click();
  await expect(reader).toHaveURL(/onboarding/);
  await reader.goto(sharedUrl);
  await reader.getByRole("button", { name: "点赞报告", exact: true }).click();
  await expect(
    reader.getByRole("button", { name: "已点赞", exact: true }),
  ).toBeVisible();
  await reader.getByRole("button", { name: "收藏报告", exact: true }).click();
  await expect(
    reader.getByRole("button", { name: "已收藏", exact: true }),
  ).toBeVisible();
  const downloadEvent = reader.waitForEvent("download");
  await reader.getByRole("button", { name: "下载报告", exact: true }).click();
  const download = await downloadEvent;
  expect(download.suggestedFilename()).toMatch(/futureos-.*\.md$/);
  expect(await download.failure()).toBeNull();
  await chooseSelect(reader.getByLabel("主题模式"), "dark");
  await expect(reader.locator("html")).toHaveAttribute("data-theme", "dark");
  await expect
    .poll(
      async () =>
        (await (await reader.request.get("/api/account/me/preferences")).json())
          .theme,
    )
    .toBe("dark");
  await reader.reload();
  await expect(reader.locator("html")).toHaveAttribute("data-theme", "dark");
  await reader.screenshot({
    animations: "disabled",
    path: "docs/milestones/evidence/social/report-dark.png",
    fullPage: true,
  });
  await reader.goto("/dashboard");
  await reader.getByRole("link", { name: "人工智能", exact: true }).click();
  await expect(
    reader.getByRole("switch", { name: "重要建议邮件提醒", exact: true }),
  ).not.toBeChecked();
  await reader
    .getByRole("switch", { name: "重要建议邮件提醒", exact: true })
    .check();
  await expect(
    reader.getByRole("switch", { name: "重要建议邮件提醒", exact: true }),
  ).toBeChecked();
  await expect(
    reader.getByRole("switch", { name: "重要建议邮件提醒", exact: true }),
  ).toBeEnabled();
  await reader.reload();
  await reader.getByRole("link", { name: "人工智能", exact: true }).click();
  await expect(
    reader.getByRole("switch", { name: "重要建议邮件提醒", exact: true }),
  ).toBeChecked();
  await expect(
    reader.getByText("实时执行等待抓取与提醒规则配置。", { exact: false }),
  ).toBeVisible();
  await reader.setViewportSize({ width: 390, height: 844 });
  expect(
    await reader.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
  await reader.screenshot({
    animations: "disabled",
    path: "docs/milestones/evidence/social/industry-mobile-dark.png",
    fullPage: true,
  });
  await page.goto("/notifications");
  await expect(
    page.getByRole("heading", { name: "互动消息", exact: true }),
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: "标记互动已读", exact: true }),
  ).toHaveCount(2);
  await page
    .getByRole("button", { name: "标记互动已读", exact: true })
    .first()
    .click();
  await expect(
    page.getByRole("button", { name: "标记互动已读", exact: true }),
  ).toHaveCount(1);
  await readerContext.close();
  const guestContext = await browser.newContext();
  const guest = await guestContext.newPage();
  await guest.goto(sharedUrl);
  await expect(
    guest.getByRole("heading", { name: "行业观察", exact: true }).first(),
  ).toBeVisible();
  await page.goto("/dashboard");
  await page.getByRole("tab", { name: "我的公开内容", exact: true }).click();
  await page.getByRole("button", { name: "撤回公开", exact: true }).click();
  await expect(page.getByRole("status")).toContainText("公开已撤回");
  await guest.reload();
  await expect(
    guest.getByRole("heading", { name: "这份报告暂时无法查看", exact: true }),
  ).toBeVisible();
  await page.goto(privateReportUrl);
  await page.getByRole("button", { name: "公开报告", exact: true }).click();
  await chooseSelect(page.getByLabel("公开位置"), "standalone");
  await page.getByRole("button", { name: "预览公开内容", exact: true }).click();
  await page
    .getByRole("checkbox", {
      name: "我已检查预览，愿意让其他人无需登录即可阅读以上内容。",
    })
    .check();
  await page.getByRole("button", { name: "确认公开", exact: true }).click();
  await expect(
    page.getByRole("link", { name: "查看公开报告", exact: true }),
  ).toBeVisible();
  await guest.goto("/");
  const standalone = guest.getByRole("region", {
    name: "独立公开报告",
    exact: true,
  });
  await standalone.getByRole("link").first().click();
  await expect(
    guest.getByRole("link", { name: "返回独立公开报告" }),
  ).toBeVisible();
  await guestContext.close();
  await page.goto(chatUrl);
  await expect(
    page.getByRole("heading", { name: "这次报告已完成", exact: true }),
  ).toBeVisible();
  await page.goto("/chat");
  await page.getByLabel("你想研究什么").fill("帮我添加商业航天行业");
  await page.getByRole("button", { name: "发送问题", exact: true }).click();
  const addIndustry = page.getByRole("button", { name: "确认添加到我的行业" });
  await expect(addIndustry).toBeVisible();
  await addIndustry.click();
  await expect(page.getByRole("status")).toHaveText("已添加到我的行业");
  const research = page.getByRole("region", { name: "行业研究任务" });
  await research.getByRole("button", { name: "选择研究范围" }).click();
  await research.getByRole("combobox", { name: "研究行业" }).click();
  await page.getByRole("option", { name: "商业航天", exact: true }).click();
  await research
    .getByRole("button", { name: "确认并运行行业研究演示" })
    .click();
  await expect(research.getByText("研究已结束")).toBeVisible({
    timeout: 30000,
  });
  await page.reload();
  await expect(page.getByRole("status")).toHaveText("已添加到我的行业");
  await expect(
    research.getByRole("list", { name: "实际执行阶段" }),
  ).toContainText("分析与补证");
  await research.getByRole("button", { name: "查看研究结果" }).click();
  await expect(research.getByText("DEMO · 研究草稿")).toBeVisible();
  await page.goto("/dashboard");
  await expect(
    page.getByRole("link", { name: "商业航天", exact: true }),
  ).toBeVisible();
});
