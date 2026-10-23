# node:sqlite (lib/db.js) is built in, unflagged, since Node 22.13 — anything older dies
# at boot (server.js says so), and package.json pins >=22.13. node:22-alpine is current 22.x.
FROM node:22-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --omit=dev

COPY . .

# the keyring (data/master.json) and the registry seal (data/registry.json) live here;
# mount a volume or every redeploy loses the ability to decrypt secrets and verify the seal
# the server runs as the image's unprivileged node user, never root: a compromise of the
# process cannot rewrite the code or the system. It owns only its data directory.
RUN mkdir -p /app/data && chown -R node:node /app/data
VOLUME /app/data
USER node

ENV NODE_ENV=production
ENV PORT=3000

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD wget -qO- http://localhost:3000/healthz || exit 1

CMD ["node", "server.js"]
