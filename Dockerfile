# The base is the deploy.container resolution in technology.lock.json (tag and digest): a
# plain docker build cannot read the lock, so the line is written here and
# node scripts/technology.js check fails when it differs. The runtime it carries is the primary
# CI lane. To change it, update the registry (lib/seed/technology.json and its discovery
# snapshot), regenerate the lock, and make this line match.
FROM node:22.23.4-alpine@sha256:fe4f6d74e20370acb04ad889077d14d0f64a9c8ea6a42bc60cddf1e844699914

WORKDIR /app

COPY package*.json ./
RUN npm ci --omit=dev && npm cache clean --force

COPY . .

# Runs as the image's unprivileged `node` user, never root: a compromise of the process
# cannot rewrite the code or the system. The code stays root-owned and read-only to it; the
# only writable places are
#   /app/data      the database, the keyring (master.json), the registry seal key
#                  (registry.json), TLS material and exports — mount a volume, or every
#                  redeploy loses the ability to decrypt secrets and verify the seal
#   /app/_registry the runtime writes the compiled registry (canonical.lxr/.json) here; the
#                  sticky bit lets it create those without being able to delete the sources
RUN mkdir -p /app/data && chown node:node /app/data && chmod 700 /app/data \
 && chgrp node /app/_registry && chmod 1775 /app/_registry
VOLUME /app/data
USER node

ENV NODE_ENV=production
ENV PORT=3000

EXPOSE 3000

# liveness only (/healthz). Point a load balancer's readiness check at /readyz, which goes
# 503 while draining for shutdown or when the database does not answer. The first boot
# seeds the catalogue, hence the long start period.
HEALTHCHECK --interval=30s --timeout=5s --start-period=90s --retries=3 \
  CMD wget -qO- http://localhost:3000/healthz || exit 1

CMD ["node", "server.js"]
