---
title: TiDB Cloud SSL Verification (Connection Gotchas)
---

# TiDB Cloud SSL Verification (Connection Gotchas)

When connecting to TiDB Cloud over the MySQL protocol, enable TLS and enforce:

- server certificate verification
- server identity (hostname) verification

If SSL verification is missing or misconfigured, you might see connection failures even before you can run SQL.

## Detect TiDB Cloud gateway hosts

If the host matches this pattern (Python regex):

```python
r"gateway\\d{2}\\.(.+)\\.(prod|dev|staging)\\.(shared\\.)?(aws|alicloud)\\.tidbcloud\\.com"
```

assume TiDB Cloud requirements apply.

## Common client settings

MySQL CLI:

```bash
mysql ... --ssl-mode=VERIFY_IDENTITY
```

MariaDB CLI:

```bash
mariadb ... --ssl-verify-server-cert
```

Node.js (mysql2):

```js
ssl: {
  minVersion: 'TLSv1.2',
  rejectUnauthorized: true,
},
```

Prisma (connection string query param):

```text
sslaccept=strict
```

Go (database/sql + go-sql-driver/mysql):

Register a TLS config and reference it via `tls=` in the DSN:

```go
mysql.RegisterTLSConfig("tidb", &tls.Config{
  MinVersion: tls.VersionTLS12,
  ServerName: "gateway01.ap-southeast-1.prod.aws.tidbcloud.com",
})

db, err := sql.Open(
  "mysql",
  "USER:PASSWORD@tcp(gateway01.ap-southeast-1.prod.aws.tidbcloud.com:4000)/DB?tls=tidb",
)
```

Rails (ActiveRecord + mysql2, database.yml URL):

```yaml
development:
  adapter: mysql2
  url: mysql2://USER:PASSWORD@gateway01.ap-southeast-1.prod.aws.tidbcloud.com:4000/DB?ssl_mode=verify_identity
```

MySQL Connector/J (JDBC URL params):

```text
sslMode=VERIFY_IDENTITY
```

## DSN / URL query parameters (generic)

If you are building a connection string and can only toggle via query parameters, append:

```text
ssl_verify_cert=true&ssl_verify_identity=true
```

Use this especially when the host matches the gateway pattern above.
