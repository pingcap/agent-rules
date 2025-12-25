# TiDB Cloud Serverless Driver Drizzle Tutorial

[Drizzle ORM](https://orm.drizzle.team/) is a lightweight and performant TypeScript ORM with developer experience in mind. Starting from `drizzle-orm@0.31.2`, it supports [drizzle-orm/tidb-serverless](https://orm.drizzle.team/docs/get-started-mysql#tidb-serverless), enabling you to use Drizzle over HTTPS with TiDB Cloud serverless driver.

This tutorial describes how to use TiDB Cloud serverless driver with Drizzle in Node.js environments and edge environments.

> **Tip:**
>
> In addition to Starter clusters, the steps in this document also work with Essential clusters.

## Use Drizzle and TiDB Cloud serverless driver in Node.js environments

### Before you begin

To complete this tutorial, you need the following:

- [Node.js](https://nodejs.org/en) >= 18.0.0.
- [npm](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) or your preferred package manager.
- A Starter cluster. If you don't have any, create a Starter cluster in TiDB Cloud.

### Step 1. Create a project

1. Create a project named `drizzle-node-example`:

   ```shell
   mkdir drizzle-node-example
   cd drizzle-node-example
   ```

2. Install the `drizzle-orm` and `@tidbcloud/serverless` packages:

   ```shell
   npm install drizzle-orm @tidbcloud/serverless
   ```

3. In the root directory of your project, locate the `package.json` file, and then specify ES modules by adding `"type": "module"`:

   ```json
   {
     "type": "module",
     "dependencies": {
       "@tidbcloud/serverless": "^0.1.1",
       "drizzle-orm": "^0.31.2"
     }
   }
   ```

4. In the root directory of your project, add a `tsconfig.json` file to define the TypeScript compiler options:

   ```json
   {
     "compilerOptions": {
       "module": "ES2022",
       "target": "ES2022",
       "moduleResolution": "node",
       "strict": false,
       "declaration": true,
       "outDir": "dist",
       "removeComments": true,
       "allowJs": true,
       "esModuleInterop": true,
       "resolveJsonModule": true
     }
   }
   ```

### Step 2. Set the environment

1. In the TiDB Cloud console, navigate to the Clusters page of your project, and then click the name of your target Starter cluster to go to its overview page.

2. On the overview page, click **Connect** in the upper-right corner, select `Serverless Driver` in the **Connect With** drop-down list, and then click **Generate Password** to create a random password.

   > **Tip:**
   >
   > If you have created a password before, you can either use the original password or click **Reset Password** to generate a new one.

   The connection string looks like this:

   ```
   mysql://[username]:[password]@[host]/[database]
   ```

3. Set the environment variable `DATABASE_URL` in your local environment. For example, in Linux or macOS:

   ```shell
   export DATABASE_URL='mysql://[username]:[password]@[host]/[database]'
   ```

### Step 3. Use Drizzle to query data

1. Create a table in your Starter cluster.

   You can use SQL Editor in the TiDB Cloud console to execute SQL statements. Example:

   ```sql
   CREATE TABLE `test`.`users` (
    `id` BIGINT PRIMARY KEY auto_increment,
    `full_name` TEXT,
    `phone` VARCHAR(256)
   );
   ```

2. In the root directory of your project, create a file named `hello-world.ts` and add the following code:

   ```ts
   import { connect } from '@tidbcloud/serverless'
   import { drizzle } from 'drizzle-orm/tidb-serverless'
   import { mysqlTable, serial, text, varchar } from 'drizzle-orm/mysql-core'

   const client = connect({ url: process.env.DATABASE_URL })
   const db = drizzle(client)

   export const users = mysqlTable('users', {
     id: serial('id').primaryKey(),
     fullName: text('full_name'),
     phone: varchar('phone', { length: 256 })
   })
   export type User = typeof users.$inferSelect
   export type NewUser = typeof users.$inferInsert

   const user: NewUser = { fullName: 'John Doe', phone: '123-456-7890' }
   await db.insert(users).values(user)
   const result: User[] = await db.select().from(users)
   console.log(result)
   ```

### Step 4. Run the Typescript code

1. Install `ts-node` and `@types/node`:

   ```shell
   npm install -g ts-node
   npm i --save-dev @types/node
   ```

2. Run the Typescript code:

   ```shell
   ts-node --esm hello-world.ts
   ```

## Use Drizzle and TiDB Cloud serverless driver in edge environments

This section takes the Vercel Edge Function as an example.

### Before you begin

To complete this tutorial, you need the following:

- A [Vercel](https://vercel.com/docs) account that provides edge environment.
- [npm](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) or your preferred package manager.
- A Starter cluster. If you don't have any, create a Starter cluster in TiDB Cloud.

### Step 1. Create a project

1. Install the Vercel CLI:

   ```shell
   npm i -g vercel@latest
   ```

2. Create a Next.js project called `drizzle-example`:

   ```shell
   npx create-next-app@latest drizzle-example --ts --no-eslint --tailwind --no-src-dir --app --import-alias "@/*"
   ```

3. Navigate to the `drizzle-example` directory:

   ```shell
   cd drizzle-example
   ```

4. Install the `drizzle-orm` and `@tidbcloud/serverless` packages:

   ```shell
   npm install drizzle-orm @tidbcloud/serverless --force
   ```

### Step 2. Set the environment

1. In the TiDB Cloud console, navigate to the Clusters page of your project, and then click the name of your target Starter cluster to go to its overview page.

2. On the overview page, click **Connect** in the upper-right corner, select `Serverless Driver` in the **Connect With** drop-down list, and then click **Generate Password** to create a random password.

   > **Tip:**
   >
   > If you have created a password before, you can either use the original password or click **Reset Password** to generate a new one.

   The connection string looks like this:

   ```
   mysql://[username]:[password]@[host]/[database]
   ```

### Step 3. Create an edge function

1. Create a table in your Starter cluster.

   You can use SQL Editor in the TiDB Cloud console to execute SQL statements. Example:

   ```sql
   CREATE TABLE `test`.`users` (
    `id` BIGINT PRIMARY KEY auto_increment,
    `full_name` TEXT,
    `phone` VARCHAR(256)
   );
   ```

2. In the `app` directory of your project, create a file `/api/edge-function-example/route.ts` and add the following code:

   ```ts
   import { NextResponse } from 'next/server'
   import type { NextRequest } from 'next/server'
   import { connect } from '@tidbcloud/serverless'
   import { drizzle } from 'drizzle-orm/tidb-serverless'
   import { mysqlTable, serial, text, varchar } from 'drizzle-orm/mysql-core'

   export const runtime = 'edge'

   const client = connect({ url: process.env.DATABASE_URL })
   const db = drizzle(client)

   export const users = mysqlTable('users', {
     id: serial('id').primaryKey(),
     fullName: text('full_name'),
     phone: varchar('phone', { length: 256 })
   })
   export type User = typeof users.$inferSelect
   export type NewUser = typeof users.$inferInsert

   export async function GET(request: NextRequest) {
     const user: NewUser = { fullName: 'John Doe', phone: '123-456-7890' }
     await db.insert(users).values(user)
     const result: User[] = await db.select().from(users)
     return NextResponse.json(result)
   }
   ```

3. Test your code locally:

   ```shell
   export DATABASE_URL='mysql://[username]:[password]@[host]/[database]'
   next dev
   ```

4. Navigate to `http://localhost:3000/api/edge-function-example` to get the response from your route.

### Step 4. Deploy your code to Vercel

1. Deploy your code to Vercel with the `DATABASE_URL` environment variable:

   ```shell
   vercel -e DATABASE_URL='mysql://[username]:[password]@[host]/[database]' --prod
   ```

2. Navigate to the `${Your-URL}/api/edge-function-example` page to get the response from your route.

## What's next

- Learn more about [Drizzle](https://orm.drizzle.team/docs/overview) and [drizzle-orm/tidb-serverless](https://orm.drizzle.team/docs/get-started-mysql#tidb-serverless).
- Learn how to [integrate TiDB Cloud with Vercel](https://docs.pingcap.com/tidbcloud/integrate-tidbcloud-with-vercel).
