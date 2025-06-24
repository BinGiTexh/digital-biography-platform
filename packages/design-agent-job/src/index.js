#!/usr/bin/env node
import { hideBin } from "yargs/helpers";
import yargs from "yargs/yargs";
import path from "node:path";
import { runDesignAgent } from "@digital-biography/design-agent-core";

const argv = yargs(hideBin(process.argv))
  .option("config", {
    alias: "c",
    type: "string",
    default: "config/design-config.json",
    describe: "Path to design-config.json"
  })
  .option("out", {
    alias: "o",
    type: "string",
    default: "../../frontend/src/ui_generated",
    describe: "Output directory for generated components"
  })
  .help()
  .argv;

const cfgPath = path.resolve(argv.config);
const outDir = path.resolve(path.dirname(new URL(import.meta.url).pathname), argv.out);

await runDesignAgent(cfgPath, outDir);
