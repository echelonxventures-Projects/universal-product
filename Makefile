.PHONY: dev build test lint clean docker-build docker-push

dev:
	npm run dev

build:
	npm run build

test:
	npm test

lint:
	npm run lint

clean:
	rm -rf node_modules dist

docker-build:
	docker build -t uci-platform:latest .

docker-push:
	docker push uci-platform:latest

terraform-init:
	cd infrastructure/terraform && terraform init

terraform-apply:
	cd infrastructure/terraform && terraform apply
