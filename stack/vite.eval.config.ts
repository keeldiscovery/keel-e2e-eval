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

// **keel-web spec 023 moved the app to React Router 7 framework mode** (`@react-router/dev/vite`'s
// `reactRouter()` carries React refresh itself and reads `react-router.config.ts` from the root,
// which is keel-web because that is the cwd). Loading `@vitejs/plugin-react` alone against that
// checkout boots a vite that answers 404 on `/` -- found by spec 039, the first `make up` against
// keel-web e54cb1c. The framework plugin is preferred when keel-web carries it, and the plain
// React plugin is kept for an older checkout. keel-web's own `define` block is restated so a
// guarded panel stays deleted in the eval's build exactly as in keel-web's.
import fs from "node:fs";

export default async () => {
  const routerPluginPath = path.join(
    process.cwd(), "node_modules", "@react-router", "dev", "dist", "vite.js");
  let plugins;
  if (fs.existsSync(routerPluginPath) && fs.existsSync(path.join(process.cwd(), "react-router.config.ts"))) {
    const { reactRouter } = await import(pathToFileURL(routerPluginPath).href);
    plugins = [reactRouter()];
  } else {
    const pluginPath = path.join(
      process.cwd(),
      "node_modules",
      "@vitejs",
      "plugin-react",
      "dist",
      "index.js",
    );
    const { default: react } = await import(pathToFileURL(pluginPath).href);
    plugins = [react()];
  }

  return {
    // Spec 044 (keel-web 069 FR-010): the eval serves keel-web the way keel-web's own e2e does, `--mode test`, so the
    // test build's one seam -- `window.__keelSpeech`, the speech recogniser the AI interviewer's page listens through --
    // is in it, and the stranger can "speak" without a microphone. Nothing else in keel-web reads the mode
    // (`import.meta.env.DEV` is still true under `vite` serve); a production build folds the seam away, which
    // `tests/test_interviewer_screens.py` holds on keel-web's source. EVAL_WEB_MODE overrides it.
    mode: process.env.EVAL_WEB_MODE ?? "test",
    plugins,
    define: {
      "import.meta.env.VITE_KEEL_SHOW_SPEC_KIT_PANEL": JSON.stringify(process.env.VITE_KEEL_SHOW_SPEC_KIT_PANEL ?? "0"),
      "import.meta.env.VITE_KEEL_SHOW_UNREVIEWED_FRAMES": JSON.stringify(process.env.VITE_KEEL_SHOW_UNREVIEWED_FRAMES ?? "0"),
      "import.meta.env.VITE_KEEL_BUILD": JSON.stringify(process.env.VITE_KEEL_BUILD ?? ""),
    },
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
