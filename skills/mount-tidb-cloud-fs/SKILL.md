---
name: mount-tidb-cloud-fs
description: Mount an existing TiDB Cloud Filesystem to a local directory with the ti CLI in a clean or ephemeral environment, using TI_FS_TOKEN and TI_REGION_CODE without ti configure, TiDB Cloud API keys, a profile, or TI_FS_FILE_SYSTEM_ID. Use when an agent needs to mount, access, or persist a Drive9-backed workspace in a sandbox, CI job, container, or local machine.
---

# Mount a TiDB Cloud Filesystem

Mount an existing TiDB Cloud Filesystem without configuring a `ti` profile. Do not
use this skill to create or delete a file system or to manage its tokens.

This token-only workflow requires `ti` v0.2.1 or later. The CLI is currently in
preview; if installed behavior differs, run `ti fs mount-file-system --help` and
check the official repository: <https://github.com/tidbcloud/ti-cli>.

## Required inputs

| Input | Required | Purpose |
| --- | --- | --- |
| `TI_FS_TOKEN` | yes | Owner or scoped Filesystem token. It authenticates the request and identifies the file system. |
| `TI_REGION_CODE` | yes | Routing region, for example `aws-us-east-1`. Use `--region` only as an explicit alternative. |
| `MOUNT_PATH` | yes | Local directory where the file system will be mounted. |
| `TI_FS_FILE_SYSTEM_ID` | no | Optional consistency assertion. `ti` normally derives the ID from the token. |

The token does not remove the need for an explicit region in a clean environment.
Do not run `ti configure` or supply TiDB Cloud API keys for this workflow.

## Workflow

### 1. Validate the inputs

```bash
: "${TI_FS_TOKEN:?Set TI_FS_TOKEN to an existing Filesystem token}"
: "${TI_REGION_CODE:?Set TI_REGION_CODE to the Filesystem region}"
: "${MOUNT_PATH:?Set MOUNT_PATH to the local mount directory}"
```

Never print or log `TI_FS_TOKEN`. Let `ti` validate the token format and its remote
permissions.

### 2. Install or verify `ti`

```bash
if ! command -v ti >/dev/null 2>&1; then
  curl -fsSL https://github.com/tidbcloud/ti-cli/releases/latest/download/install.sh \
    | sh -s -- --yes
  export PATH="$HOME/.ti/bin:$PATH"
fi

ti --version
```

Require v0.2.1 or later. If an older version is installed, upgrade it before
mounting with `ti update`.

### 3. Prepare the mount path and driver

```bash
mkdir -p -- "$MOUNT_PATH"
```

Prefer a new or empty directory. Do not hide existing local files by mounting over
a non-empty directory unless the user explicitly intends that behavior.

Keep the default `--driver auto` unless a specific driver is required:

- Linux requires `/dev/fuse` plus `fusermount3` or `fusermount`. Installing `fuse3`
  is not enough in a container unless the container can access `/dev/fuse` and has
  the permissions needed to mount it. WebDAV is not a Linux fallback in v0.2.3.
- macOS automatically uses macFUSE when available and otherwise uses the system
  WebDAV mount helper. Install macFUSE only when FUSE behavior is required.
- Windows local mounting is not supported by the v0.2.3 implementation. Use
  Filesystem data-plane commands or mount from a supported Linux/macOS host.

### 4. Mount the file system

```bash
ti fs mount-file-system \
  --mount-path "$MOUNT_PATH" \
  --ready-timeout 60s
```

Rely on the environment variables instead of passing `--fs-token`; command-line
arguments can be exposed through shell history or process inspection.

The mount runs in the background and returns after it is ready. Useful options:

- Add `--read-only` for inspection or when the token has no write permission.
- Add `--foreground` when debugging the mount process.
- Add `--driver fuse` or `--driver webdav` only after checking platform support.
- Use `--query` and `--output` when an agent needs a specific machine-readable
  result.

### 5. Verify access

```bash
ls -la -- "$MOUNT_PATH"
```

If write access is expected, create a unique probe rather than overwriting a fixed
path. Skip this check for a read-only mount or a token without `write` permission.

```bash
probe_path="$(mktemp "$MOUNT_PATH/.ti-mount-probe.XXXXXX")"
printf 'mount probe\n' > "$probe_path"
cat -- "$probe_path"
rm -f -- "$probe_path"
```

### 6. Unmount when finished

```bash
ti fs unmount-file-system --mount-path "$MOUNT_PATH"
```

## Troubleshooting

- A missing region fails even when the token is valid. Set `TI_REGION_CODE` or pass
  `--region <code>`.
- A supplied `TI_FS_FILE_SYSTEM_ID` must match the ID derived from the token.
- A scoped token can access only its allowed paths and operations. Do not assume it
  permits writes.
- On Linux, confirm both `/dev/fuse` and `fusermount3` or `fusermount` are available.
  If FUSE cannot be exposed, a local mount is not available; use `ti fs` data-plane
  commands instead.
- If a background mount times out, inspect the log path reported by `ti` and retry
  with `--foreground`.
