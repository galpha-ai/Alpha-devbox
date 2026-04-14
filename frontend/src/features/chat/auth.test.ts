import { beforeEach, describe, expect, it } from "vitest";

import { resolveLocalDevUserId, writeAuthSession } from "./auth";

describe("resolveLocalDevUserId", () => {
  beforeEach(() => {
    window.localStorage.clear();
  });

  it("creates and persists a local UUID when none exists", () => {
    const userId = resolveLocalDevUserId(
      window.localStorage,
      undefined,
      () => "generated-user-id",
    );

    expect(userId).toBe("generated-user-id");
    expect(
      resolveLocalDevUserId(window.localStorage, undefined, () => "ignored"),
    ).toBe("generated-user-id");
  });

  it("prefers an explicit configured local user id", () => {
    const userId = resolveLocalDevUserId(
      window.localStorage,
      "configured-user",
      () => "ignored",
    );

    expect(userId).toBe("configured-user");
    expect(
      resolveLocalDevUserId(window.localStorage, undefined, () => "ignored"),
    ).toBe("configured-user");
  });

  it("migrates an existing local dev session user id before generating a new one", () => {
    writeAuthSession(window.localStorage, {
      accessToken: "local-dev-access-token",
      refreshToken: null,
      user: {
        id: "legacy-user",
        address: "local:legacy-user",
        email: null,
        username: "legacy-user",
        display_name: "Legacy User",
        avatar_url: null,
        created_at: "2026-04-14T00:00:00.000Z",
        last_login_at: "2026-04-14T00:00:00.000Z",
        chain_id: "local",
      },
    });

    expect(
      resolveLocalDevUserId(window.localStorage, undefined, () => "ignored"),
    ).toBe("legacy-user");
  });
});
