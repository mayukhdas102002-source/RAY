// Render every aspect of the brand film plus stills.
// Usage: node scripts/render-all.mjs [--aspects 16x9,9x16] [--draft] [--no-captions] [--props props.json]
import {spawnSync} from 'node:child_process';
import {mkdirSync} from 'node:fs';

const args = process.argv.slice(2);
const get = (flag, def) => {
  const i = args.indexOf(flag);
  return i >= 0 ? args[i + 1] : def;
};
const aspects = get('--aspects', '16x9,9x16,1x1,4x5').split(',');
const draft = args.includes('--draft');
const noCaptions = args.includes('--no-captions');
const propsFile = get('--props', null);

mkdirSync('renders', {recursive: true});
const run = (cmd) => {
  console.log(`> ${cmd}`);
  const r = spawnSync(cmd, {stdio: 'inherit', shell: true});
  if (r.status !== 0) process.exit(r.status ?? 1);
};

const extra = [];
if (draft) extra.push('--scale=0.5', '--crf=28');
if (propsFile) extra.push(`--props=${propsFile}`);
if (noCaptions) extra.push(`--props="{\\"showCaptions\\":false}"`);

for (const a of aspects) {
  const suffix = `${draft ? 'draft-' : ''}${a}${noCaptions ? '-clean' : ''}`;
  run(`npx remotion render BrandFilm-${a} renders/brandfilm-${suffix}.mp4 ${extra.join(' ')}`);
  if (!draft) run(`npx remotion still EndCard-${a} renders/endcard-${a}.png`);
}
