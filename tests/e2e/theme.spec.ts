import { test, expect } from "@playwright/test";
import { chooseSelect } from "./control-helper";

test("theme follows OS, explicit appearance persists, controls support keyboard on mobile", async ({
  page,
}) => {
  await page.emulateMedia({ colorScheme: "dark" });
  await page.goto("/");
  await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
  await expect(page.locator("html")).toHaveAttribute(
    "data-theme-mode",
    "system",
  );
  await page.emulateMedia({ colorScheme: "light" });
  await expect(page.locator("html")).toHaveAttribute("data-theme", "light");
  await chooseSelect(page.getByLabel("主题模式"), "dark");
  await page.reload();
  await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
  await page.screenshot({
    animations: "disabled",
    path: "docs/milestones/evidence/social/home-dark.png",
    fullPage: true,
  });
  await page.setViewportSize({ width: 390, height: 844 });
  await page.getByLabel("主题模式").focus();
  await page.keyboard.press("Enter");
  await page.getByRole("option", { name: "浅色", exact: true }).focus();
  await page.keyboard.press("Enter");
  await expect(page.locator("html")).toHaveAttribute("data-theme", "light");
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
  await chooseSelect(page.getByLabel("主题模式"), "system");
  await page.emulateMedia({ colorScheme: "dark" });
  await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
});
