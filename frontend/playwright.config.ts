import { defineConfig } from "@playwright/test";

const output = process.env.SMART_RETAIL_E2E_OUTPUT || "../var/playwright";
export default defineConfig({
  testDir: "./tests/e2e",
  timeout: 60000,
  expect: { timeout: 15000 },
  workers: 1,
  outputDir: `${output}/test-results`,
  use: {
    baseURL: process.env.SMART_RETAIL_E2E_URL || "http://127.0.0.1:5173",
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
  reporter: [
    ["list"],
    ["json", { outputFile: `${output}/results.json` }],
  ],
});
