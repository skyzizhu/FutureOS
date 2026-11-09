import { chooseSelect } from "./control-helper";
import { test, expect } from "@playwright/test";
import { fillRegistrationCode } from "./auth-helper";

test("expanded profile hierarchy, manual state, demographics and understandable preferences", async ({
  page,
}) => {
  test.setTimeout(90000);
  await page.goto("/auth/login");
  await page
    .getByLabel("邮箱", { exact: true })
    .fill(`profile-ui-${Date.now()}@example.invalid`);
  await page
    .getByLabel("密码", { exact: true })
    .fill("Profile-ui-private-test-123!");
  await fillRegistrationCode(page);
  await page.getByRole("button", { name: "注册并继续", exact: true }).click();
  await chooseSelect(page.getByLabel("一级行业（必选）"), "technology");
  await expect(page.getByLabel("一级行业（必选）")).toContainText(
    "互联网与信息技术",
  );
  await chooseSelect(
    page.getByLabel("二级行业（必选）"),
    "technology_product_management",
  );
  await expect(page.getByLabel("二级行业（必选）")).toContainText("产品经理");
  await page.getByLabel("二级行业（必选）").click();
  await expect(
    page.getByRole("option", { name: "UI设计师", exact: true }),
  ).toBeVisible();
  await page.screenshot({
    animations: "disabled",
    path: "docs/milestones/evidence/profile-technology-roles.png",
  });
  await page.getByRole("option", { name: "UI设计师", exact: true }).click();
  await chooseSelect(page.getByLabel("一级行业（必选）"), "not_applicable");
  await expect(
    page.getByText("这是身份兜底选项", { exact: false }),
  ).toBeVisible();
  await chooseSelect(page.getByLabel("一级行业（必选）"), "technology");
  await chooseSelect(page.getByLabel("二级行业（必选）"), "software");
  await chooseSelect(page.getByLabel("一级行业（必选）"), "agriculture");
  await expect(page.getByLabel("二级行业（必选）")).toHaveAttribute(
    "data-value",
    "",
  );
  await expect(
    page.getByLabel("二级行业（必选）").locator('option[value="software"]'),
  ).toHaveCount(0);
  await chooseSelect(page.getByLabel("二级行业（必选）"), "agriculture_other");
  await page
    .getByLabel("你的细分行业", { exact: true })
    .fill("智慧农业机器人服务");
  await page
    .locator("summary")
    .filter({ hasText: "个性化资料（选填）" })
    .click();
  await chooseSelect(
    page.getByLabel("国家／地区（选填）", { exact: true }),
    "US",
  );
  await expect(
    page.getByRole("textbox", { name: "州（选填）", exact: true }),
  ).toBeEditable();
  await page.getByLabel("州（选填）", { exact: true }).fill("California");
  await chooseSelect(
    page.getByLabel("国家／地区（选填）", { exact: true }),
    "CN",
  );
  await expect(
    page.getByLabel("省／自治区／直辖市（选填）", { exact: true }),
  ).toHaveValue("");
  await chooseSelect(
    page.getByLabel("国家／地区（选填）", { exact: true }),
    "US",
  );
  await page.getByLabel("州（选填）", { exact: true }).fill("California");
  await chooseSelect(
    page.getByLabel("性别（选填）", { exact: true }),
    "female",
  );
  await page.getByLabel("年龄（选填）", { exact: true }).fill("28");
  await page
    .getByRole("checkbox", { name: "寻找职业机会", exact: true })
    .check();
  await page.getByText("进阶：定制行动建议（可跳过）", { exact: true }).click();
  await page
    .getByLabel("你希望重点关注的工作／业务", { exact: true })
    .fill("经营网店");
  await page.getByRole("button", { name: "添加工作内容", exact: true }).click();
  await chooseSelect(
    page.getByLabel("每周愿意花多久尝试新方法？", { exact: true }),
    "30",
  );
  await expect(page.getByText(/不影响报告生成速度/)).toBeVisible();
  await page
    .getByRole("checkbox", {
      name: "允许报告使用岗位、地区和关注偏好",
      exact: true,
    })
    .check();
  await page.getByRole("button", { name: "保存画像", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "我的未来观察", exact: true }),
  ).toBeVisible();
  const response = await page.request.get("/api/account/me/profile");
  expect(response.ok()).toBe(true);
  const profile = (await response.json()).profile;
  expect(profile).toMatchObject({
    industry_l1_code: "agriculture",
    industry_l2_code: "agriculture_other",
    industry_detail: "智慧农业机器人服务",
    country_code: "US",
    subdivision: "California",
    gender: "female",
    age: 28,
    available_minutes_per_week: 30,
  });
  expect(profile.goals).toContain("寻找职业机会");
  expect(profile.tasks).toEqual(["经营网店"]);
  await page.goto("/settings");
  await page
    .locator("summary")
    .filter({ hasText: "个性化资料（选填）" })
    .click();
  await expect(page.getByLabel("年龄（选填）", { exact: true })).toHaveValue(
    "28",
  );
  await expect(page.getByLabel("州（选填）", { exact: true })).toHaveValue(
    "California",
  );
  await page.setViewportSize({ width: 390, height: 844 });
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBe(true);
  await page
    .getByLabel("年龄（选填）", { exact: true })
    .scrollIntoViewIfNeeded();
  await page.screenshot({
    path: "docs/milestones/evidence/profile-mobile.png",
    fullPage: false,
  });
});
