# Local development stack (deploy/local/compose.yaml).
COMPOSE := docker compose -f compose.yaml
.PHONY: up down logs ps reset
up:     ## start everything, wait until healthy, apply the kernel schema
	$(COMPOSE) up -d --wait
	$(COMPOSE) run --rm --build migrate
down:   ## stop
	$(COMPOSE) down
reset:  ## stop and delete data (the schema is re-applied by the next `make up`)
	$(COMPOSE) down -v
logs:
	$(COMPOSE) logs -f
ps:
	$(COMPOSE) ps
