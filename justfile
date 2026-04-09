set dotenv-load

# start local k8s development with Tilt (hot-reload, logs, monitoring)
dev-k8s:
    tilt up

# start the bot locally (direct node process, fastest for controller-only testing)
dev:
    npx tsx src/index.ts --config config.local.yaml

# build typescript
build:
    npm run build

# run tests
test:
    npm test

# typecheck without emitting
typecheck:
    npm run typecheck

# format source files
fmt:
    npm run format

runtime := env("CONTAINER_RUNTIME", "docker")

# build the runner container image
build-runner tag='latest':
    {{runtime}} build -t devbox-runner:{{tag}} -f docker/runner.Dockerfile .

# build the controller container image (runs npm build first)
build-controller tag='latest': build
    {{runtime}} build -t devbox-controller:{{tag}} -f docker/controller.Dockerfile .

# build both controller and runner images
build-images tag='latest': (build-controller tag) (build-runner tag)

# legacy alias
container-build: build-runner

# build and push controller + runner images (tag defaults to git short sha)
build-push tag='':
    if [ -n "{{tag}}" ]; then ./scripts/build-push.sh "{{tag}}"; else ./scripts/build-push.sh; fi

# --- Docker Compose (local verification) ---

data_root := env("DEVBOX_DATA_ROOT", "/data/devbox-agent")

# start the compose stack
compose-up *args='':
    {{runtime}} compose up -d {{args}}

# stop the compose stack
compose-down:
    {{runtime}} compose down --remove-orphans

# show compose logs
compose-logs *args='':
    {{runtime}} compose logs -f {{args}}

# remove persisted data (store, agents, sessions, ipc)
compose-clean-data:
    rm -rf "{{data_root}}/store" "{{data_root}}/agents" "{{data_root}}/data"
    @echo "Cleaned data under {{data_root}}"

# stop stack and remove all persisted data
compose-clean: compose-down compose-clean-data
