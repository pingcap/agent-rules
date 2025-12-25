# TiDB Cloud Serverless Driver Node.js Tutorial

## Table of contents

- [Before you begin](#before-you-begin)
- [Step 1. Create a local Node.js project](#step-1-create-a-local-nodejs-project)
- [Step 2. Use the serverless driver](#step-2-use-the-serverless-driver)
- [Compatibility with earlier versions of Node.js](#compatibility-with-earlier-versions-of-nodejs)

This tutorial describes how to use TiDB Cloud serverless driver in a local Node.js project.

> **Note:**
>
> - In addition to Starter clusters, the steps in this document also work with Essential clusters.
> - To learn how to use TiDB Cloud serverless driver with Cloudflare Workers, Vercel Edge Functions, and Netlify Edge Functions, check out [Insights into Automotive Sales](https://car-sales-insight.vercel.app/) and the [sample repository](https://github.com/tidbcloud/car-sales-insight).

## Before you begin

To complete this step-by-step tutorial, you need the following:

- [Node.js](https://nodejs.org/en) >= 18.0.0.
- [npm](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) or your preferred package manager.
- A Starter cluster. If you don't have any, create a Starter cluster in TiDB Cloud.

## Step 1. Create a local Node.js project

1. Create a project named `node-example`:

   ```shell
   mkdir node-example
   cd node-example
   ```

2. Install the TiDB Cloud serverless driver using npm or your preferred package manager.

   The following command takes installation with npm as an example. Executing this command will create a `node_modules` directory and a `package.json` file in your project directory.

   ```
   npm install @tidbcloud/serverless
   ```

## Step 2. Use the serverless driver

The serverless driver supports both CommonJS and ES modules. The following steps take the usage of the ES module as an example.

1. On the overview page of your Starter cluster, click **Connect** in the upper-right corner, and then get the connection string for your database from the displayed dialog. The connection string looks like this:

   ```
   mysql://[username]:[password]@[host]/[database]
   ```

2. In the `package.json` file, specify the ES module by adding `type: "module"`.

   For example:

   ```json
   {
     "type": "module",
     "dependencies": {
       "@tidbcloud/serverless": "^0.0.7"
     }
   }
   ```

3. Create a file named `index.js` in your project directory and add the following code:

   ```js
   import { connect } from '@tidbcloud/serverless'

   const conn = connect({ url: 'mysql://[username]:[password]@[host]/[database]' }) // replace with your Starter cluster info
   console.log(await conn.execute('show tables'))
   ```

4. Run your project with the following command:

   ```
   node index.js
   ```

## Compatibility with earlier versions of Node.js

If you are using Node.js earlier than 18.0.0, which does not have a global `fetch` function, take the following steps to get `fetch`:

1. Install a package that provides `fetch`, such as `undici`:

   ```
   npm install undici
   ```

2. Pass the `fetch` function to the `connect` function:

   ```js
   import { connect } from '@tidbcloud/serverless'
   import { fetch } from 'undici'

   const conn = connect({ url: 'mysql://[username]:[password]@[host]/[database]', fetch })
   ```
