import type { Locator } from "@playwright/test";
// Exercise the visible packaged control; admin surfaces still use native selects.
export async function chooseSelect(control: Locator, value: string) {
  const native = await control.evaluate(
    (element) => element.tagName === "SELECT",
  );
  if (native) {
    await control.selectOption(value);
    return;
  }
  await control.click();
  await control
    .page()
    .locator(`[role="option"][data-value=${JSON.stringify(value)}]`)
    .click();
}
