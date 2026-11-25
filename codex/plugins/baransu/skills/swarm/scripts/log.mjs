#!/usr/bin/env node
// Append one row to a swarm decision log (TSV).
// Usage: node log.mjs <logfile> <phase> <decision> <why> <evidence> <result>
// Stamps the UTC time, writes the header on first use, keeps every cell on one line,
// and prefixes a cell a spreadsheet would read as a formula (=, +, -, @) with a quote,
// since evidence can carry text the run did not write (titles, file names).
import fs from "node:fs";
import path from "node:path";

const args = process.argv.slice(2);
if (args.length !== 6) {
  process.stderr.write("usage: log.mjs <logfile> <phase> <decision> <why> <evidence> <result>\n");
  process.exit(1);
}
const [file, ...cells] = args;
const header = "ts\tphase\tdecision\twhy\tevidence\tresult\n";
const clean = (v) => {
  const one = String(v).replace(/[\t\r\n]+/g, " ").trim();
  return /^[=+\-@]/.test(one) ? `'${one}` : one;
};
const ts = new Date().toISOString().replace(/\.\d{3}Z$/, "Z");

fs.mkdirSync(path.dirname(path.resolve(file)), { recursive: true });
const empty = !fs.existsSync(file) || fs.statSync(file).size === 0;
fs.appendFileSync(file, (empty ? header : "") + [ts, ...cells.map(clean)].join("\t") + "\n", "utf8");
