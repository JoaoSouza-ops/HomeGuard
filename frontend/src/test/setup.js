import "@testing-library/jest-dom/vitest";

// O Recharts usa ResizeObserver, que o jsdom não tem.
globalThis.ResizeObserver = class {
  observe() {}
  unobserve() {}
  disconnect() {}
};
