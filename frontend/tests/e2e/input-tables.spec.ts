import { expect, test } from "@playwright/test";
import fs from "node:fs/promises";

test("saved versioned product table exports and imports CSV without losing metadata", async ({ page }) => {
  await page.goto("/#projects");
  await page.getByRole("button", { name: "Tạo dự án mẫu", exact: true }).click();
  await expect(page.getByText("Đã tạo dự án với 7 nhóm dữ liệu tổng hợp.")).toBeVisible();
  await page.getByRole("link", { name: "Sản phẩm", exact: true }).click();
  const awaited = page.waitForEvent("download");
  await page.getByRole("link", { name: "Xuất CSV đã lưu", exact: true }).click();
  const download = await awaited;
  const file = await download.path();
  const text = await fs.readFile(file!, "utf-8");
  expect(text).toContain("_metadata");
  expect(text).toContain("SYNTHETIC");
  expect(text).toContain("WATER");
  await page.getByLabel("Nhập và lưu CSV", { exact: true }).setInputFiles({ name: "products.csv", mimeType: "text/csv", buffer: Buffer.from(text) });
  await expect(page.getByLabel("sku dòng 1", { exact: true })).toHaveValue("WATER");
  await expect(page.getByText("Revision 8", { exact: false })).toBeVisible();
});
