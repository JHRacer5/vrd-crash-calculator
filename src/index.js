// Minimal Cloudflare Worker entry point for container routing
export default {
  async fetch(request, env, ctx) {
    // Forward all requests to the container
    return await env.CONTAINER.fetch(request);
  },
};
