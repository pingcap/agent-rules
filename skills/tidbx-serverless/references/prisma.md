# TiDB Cloud Serverless Driver Prisma Tutorial

## Table of contents

- [Install](#install)
- [Enable `driverAdapters`](#enable-driveradapters)
- [Initialize Prisma Client](#initialize-prisma-client)
- [Use the Prisma adapter in Node.js environments](#use-the-prisma-adapter-in-nodejs-environments)
  - [Before you begin](#before-you-begin)
  - [Step 1. Create a project](#step-1-create-a-project)
  - [Step 2. Set the environment](#step-2-set-the-environment)
  - [Step 3. Define your schema](#step-3-define-your-schema)
  - [Step 4. Execute CRUD operations](#step-4-execute-crud-operations)
- [Use the Prisma adapter in edge environments](#use-the-prisma-adapter-in-edge-environments)

[Prisma](https://www.prisma.io/docs) is an open source next-generation ORM that helps developers interact with their database in an intuitive, efficient, and safe way. TiDB Cloud offers [@tidbcloud/prisma-adapter](https://github.com/tidbcloud/prisma-adapter), enabling you to use Prisma Client over HTTPS with TiDB Cloud serverless driver. Compared with the traditional TCP way, @tidbcloud/prisma-adapter brings:

- Better performance of Prisma Client in serverless environments
- Ability to use Prisma Client in edge environments

This tutorial describes how to use @tidbcloud/prisma-adapter in serverless environments and edge environments.

> **Tip:**
>
> In addition to Starter clusters, the steps in this document also work with Essential clusters.

## Install

You need to install both @tidbcloud/prisma-adapter and @tidbcloud/serverless. You can install them using npm or your preferred package manager.

```shell
npm install @tidbcloud/prisma-adapter
npm install @tidbcloud/serverless
```

## Enable `driverAdapters`

To use the Prisma adapter, enable the `driverAdapters` feature in `schema.prisma`:

```prisma
generator client {
  provider        = "prisma-client-js"
  previewFeatures = ["driverAdapters"]
}

datasource db {
  provider = "mysql"
  url      = env("DATABASE_URL")
}
```

## Initialize Prisma Client

For @tidbcloud/prisma-adapter earlier than v6.6.0:

```js
import { connect } from '@tidbcloud/serverless'
import { PrismaTiDBCloud } from '@tidbcloud/prisma-adapter'
import { PrismaClient } from '@prisma/client'

const connection = connect({ url: `${DATABASE_URL}` })
const adapter = new PrismaTiDBCloud(connection)
const prisma = new PrismaClient({ adapter })
```

For @tidbcloud/prisma-adapter v6.6.0 or later:

```js
import { PrismaTiDBCloud } from '@tidbcloud/prisma-adapter'
import { PrismaClient } from '@prisma/client'

const adapter = new PrismaTiDBCloud({ url: `${DATABASE_URL}` })
const prisma = new PrismaClient({ adapter })
```

Then, queries from Prisma Client can be sent to the TiDB Cloud serverless driver for processing.

## Use the Prisma adapter in Node.js environments

### Before you begin

To complete this tutorial, you need the following:

- [Node.js](https://nodejs.org/en) >= 18.0.0.
- [npm](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) or your preferred package manager.
- A Starter cluster. If you don't have any, create a Starter cluster in TiDB Cloud.

### Step 1. Create a project

1. Create a project named `prisma-example`:

   ```
   mkdir prisma-example
   cd prisma-example
   ```

2. Install the adapter, serverless driver, and Prisma CLI:

   ```
   npm install @tidbcloud/prisma-adapter
   npm install @tidbcloud/serverless
   npm install prisma --save-dev
   ```

3. In `package.json`, specify ES modules by adding `type: "module"`:

   ```json
   {
     "type": "module",
     "dependencies": {
       "@prisma/client": "^6.6.0",
       "@tidbcloud/prisma-adapter": "^6.6.0",
       "@tidbcloud/serverless": "^0.1.0"
     },
     "devDependencies": {
       "prisma": "^6.6.0"
     }
   }
   ```

### Step 2. Set the environment

1. On the overview page of your Starter cluster, click **Connect** in the upper-right corner, and then get the connection string for your database. The connection string looks like this:

   ```
   mysql://[username]:[password]@[host]:4000/[database]?sslaccept=strict
   ```

2. In the root directory of your project, create a file named `.env`, define an environment variable named `DATABASE_URL`, and replace the placeholders:

   ```dotenv
   DATABASE_URL='mysql://[username]:[password]@[host]:4000/[database]?sslaccept=strict'
   ```

   > **Note:**
   >
   > `@tidbcloud/prisma-adapter` only supports the use of Prisma Client over HTTPS. For Prisma Migrate and Prisma Introspection, the traditional TCP connection is still used. If you only need Prisma Client, you can simplify `DATABASE_URL` to `mysql://[username]:[password]@[host]/[database]`.

3. Install `dotenv` to load the environment variable from `.env`:

   ```
   npm install dotenv
   ```

### Step 3. Define your schema

1. Create a file named `schema.prisma` and include the `driverAdapters` preview feature and the `DATABASE_URL` env var:

   ```prisma
   generator client {
     provider        = "prisma-client-js"
     previewFeatures = ["driverAdapters"]
   }

   datasource db {
     provider = "mysql"
     url      = env("DATABASE_URL")
   }
   ```

2. Define a data model for your database table. Example:

   ```prisma
   model user {
     id    Int     @id @default(autoincrement())
     email String? @unique(map: "uniq_email") @db.VarChar(255)
     name  String? @db.VarChar(255)
   }
   ```

3. Synchronize your database with the Prisma schema:

   ```
   npx prisma db push
   ```

4. Generate Prisma Client:

   ```
   npx prisma generate
   ```

### Step 4. Execute CRUD operations

1. Create a file named `hello-word.js` and initialize Prisma Client:

   ```js
   import { PrismaTiDBCloud } from '@tidbcloud/prisma-adapter'
   import { PrismaClient } from '@prisma/client'
   import dotenv from 'dotenv'

   dotenv.config()
   const connectionString = `${process.env.DATABASE_URL}`

   const adapter = new PrismaTiDBCloud({ url: connectionString })
   const prisma = new PrismaClient({ adapter })
   ```

2. Execute CRUD operations:

   ```js
   const user = await prisma.user.create({
     data: {
       email: 'test@pingcap.com',
       name: 'test'
     }
   })
   console.log(user)

   console.log(await prisma.user.findMany())

   await prisma.user.delete({
     where: { id: user.id }
   })
   ```

3. Execute transaction operations:

   ```js
   const createUser1 = prisma.user.create({
     data: { email: 'test1@pingcap.com', name: 'test1' }
   })
   const createUser2 = prisma.user.create({
     data: { email: 'test1@pingcap.com', name: 'test1' }
   })
   const createUser3 = prisma.user.create({
     data: { email: 'test2@pingcap.com', name: 'test2' }
   })

   try {
     await prisma.$transaction([createUser1, createUser2])
   } catch (e) {
     console.log(e)
   }

   try {
     await prisma.$transaction([createUser2, createUser3])
   } catch (e) {
     console.log(e)
   }
   ```

## Use the Prisma adapter in edge environments

You can use @tidbcloud/prisma-adapter v5.11.0 or later in edge environments such as Vercel Edge Functions and Cloudflare Workers.

- [Vercel Edge Function example](https://github.com/tidbcloud/serverless-driver-example/tree/main/prisma/prisma-vercel-example)
- [Cloudflare Workers example](https://github.com/tidbcloud/serverless-driver-example/tree/main/prisma/prisma-cloudflare-worker-example)
