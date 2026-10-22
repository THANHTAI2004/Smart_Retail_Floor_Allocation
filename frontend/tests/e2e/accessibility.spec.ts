const output = process.env.SMART_RETAIL_E2E_OUTPUT || "../var/playwright";
import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import fs from "node:fs/promises";

test("dashboard and editor accessibility checks", async ({ page }) => {
  await page.goto("/#projects");
  await page
    .getByRole("button", { name: "Tạo dự án mẫu", exact: true })
    .click();
  await expect(
    page.getByText("Đã tạo dự án với 7 nhóm dữ liệu tổng hợp."),
  ).toBeVisible();
  const results: Record<string, unknown> = {};
  for (const route of ["dashboard", "floorplan", "research"]) {
    await page.goto(`/#${route}`);
    await expect(page.locator("h1")).toBeVisible();
    const result = await new AxeBuilder({ page })
      .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
      .analyze();
    results[route] = result.violations;
  }
  await fs.mkdir(output, { recursive: true });
  await fs.writeFile(
    `${output}/axe-results.json`,
    JSON.stringify(results, null, 2),
  );
  expect(
    Object.values(results)
      .flat()
      .map((issue) => (issue as { id: string }).id),
  ).toEqual([]);
});
