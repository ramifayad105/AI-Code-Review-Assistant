import { initAutterServer } from "@autter/runtime-next/server";

export function register() {
  initAutterServer({
    apiKey: process.env.AUTTER_RUNTIME_KEY!,
    endpoint: process.env.AUTTER_ENDPOINT || "http://localhost:4318",
    service: "ai-code-review-dashboard",
    environment: process.env.NODE_ENV,
  });
}
