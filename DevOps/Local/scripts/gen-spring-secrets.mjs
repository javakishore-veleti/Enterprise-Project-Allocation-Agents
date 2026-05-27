#!/usr/bin/env node
/*
 * Generate each Spring Boot service's `application-local-secrets.yaml` from the
 * git-ignored root `.env`.
 *
 *  - Source of truth: <repo-root>/.env  (git-ignored)
 *  - Target (per service, git-ignored):
 *      Middleware/<service>/<api-module>/src/main/resources/application-local-secrets.yaml
 *  - If the target already exists and differs from what .env would produce,
 *    the differing lines are printed (old `-` / new `+`) BEFORE the file is
 *    updated (a .bak copy is kept). Unchanged files are left untouched.
 *  - Services whose -api module does not exist yet (pre-M4) are skipped.
 *
 * No external dependencies — Node built-ins only. Run via `npm run secrets:gen`.
 */
import { readFileSync, writeFileSync, existsSync, mkdirSync, copyFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '../../..');
const ENV_PATH = join(ROOT, '.env');

// service dir -> Spring Boot api module (the deployable). See DevelopmentPlan §M4.
const SERVICES = [
  { dir: 'employee-service', api: 'employee-api' },
  { dir: 'project-service', api: 'project-api' },
  { dir: 'allocation-service', api: 'allocation-api' },
  { dir: 'notification-service', api: 'notification-api' },
  { dir: 'reporting-service', api: 'reporting-api' },
  { dir: 'api-gateway', api: 'gateway-api' },
];

const cyan = (s) => `\x1b[36m${s}\x1b[0m`;
const yellow = (s) => `\x1b[33m${s}\x1b[0m`;
const green = (s) => `\x1b[32m${s}\x1b[0m`;
const red = (s) => `\x1b[31m${s}\x1b[0m`;
const log = (s) => console.log(`${cyan('[secrets]')} ${s}`);

function parseEnv(path) {
  if (!existsSync(path)) {
    console.error(`${red('[secrets]')} .env not found at ${path}. Copy .env.example to .env first.`);
    process.exit(1);
  }
  const env = {};
  for (const raw of readFileSync(path, 'utf8').split('\n')) {
    const line = raw.trim();
    if (!line || line.startsWith('#')) continue;
    const eq = line.indexOf('=');
    if (eq === -1) continue;
    const key = line.slice(0, eq).trim();
    let val = line.slice(eq + 1).trim();
    if ((val.startsWith('"') && val.endsWith('"')) || (val.startsWith("'") && val.endsWith("'"))) {
      val = val.slice(1, -1);
    }
    env[key] = val;
  }
  return env;
}

// The secret-bearing config every service needs locally. Non-secret config
// belongs in the committed application-local.yaml (added in M4).
// DB_PROFILE selects the datasource: `h2` (default — no Postgres needed) or
// `postgres`. The Spring side activates the matching profile.
function renderSecrets(env) {
  const profile = (env.DB_PROFILE ?? 'h2').toLowerCase();
  const head = [
    '# GENERATED from .env by DevOps/Local/scripts/gen-spring-secrets.mjs',
    '# DO NOT COMMIT and DO NOT edit by hand — edit .env and re-run `npm run secrets:gen`.',
    `# active DB profile: ${profile}`,
  ];
  let datasource;
  if (profile === 'postgres') {
    datasource = [
      '  datasource:',
      `    url: ${env.SPRING_DATASOURCE_URL ?? 'jdbc:postgresql://localhost:5432/epaa'}`,
      `    username: ${env.POSTGRES_USER ?? 'epaa'}`,
      `    password: ${env.POSTGRES_PASSWORD ?? 'epaa_local'}`,
    ];
  } else {
    // H2 in-memory — the default so a service runs without docker Postgres.
    datasource = [
      '  datasource:',
      `    url: ${env.H2_URL ?? 'jdbc:h2:mem:epaa;DB_CLOSE_DELAY=-1;MODE=PostgreSQL'}`,
      `    username: ${env.H2_USER ?? 'sa'}`,
      `    password: ${env.H2_PASSWORD ?? ''}`,
    ];
  }
  return [
    ...head,
    'spring:',
    ...datasource,
    'epaa:',
    '  agents:',
    `    base-url: ${env.AGENTS_BASE_URL ?? 'http://localhost:8001'}`,
    '  aws:',
    `    region: ${env.AWS_REGION ?? 'us-east-1'}`,
    `    bedrock-model-id: ${env.BEDROCK_MODEL_ID ?? ''}`,
    '',
  ].join('\n');
}

function diffLines(oldText, newText) {
  const oldLines = oldText.split('\n');
  const newLines = newText.split('\n');
  const max = Math.max(oldLines.length, newLines.length);
  const out = [];
  for (let i = 0; i < max; i++) {
    const o = oldLines[i];
    const n = newLines[i];
    if (o === n) continue;
    if (o !== undefined) out.push(red(`  - ${o}`));
    if (n !== undefined) out.push(green(`  + ${n}`));
  }
  return out;
}

function main() {
  const env = parseEnv(ENV_PATH);
  const content = renderSecrets(env);
  let written = 0, unchanged = 0, skipped = 0;

  for (const { dir, api } of SERVICES) {
    const moduleDir = join(ROOT, 'Middleware', dir, api);
    if (!existsSync(moduleDir)) {
      log(`${yellow('skip')} ${dir}/${api} — module not created yet (pre-M4)`);
      skipped++;
      continue;
    }
    const resDir = join(moduleDir, 'src', 'main', 'resources');
    const target = join(resDir, 'application-local-secrets.yaml');

    if (existsSync(target)) {
      const current = readFileSync(target, 'utf8');
      if (current === content) {
        log(`${green('ok')} ${dir}/${api} — already up to date`);
        unchanged++;
        continue;
      }
      log(`${yellow('changed')} ${dir}/${api} — differences vs .env:`);
      for (const l of diffLines(current, content)) console.log(l);
      copyFileSync(target, `${target}.bak`);
      writeFileSync(target, content);
      log(`updated ${target} (previous saved as application-local-secrets.yaml.bak)`);
      written++;
    } else {
      mkdirSync(resDir, { recursive: true });
      writeFileSync(target, content);
      log(`${green('created')} ${target}`);
      written++;
    }
  }

  log(`done — ${written} written, ${unchanged} unchanged, ${skipped} skipped.`);
}

main();
