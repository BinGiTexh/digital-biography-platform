# `@digital-biography/design-agent-core`

Generic utilities for generating React component stubs from a JSON design spec. Primarily exposes a single async function: `runDesignAgent(cfgPath, outDir)`.

```js
import { runDesignAgent } from "@digital-biography/design-agent-core";

await runDesignAgent("config/design-config.json", "./src/ui_generated");
```

Pass in a `design-config.json` object shaped like:

```json
{
  "brandColors": { "primary": "#ff6600" },
  "typography": { "heading": "Inter" },
  "screens": [
    { "name": "Home" },
    { "name": "About" }
  ]
}
```

The agent will emit `Home.jsx`, `About.jsx`, … into the output directory.
