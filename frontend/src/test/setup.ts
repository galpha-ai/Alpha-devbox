import "@testing-library/jest-dom";

Object.defineProperty(window, "matchMedia", {
  writable: true,
  value: (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => {},
  }),
});

class MockIntersectionObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
  takeRecords() {
    return [];
  }
}

Object.defineProperty(globalThis, "IntersectionObserver", {
  writable: true,
  value: MockIntersectionObserver,
});

Object.defineProperty(window, "IntersectionObserver", {
  writable: true,
  value: MockIntersectionObserver,
});

class MockResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
}

Object.defineProperty(globalThis, "ResizeObserver", {
  writable: true,
  value: MockResizeObserver,
});

Object.defineProperty(window, "ResizeObserver", {
  writable: true,
  value: MockResizeObserver,
});

Object.defineProperty(window, "requestIdleCallback", {
  writable: true,
  value: (callback: IdleRequestCallback) =>
    window.setTimeout(() => callback({ didTimeout: false, timeRemaining: () => 0 } as IdleDeadline), 1),
});

Object.defineProperty(window, "cancelIdleCallback", {
  writable: true,
  value: (id: number) => window.clearTimeout(id),
});

Object.defineProperty(HTMLCanvasElement.prototype, "getContext", {
  writable: true,
  value: () => null,
});

Object.defineProperty(HTMLElement.prototype, "scrollIntoView", {
  writable: true,
  value: () => {},
});
