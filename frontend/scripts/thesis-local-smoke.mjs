import process from "node:process";
import { chromium } from "playwright";

const baseUrl = process.env.DEVBOX_E2E_URL || "http://127.0.0.1:5175/";
const repoPrompt = "Using the seeded crypto-quant repo, what file is the primary edit target for the starter strategy? Reply in one short sentence and include the exact repo-relative path.";
const chartPrompt = `Reply with one short sentence and then exactly this markdown table:\n\n| Month | Revenue | Cost |\n| --- | ---: | ---: |\n| Jan | 10 | 4 |\n| Feb | 12 | 5 |\n| Mar | 14 | 6 |`;

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 1100 } });

try {
  await page.goto(baseUrl, { waitUntil: "networkidle", timeout: 30_000 });
  await page.getByPlaceholder("Message the agent...").waitFor({ state: "visible", timeout: 30_000 });
  const newChatButton = page.getByRole("button", { name: "New Chat" });
  if (await newChatButton.count()) {
    await newChatButton.click();
    await page.waitForTimeout(500);
  }

  const modeBadge = page.getByText(/live|polling/i).first();
  await modeBadge.waitFor({ state: "visible", timeout: 15_000 });

  await sendPrompt(page, repoPrompt);
  await waitForText(page, repoPrompt, 15_000);
  await waitForAssistantResponse(page, /crates\/poly-strat-starter\/src\/strategy\.rs|src\/strategy\.rs/i, 180_000);

  await sendPrompt(page, chartPrompt);
  await page.getByText("Jan").waitFor({ state: "visible", timeout: 180_000 });
  await waitForAnyChart(page, 60_000);

  console.log("E2E smoke passed:", {
    url: baseUrl,
    mode: (await modeBadge.textContent())?.trim() || "unknown",
  });
} finally {
  await page.close();
  await browser.close();
}

async function sendPrompt(page, prompt) {
  const textarea = page.getByPlaceholder("Message the agent...");
  await textarea.fill(prompt);
  await page.getByRole("button", { name: "Send message" }).click();
}

async function waitForAssistantResponse(page, matcher, timeoutMs) {
  const start = Date.now();

  while (Date.now() - start < timeoutMs) {
    const bodyText = await page.locator("body").innerText();
    if (matcher.test(bodyText) && !bodyText.includes("Assistant is working...")) {
      return;
    }

    const retryButton = page.getByRole("button", { name: "Retry request" });
    if (await retryButton.count()) {
      throw new Error("Assistant response failed and exposed a retry button.");
    }

    await page.waitForTimeout(1000);
  }

  throw new Error(`Timed out waiting for assistant response matching ${matcher}`);
}

async function waitForAnyChart(page, timeoutMs) {
  const chartLocator = page.locator("canvas, svg.recharts-surface");
  await chartLocator.first().waitFor({ state: "visible", timeout: timeoutMs });
}

async function waitForText(page, text, timeoutMs) {
  await page.waitForFunction(
    (expected) => document.body?.innerText.includes(expected),
    text,
    { timeout: timeoutMs },
  );
}
