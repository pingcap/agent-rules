# Troubleshooting (Prisma + TiDB)

## Cannot connect / timeout

- Confirm endpoint type (public vs private/VPC) matches where the app runs.
- Confirm host/port/user/password are correct in `DATABASE_URL`.
- If using TiDB Cloud Dedicated, ensure traffic filters allow your client IP.

## TLS errors (TiDB Cloud public endpoint)

- Ensure `DATABASE_URL` includes `sslaccept=strict`.
- If using a downloaded CA, ensure `sslcert=/absolute/path/to/ca.pem` points to a readable file.

## Prisma Client errors

- If you see "Cannot find module '@prisma/client'": run `npm i @prisma/client`.
- If you see client generation errors: run `npx prisma generate` (or `npx prisma migrate dev` which also generates).

