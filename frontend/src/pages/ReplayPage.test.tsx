import { MemoryRouter, Route, Routes } from "react-router-dom";
import { render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import ReplayPage from "./ReplayPage";

vi.mock("@galpha-ai/better-markdown/react", () => ({
  MarkdownChartRenderer: ({
    markdown,
  }: {
    markdown: string;
  }) => <div data-testid="vendor-markdown">{markdown}</div>,
}));

describe("ReplayPage", () => {
  const fetchMock = vi.fn<typeof fetch>();

  beforeEach(() => {
    fetchMock.mockReset();
    vi.stubGlobal("fetch", fetchMock);
  });

  it("renders a read-only replay thread from the replay API", async () => {
    fetchMock.mockResolvedValue(
      new Response(
        JSON.stringify({
          messages: [
            {
              id: "user-1",
              role: "user",
              parts: [{ type: "text", text: "hello", state: "done" }],
              metadata: {
                timestamp: "2026-04-15T00:00:00.000Z",
                sender: "user",
                senderName: "You",
              },
            },
            {
              id: "assistant-1",
              role: "assistant",
              parts: [{ type: "text", text: "world", state: "done" }],
              metadata: {
                timestamp: "2026-04-15T00:00:01.000Z",
                sender: "Devbox",
                senderName: "Devbox",
              },
            },
          ],
        }),
        {
          status: 200,
          headers: { "Content-Type": "application/json" },
        },
      ),
    );

    renderWithRoute("/replay/rpl_123");

    expect(screen.getByText("Loading replay...")).toBeInTheDocument();

    expect(await screen.findByText("Replay")).toBeInTheDocument();
    expect(await screen.findByText("world")).toBeInTheDocument();
    expect(
      screen.queryByPlaceholderText("Message the agent..."),
    ).not.toBeInTheDocument();

    expect(fetchMock).toHaveBeenCalledWith(
      "/api/devbox/replays/rpl_123/ui-messages",
      expect.objectContaining({ method: "GET" }),
    );
  });

  it("focuses and highlights a deep-linked reply after hydration", async () => {
    const scrollIntoView = vi.spyOn(HTMLElement.prototype, "scrollIntoView");

    fetchMock.mockResolvedValue(
      new Response(
        JSON.stringify({
          messages: [
            {
              id: "assistant-1",
              role: "assistant",
              parts: [{ type: "text", text: "first", state: "done" }],
              metadata: {
                timestamp: "2026-04-15T00:00:00.000Z",
                sender: "Devbox",
                senderName: "Devbox",
              },
            },
            {
              id: "assistant-2",
              role: "assistant",
              parts: [{ type: "text", text: "second", state: "done" }],
              metadata: {
                timestamp: "2026-04-15T00:00:01.000Z",
                sender: "Devbox",
                senderName: "Devbox",
              },
            },
          ],
        }),
        {
          status: 200,
          headers: { "Content-Type": "application/json" },
        },
      ),
    );

    renderWithRoute("/replay/rpl_123?reply=assistant-2");

    const highlighted = await screen.findByTestId("replay-message-assistant-2");

    await waitFor(() => {
      expect(highlighted).toHaveAttribute("data-highlighted", "true");
    });
    expect(scrollIntoView).toHaveBeenCalled();
  });

  it("renders a replay-specific error state when the API request fails", async () => {
    fetchMock.mockResolvedValue(
      new Response(
        JSON.stringify({ message: "Replay not found" }),
        {
          status: 404,
          headers: { "Content-Type": "application/json" },
        },
      ),
    );

    renderWithRoute("/replay/missing");

    expect(await screen.findByText("Replay unavailable")).toBeInTheDocument();
    expect(screen.getByText("Replay not found")).toBeInTheDocument();
  });
});

function renderWithRoute(initialEntry: string) {
  return render(
    <MemoryRouter initialEntries={[initialEntry]}>
      <Routes>
        <Route path="/replay/:replayId" element={<ReplayPage />} />
      </Routes>
    </MemoryRouter>,
  );
}
