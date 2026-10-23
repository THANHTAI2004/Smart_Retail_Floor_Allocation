import { expect, test } from "@playwright/test";
import fs from "node:fs/promises";
import path from "node:path";
import { execFile } from "node:child_process";
import { promisify } from "node:util";

const run = promisify(execFile);
const output = process.env.SMART_RETAIL_E2E_OUTPUT || "../var/playwright";

test("audit all pages and seven UI saves against direct MongoDB readback", async ({ page }) => {
  test.setTimeout(120000);
  const errors: string[] = [];
  const failures: string[] = [];
  page.on("pageerror", e => errors.push(e.message));
  page.on("response", r => { if (r.status() >= 500) failures.push(`${r.status()} ${r.url()}`); });
  await page.goto("/#projects");
  await page.getByLabel("Tên dự án", { exact: true }).fill(`System audit ${Date.now()}`);
  await page.getByRole("button", { name: "Tạo dự án mẫu", exact: true }).click();
  await expect(page.getByText("Đã tạo dự án với 7 nhóm dữ liệu tổng hợp.")).toBeVisible();
  const projectId = await page.evaluate(() => localStorage.getItem("smart-retail-project"));
  expect(projectId).toBeTruthy();
  const evidence: object[] = [];
  const readback = async () => {
    const result = await run(path.resolve("../.venv/Scripts/python.exe"), ["-c",
      "import json,os,sys; from smart_retail.infrastructure.mongodb.client import connect; s,_=connect(database=os.environ['MONGODB_DATABASE']); p=s.get_project(sys.argv[1]); print(json.dumps({'revision':p.revision,'sections':p.sections})); s.dispose()", projectId!], { cwd: path.resolve("..") });
    return JSON.parse(result.stdout);
  };
  await page.goto("/#floorplan");
  const drawing = page.waitForResponse(r => r.request().method() === "PUT" && r.url().includes("/inputs/shelves"));
  await page.getByRole("button", { name: "Lưu bản vẽ & kệ", exact: true }).click();
  const savedDrawing = await (await drawing).json();
  expect((await readback()).sections).toEqual(savedDrawing.sections);
  evidence.push({ section: "floorplan+shelves", revision: savedDrawing.revision, mongo: "MATCH" });
  for (const section of ["shelves", "categories", "products", "demand", "orders", "optimization"]) {
    await page.goto(`/#${section}`);
    const response = page.waitForResponse(r => r.request().method() === "PUT" && r.url().includes(`/inputs/${section}`));
    await page.getByRole("button", { name: "Lưu dữ liệu", exact: true }).click();
    const saved = await (await response).json();
    const stored = await readback();
    expect(stored.revision).toBe(saved.revision);
    expect(stored.sections).toEqual(saved.sections);
    await page.reload();
    await expect(page.getByRole("button", { name: "Lưu dữ liệu", exact: true })).toBeVisible();
    evidence.push({ section, revision: saved.revision, mongo: "MATCH", reload: "PASS" });
  }
  await page.goto("/#runs");
  await page.getByRole("button", { name: "Chạy baseline", exact: true }).click();
  await expect(page.locator("tbody").getByText("SUCCEEDED", { exact: true }).first()).toBeVisible({ timeout: 45000 });
  await page.getByRole("button", { name: "Kết quả", exact: true }).first().click();
  await page.getByRole("link", { name: "Planogram", exact: true }).click();
  await expect(page.getByRole("cell", { name: "WATER", exact: true })).toBeVisible();
  await fs.mkdir(`${output}/system-pages`, { recursive: true });
  const routes = ["dashboard", "projects", "floorplan", "shelves", "categories", "products", "demand", "orders", "optimization", "runs", "layout", "planogram", "simulation", "research", "reports", "diagnostics"];
  for (const route of routes) {
    await page.goto(`/#${route}`);
    await expect(page.locator("h1")).toBeVisible();
    await expect(page.locator("main")).not.toBeEmpty();
    await page.screenshot({ path: `${output}/system-pages/${route}.png`, fullPage: true });
  }
  expect(errors).toEqual([]);
  expect(failures).toEqual([]);
  await fs.writeFile(`${output}/system-pages/verification.json`, JSON.stringify({ status: "PASS", routes, projectId, sevenGroupReadbacks: evidence, errors, failures }, null, 2));
});
