#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUNTIME="${CONTAINER_RUNTIME:-docker}"
REGISTRY="${IMAGE_REGISTRY:?Set IMAGE_REGISTRY (e.g. ghcr.io/your-org)}"
TAG="${1:-$(git -C "${ROOT_DIR}" rev-parse --short HEAD)}"

CONTROLLER_IMAGE="${REGISTRY}/devbox-controller:${TAG}"
RUNNER_IMAGE="${REGISTRY}/devbox-runner:${TAG}"

echo "Building controller image: ${CONTROLLER_IMAGE}"
cd "${ROOT_DIR}"
npm run build
${RUNTIME} build -t "${CONTROLLER_IMAGE}" -f docker/controller.Dockerfile .

echo "Building runner image: ${RUNNER_IMAGE}"
${RUNTIME} build -t "${RUNNER_IMAGE}" -f docker/runner.Dockerfile .

echo "Pushing images"
${RUNTIME} push "${CONTROLLER_IMAGE}"
${RUNTIME} push "${RUNNER_IMAGE}"

echo "Done"
echo "  ${CONTROLLER_IMAGE}"
echo "  ${RUNNER_IMAGE}"
