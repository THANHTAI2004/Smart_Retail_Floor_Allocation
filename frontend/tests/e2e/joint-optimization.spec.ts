import { expect, test } from "@playwright/test";
import fs from "node:fs/promises";
import path from "node:path";

test("joint dashboard shows real local trap, exact proof, trace and candidate views", async ({ page }) => {
  test.setTimeout(150000);
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.goto("/#research");
  await page.getByLabel("Cấu hình campaign", { exact: true }).selectOption("joint_certification");
  await page.getByLabel("Số seed độc lập", { exact: true }).fill("1");
  await page.getByLabel("Giới hạn mỗi job (s)", { exact: true }).fill("60");
  // The preceding replay test may finish its UI assertions while its report
  // supervisor is still publishing. Wait for that real process to finish.
  await expect.poll(async () => {
    const response = await page.request.get("/api/research/campaigns");
    const campaigns = await response.json() as { supervisor?: { status: string } }[];
    return campaigns.some((c) => ["QUEUED", "RUNNING"].includes(c.supervisor?.status || ""));
  }, { timeout: 30000 }).toBe(false);
  await page.getByRole("button", { name: "Bắt đầu campaign", exact: true }).click();
  await expect(page.getByRole("status")).toContainText("COMPLETED", { timeout: 100000 });
  await expect(page.getByRole("cell", { name: "SUCCEEDED", exact: true })).toHaveCount(5);
  const exact = await page.getByLabel("Joint job", { exact: true }).locator("option").filter({ hasText: /^exact ·/ }).getAttribute("value");
  await page.getByLabel("Joint job", { exact: true }).selectOption(exact!);
  const panel = page.getByRole("region", { name: "Joint optimization evidence" });
  await expect(panel).toContainText("GLOBAL_OPTIMAL_CERTIFIED", { timeout: 15000 });
  await expect(panel).toContainText("Verification: PASS");
  await expect(panel.getByRole("img", { name: "Selected candidate layout", exact: true })).toBeVisible();
  const feedback = await page.getByLabel("Joint job", { exact: true }).locator("option").filter({ hasText: /^feedback ·/ }).getAttribute("value");
  await page.getByLabel("Joint job", { exact: true }).selectOption(feedback!);
  await expect(panel).toContainText("CONVERGED_LOCAL");
  await expect(panel).toContainText("FEASIBLE_NOT_PROVEN");
  await expect(panel.getByRole("img", { name: "Feedback convergence", exact: true })).toBeVisible();
  await expect(page.getByRole("link", { name: "joint-trace.csv", exact: true })).toBeVisible({ timeout: 15000 });
  const output = process.env.SMART_RETAIL_E2E_OUTPUT || "../var/playwright";
  await fs.mkdir(path.join(output, "ui"), { recursive: true });
  await page.screenshot({ path: path.join(output, "ui/joint-feedback.png"), fullPage: true });
  await page.getByLabel("Joint job", { exact: true }).selectOption(exact!);
  await expect(panel).toContainText("GLOBAL_OPTIMAL_CERTIFIED");
  await page.screenshot({ path: path.join(output, "ui/joint-exact.png"), fullPage: true });
  expect(errors).toEqual([]);
});
