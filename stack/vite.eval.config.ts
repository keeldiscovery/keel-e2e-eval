// Eval-owned vite config (research.md §2, contracts/stack-contract.md): port 5173 strict, proxy
// /v2 -> keel-cloud on 18080, so the browser speaks same-origin exactly as the deployed shape
// (keel-cloud has no CORS configuration). Neither product repo is touched.
//
// This file lives in keel-e2e-eval, but is launched with keel-web as the working directory:
//   npx vite --config <this file>   (run from the keel-web checkout)
//
// A plain `import react from "@vitejs/plugin-react"` -- or even `import { defineConfig } from
// "vite"` -- resolves node_modules relative to THIS file's own directory (vite's config loader
// bundles it with esbuild using the config file's own directory as the resolve root), which is
// outside keel-web's node_modules tree entirely: keel-e2e-eval and keel-web are siblings, not
// nested, so that lookup never reaches keel-web/node_modules and the whole config fails to load
// ("Cannot find module '@vitejs/plugin-react'", and even "Cannot find module 'vite'" itself).
//
// Fixed by resolving no bare specifiers at all in this file: the react plugin is loaded via an
// absolute file:// dynamic import straight at keel-web's own installed copy (found relative to
// process.cwd(), which is keel-web because that's where this config is launched from), and the
// exported config is a plain object -- `defineConfig` is only a TS-inference convenience, not
// required at runtime, so skipping its import sidesteps the same problem for "vite" itself.
// Verified empirically against this exact keel-web checkout before wiring it into stack/web.py.
import path from "node:path";
import { pathToFileURL } from "node:url";

const WEB_PORT = Number(process.env.EVAL_WEB_PORT ?? 5173);
const CLOUD_PORT = Number(process.env.EVAL_CLOUD_PORT ?? 18080);

export default async () => {
  const pluginPath = path.join(
    process.cwd(),
    "node_modules",
    "@vitejs",
    "plugin-react",
    "dist",
    "index.js",
  );
  const { default: react } = await import(pathToFileURL(pluginPath).href);

  return {
    plugins: [react()],
    resolve: {
      alias: {
        "@": path.join(process.cwd(), "src"),
      },
    },
    server: {
      port: WEB_PORT,
      strictPort: true,
      proxy: {
        "/v2": `http://localhost:${CLOUD_PORT}`,
      },
    },
  };
};
