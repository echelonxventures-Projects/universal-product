/* node:sqlite (lib/db.js) is a built-in since Node 22.5 — anything older dies at boot
   with "Cannot find module 'node:sqlite'", and package.json pins >=22.5. */
FROM node:22-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --omit=dev

COPY . .

/* the keyring (data/master.json) and the registry seal (data/registry.json) live here;
   mount a volume or every redeploy loses the ability to decrypt secrets and verify the seal */
RUN mkdir -p /app/data
VOLUME /app/data

ENV NODE_ENV=production
ENV PORT=3000

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD wget -qO- http://localhost:3000/healthz || exit 1

CMD ["node", "server.js"]
