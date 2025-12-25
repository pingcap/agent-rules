# TiDB Cloud Serverless Driver Kysely Tutorial

## Table of contents

- [Use TiDB Cloud Kysely dialect in Node.js environments](#use-tidb-cloud-kysely-dialect-in-nodejs-environments)
  - [Before you begin](#before-you-begin)
  - [Step 1. Create a project](#step-1-create-a-project)
  - [Step 2. Set the environment](#step-2-set-the-environment)
  - [Step 3. Use Kysely to query data](#step-3-use-kysely-to-query-data)
  - [Step 4. Run the Typescript code](#step-4-run-the-typescript-code)
- [Use TiDB Cloud Kysely dialect in edge environments](#use-tidb-cloud-kysely-dialect-in-edge-environments)
  - [Before you begin](#before-you-begin-1)
  - [Step 1. Create a project](#step-1-create-a-project-1)
  - [Step 2. Set the environment](#step-2-set-the-environment-1)
  - [Step 3. Create an edge function](#step-3-create-an-edge-function)
  - [Step 4. Deploy your code to Vercel](#step-4-deploy-your-code-to-vercel)
- [What's next](#whats-next)

[Kysely](https://kysely.dev/docs/intro) is a type-safe and autocompletion-friendly TypeScript SQL query builder. TiDB Cloud offers [@tidbcloud/kysely](https://github.com/tidbcloud/kysely), enabling you to use Kysely over HTTPS with TiDB Cloud serverless driver. Compared with the traditional TCP way, @tidbcloud/kysely brings:

- Better performance in serverless environments.
- Ability to use Kysely in edge environments.

This tutorial describes how to use TiDB Cloud serverless driver with Kysely in Node.js environments and edge environments.

## Use TiDB Cloud Kysely dialect in Node.js environments

### Before you begin

To complete this tutorial, you need the following:

- [Node.js](https://nodejs.org/en) >= 18.0.0.
- [npm](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) or your preferred package manager.
- A Starter cluster. If you don't have any, create a Starter cluster in TiDB Cloud.

### Step 1. Create a project

1. Create a project named `kysely-node-example`:

   ```
   mkdir kysely-node-example
   cd kysely-node-example
   ```

2. Install the `kysely`, `@tidbcloud/kysely`, and `@tidbcloud/serverless` packages:

   ```
   npm install kysely @tidbcloud/kysely @tidbcloud/serverless
   ```

3. In the root directory of your project, locate the `package.json` file, and then specify ES modules by adding `"type": "module"`:

   ```json
   {
     "type": "module",
     "dependencies": {
       "@tidbcloud/kysely": "^0.0.4",
       "@tidbcloud/serverless": "^0.0.7",
       "kysely": "^0.26.3"
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

1. On the overview page of your Starter cluster, click **Connect** in the upper-right corner, and then get the connection string for your database. The connection string looks like this:

   ```
   mysql://[username]:[password]@[host]/[database]
   ```

2. Set the environment variable `DATABASE_URL` in your local environment:

   ```bash
   export DATABASE_URL='mysql://[username]:[password]@[host]/[database]'
   ```

### Step 3. Use Kysely to query data

1. Create a table in your Starter cluster and insert some data.

   You can use SQL Editor in the TiDB Cloud console to execute SQL statements. Example:

   ```sql
   CREATE TABLE `test`.`person`  (
     `id` int(11) NOT NULL AUTO_INCREMENT,
     `name` varchar(255) NULL DEFAULT NULL,
     `gender` enum('male','female') NULL DEFAULT NULL,
     PRIMARY KEY (`id`) USING BTREE
   );

   insert into test.person values (1,'pingcap','male')
   ```

2. In the root directory of your project, create a file named `hello-world.ts` and add the following code:

   ```ts
   import { Kysely, GeneratedAlways, Selectable } from 'kysely'
   import { TiDBServerlessDialect } from '@tidbcloud/kysely'

   interface Database {
     person: PersonTable
   }

   interface PersonTable {
     id: GeneratedAlways<number>
     name: string
     gender: 'male' | 'female'
   }

   const db = new Kysely<Database>({
     dialect: new TiDBServerlessDialect({
       url: process.env.DATABASE_URL
     })
   })

   type Person = Selectable<PersonTable>
   export async function findPeople(criteria: Partial<Person> = {}) {
     let query = db.selectFrom('person')

     if (criteria.name) {
       query = query.where('name', '=', criteria.name)
     }

     return await query.selectAll().execute()
   }

   console.log(await findPeople())
   ```

### Step 4. Run the Typescript code

1. Install `ts-node` and `@types/node`:

   ```
   npm install -g ts-node
   npm i --save-dev @types/node
   ```

2. Run the Typescript code:

   ```
   ts-node --esm hello-world.ts
   ```

## Use TiDB Cloud Kysely dialect in edge environments

This section takes the TiDB Cloud Kysely dialect in Vercel Edge Function as an example.

### Before you begin

To complete this tutorial, you need the following:

- A [Vercel](https://vercel.com/docs) account that provides edge environment.
- [npm](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) or your preferred package manager.
- A Starter cluster. If you don't have any, create a Starter cluster in TiDB Cloud.

### Step 1. Create a project

1. Install the Vercel CLI:

   ```
   npm i -g vercel@latest
   ```

2. Create a Next.js project called `kysely-example`:

   ```
   npx create-next-app@latest kysely-example --ts --no-eslint --tailwind --no-src-dir --app --import-alias "@/*"
   cd kysely-example
   ```

3. Install the `kysely`, `@tidbcloud/kysely`, and `@tidbcloud/serverless` packages:

   ```
   npm install kysely @tidbcloud/kysely @tidbcloud/serverless
   ```

### Step 2. Set the environment

On the overview page of your Starter cluster, click **Connect** in the upper-right corner, and then get the connection string for your database. The connection string looks like this:

```
mysql://[username]:[password]@[host]/[database]
```

### Step 3. Create an edge function

1. Create a table in your Starter cluster and insert some data.

   You can use SQL Editor in the TiDB Cloud console to execute SQL statements. Example:

   ```sql
   CREATE TABLE `test`.`person`  (
     `id` int(11) NOT NULL AUTO_INCREMENT,
     `name` varchar(255) NULL DEFAULT NULL,
     `gender` enum('male','female') NULL DEFAULT NULL,
     PRIMARY KEY (`id`) USING BTREE
   );

   insert into test.person values (1,'pingcap','male')
   ```

2. In the `app` directory of your project, create a file `/api/edge-function-example/route.ts` and add the following code:

   ```ts
   import { NextResponse } from 'next/server'
   import type { NextRequest } from 'next/server'
   import { Kysely, GeneratedAlways, Selectable } from 'kysely'
   import { TiDBServerlessDialect } from '@tidbcloud/kysely'

   export const runtime = 'edge'

   interface Database {
     person: PersonTable
   }

   interface PersonTable {
     id: GeneratedAlways<number>
     name: string
     gender: 'male' | 'female' | 'other'
   }

   const db = new Kysely<Database>({
     dialect: new TiDBServerlessDialect({
       url: process.env.DATABASE_URL
     })
   })

   type Person = Selectable<PersonTable>
   async function findPeople(criteria: Partial<Person> = {}) {
     let query = db.selectFrom('person')

     if (criteria.name) {
       query = query.where('name', '=', criteria.name)
     }

     return await query.selectAll().execute()
   }

   export async function GET(request: NextRequest) {
     const searchParams = request.nextUrl.searchParams
     const query = searchParams.get('query')

     let response = null
     if (query) {
       response = await findPeople({ name: query })
     } else {
       response = await findPeople()
     }

     return NextResponse.json(response)
   }
   ```

3. Test your code locally:

   ```
   export DATABASE_URL='mysql://[username]:[password]@[host]/[database]'
   next dev
   ```

4. Navigate to `http://localhost:3000/api/edge-function-example` to get the response from your route.

### Step 4. Deploy your code to Vercel

1. Deploy your code to Vercel with the `DATABASE_URL` environment variable:

   ```
   vercel -e DATABASE_URL='mysql://[username]:[password]@[host]/[database]' --prod
   ```

2. Navigate to the `${Your-URL}/api/edge-function-example` page to get the response from your route.

## What's next

- Learn more about [Kysely](https://kysely.dev/docs/intro) and [@tidbcloud/kysely](https://github.com/tidbcloud/kysely)
- Learn how to [integrate TiDB Cloud with Vercel](https://docs.pingcap.com/tidbcloud/integrate-tidbcloud-with-vercel)
