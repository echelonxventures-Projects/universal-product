# ucos CLI image: static binary on scratch, non-root, reproducible flags. Signed and attested by release.yml.
FROM golang:1.26.6-alpine@sha256:3889b425f035be855a72fb4755265311293b6d414521f0a519d819df32222d83 AS build
WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download
COPY . .
ARG VERSION=dev
RUN CGO_ENABLED=0 GOFLAGS=-mod=readonly go build -trimpath -buildvcs=false \
      -ldflags "-s -w -X main.version=${VERSION}" -o /out/ucos ./cmd/ucos

FROM scratch
COPY --from=build /out/ucos /ucos
USER 65532:65532
ENTRYPOINT ["/ucos"]
