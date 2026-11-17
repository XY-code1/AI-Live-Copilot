import { expect, test } from "@playwright/test";

test("manual product appears in the product library", async ({ page, request }) => {
  const response = await request.post("http://127.0.0.1:18000/api/v1/products", {
    data: { name: "E2E 旅游商品", category: "旅游线路", summary: "端到端测试商品" },
  });
  expect(response.ok()).toBeTruthy();
  await page.context().addCookies([
    { name: "ailc_token", value: "e2e-dev", url: "http://127.0.0.1:13000" },
  ]);
  await page.goto("/products");
  await expect(page.getByText("E2E 旅游商品")).toBeVisible();
});

