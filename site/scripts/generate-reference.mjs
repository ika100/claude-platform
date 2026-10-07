// Generates the reference pages from the code, so they cannot drift: commands (plugins/*/commands), shapes (shapes.yml),
// configuration schema (render.py docstring, local-cluster.sh header) and the cplat CLI help.
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import YAML from 'yaml';
import { mdTableCell, splitDescription, withFrontMatter } from './lib.mjs';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const OUT = path.join(ROOT, 'site', 'src', 'content', 'docs', 'reference');
fs.mkdirSync(OUT, { recursive: true });
const write = (name, title, description, body, order) =>
  fs.writeFileSync(path.join(OUT, name), withFrontMatter(body, { title, description, order, editUrl: false }));
const read = (p) => fs.readFileSync(path.join(ROOT, p), 'utf8');

// ---- commands ----
const plugins = fs.readdirSync(path.join(ROOT, 'plugins')).sort();
const pluginMeta = Object.fromEntries(plugins.map((p) => [p, JSON.parse(read(`plugins/${p}/.claude-plugin/plugin.json`))]));
let commands = '';
let count = 0;
for (const plugin of plugins) {
  const dir = path.join(ROOT, 'plugins', plugin, 'commands');
  if (!fs.existsSync(dir)) continue;
  const rows = fs.readdirSync(dir).filter((f) => f.endsWith('.md')).sort().map((f) => {
    const front = fs.readFileSync(path.join(dir, f), 'utf8').match(/^---\n([\s\S]*?)\n---/);
    const { summary, usage } = splitDescription(YAML.parse(front[1]).description);
    count += 1;
    return `| \`/${plugin}:${f.replace(/\.md$/, '')}\` | ${mdTableCell(summary)} | ${usage ? `\`${mdTableCell(usage)}\`` : ''} |`;
  });
  commands += `\n## ${plugin} (version ${pluginMeta[plugin].version})\n\n${mdTableCell(pluginMeta[plugin].description).replace(/\\\|/g, '|')}\n\n| Command | What it does | Usage |\n|---|---|---|\n${rows.join('\n')}\n`;
}
write('commands.md', 'Slash commands', `All ${count} slash commands of the claude-platform plugins, generated from the plugin sources.`,
  `These pages are generated from \`plugins/*/commands/*.md\`. Install the plugins with \`/plugin marketplace add ika100/claude-platform\` and \`/plugin install <name>@ika100-claude\`.\n${commands}`, 1);

// ---- shapes ----
const shapes = YAML.parse(read('shapes.yml')).shapes;
const shapeRows = shapes.map((s) => `| \`${s.id}\` | ${s.plugin} | \`templates/${s.template}\` | ${s.deployable ? 'yes' : 'no'} | ${s.default_stack ? mdTableCell(Object.values(s.default_stack).join(' / ')) : ''} | ${s.runtime ? `${s.runtime.port}; \`${s.runtime.probes.readiness}\`; \`${s.runtime.metrics ?? '-'}\`` : '-'} | ${s.status} |`);
write('shapes.md', 'Shapes', 'The repository shapes the platform can create and operate, generated from shapes.yml.',
  `A **shape** is a kind of repository. It decides which template creates it and which agents work on it. This table is generated from \`shapes.yml\`, the single source of truth.\n\n| Shape | Plugin | Template | Deployable | Default stack | Port; readiness probe; metrics path | Status |\n|---|---|---|---|---|---|---|\n${shapeRows.join('\n')}\n\nTo add a shape, follow [Adding a new shape](/claude-platform/guides/add-a-shape/).\n`, 2);

// ---- configuration ----
const render = read('templates/gitops-app/scripts/render.py');
const doc = render.match(/"""([\s\S]*?)"""/)[1].split('\n').slice(1).join('\n').replace(/^Usage:[\s\S]*$/m, '').trim();
const cluster = read('templates/gitops-app/scripts/local-cluster.sh').split('\n').slice(1).filter((l) => l.startsWith('#')).map((l) => l.replace(/^# ?/, '')).join('\n').split('set -euo')[0].trim();
write('configuration.md', 'Configuration reference', 'services.yaml, app.yaml and the cluster-up environment variables, generated from the renderer and the cluster script.',
  `The GitOps repository is configured by two files per application: \`applications/<app>/services.yaml\` (which services, how they run) and \`applications/<app>/app.yaml\` (how the application is exposed, which addons and policies it uses). Everything below is extracted from the source of \`render.py\` and \`local-cluster.sh\`, so it is always current.\n\n## services.yaml and app.yaml (render.py)\n\n\`\`\`text\n${doc}\n\`\`\`\n\n## devbox run cluster-up (local-cluster.sh)\n\n\`\`\`text\n${cluster}\n\`\`\`\n`, 3);

// ---- cplat CLI ----
const cplatPy = path.join(ROOT, 'scripts', 'cplat', 'cplat.py');
const overview = read('scripts/cplat/cplat.py').match(/"""([\s\S]*?)"""/)[1].trim();
const subs = [...read('scripts/cplat/cplat.py').matchAll(/^\s+"([a-z-]+)": "[a-z]+",$/gm)].map((m) => m[1]);
let helpText = '';
for (const sub of subs) {
  const r = spawnSync('uv', ['run', cplatPy, sub, '--help'], { encoding: 'utf8', cwd: ROOT });
  if (r.status === 0 && r.stdout.trim()) helpText += `\n### ${sub}\n\n\`\`\`text\n${r.stdout.trim()}\n\`\`\`\n`;
}
write('cplat.md', 'The cplat CLI', 'The tested command-line tool behind the slash commands.',
  `The slash commands are thin: they run \`scripts/cplat/cplat.py\`, show you a preview (\`--dry-run\`), and only then act. You can run it yourself.\n\n\`\`\`text\n${overview}\n\`\`\`\n\n## Options per command\n${helpText || '\nThe option listing is generated in CI (it needs `uv`); see `cplat.py <command> --help`.\n'}`, 4);
console.log(`generated reference pages (${count} commands, ${shapes.length} shapes, ${subs.length} cplat commands)`);
