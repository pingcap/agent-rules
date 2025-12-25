---
name: tidbx-serverless
description: Guidance for using the TiDB Cloud Serverless Driver (Beta) in Node.js, serverless, and edge environments. Use when connecting to TiDB Cloud Starter/Essential over HTTP with @tidbcloud/serverless, or when integrating with Prisma/Kysely/Drizzle serverless adapters in Vercel/Cloudflare/Netlify/Deno/Bun.
---

# TiDB Cloud Serverless Driver (Beta)

Use this skill to guide users who need the TiDB Cloud serverless driver for serverless or edge environments.

## Introduction

Traditional TCP-based MySQL drivers are not suitable for serverless functions due to their expectation of long-lived, persistent TCP connections, which contradict the short-lived nature of serverless functions. Moreover, in edge environments such as Vercel Edge Functions and Cloudflare Workers, where comprehensive TCP support and full Node.js compatibility may be lacking, these drivers may not work at all.

TiDB Cloud serverless driver (Beta) for JavaScript lets you connect to your TiDB Cloud Starter or TiDB Cloud Essential cluster over HTTP, which is generally supported by serverless environments. With it, it is now possible to connect to TiDB Cloud Starter or TiDB Cloud Essential clusters from edge environments and reduce connection overhead with TCP while keeping the similar development experience of traditional TCP-based MySQL drivers.

## Install

**`npm install @tidbcloud/serverless`**

## Tutorials (References)

Use the reference files for step-by-step tutorials and code samples. Load only what is needed, and prefer the table of contents in each reference to jump to the right section:

- Overview and configuration: `references/serverless-driver.md`
- Node.js tutorial: `references/nodejs.md`
- Prisma adapter tutorial: `references/prisma.md`
- Kysely tutorial: `references/kysely.md`
- Drizzle tutorial: `references/drizzle.md`

## Usage Guidance

- Always confirm the target cluster type: Starter or Essential.
- Ask which runtime and ORM the user is using (Node.js, Vercel Edge, Cloudflare Workers, Netlify, Deno, Bun, Prisma, Kysely, Drizzle).
- Use the connection string from the TiDB Cloud console. In the cluster **Connect** dialog, choose **Serverless Driver** and generate/reset the password before copying `DATABASE_URL`.
- For Node.js < 18, use the `undici` fetch shim as described in `references/nodejs.md`.
- If the user needs cluster provisioning, route them to the `tidbx` skill.
