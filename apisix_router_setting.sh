# Usage: apisix_router_setting.sh [--skip-wait]
# ./apisix_router_setting.sh             
# ./apisix_router_setting.sh --skip-wait

SKIP_WAIT=false
for arg in "$@"; do
  case "$arg" in
    --skip-wait) SKIP_WAIT=true ;;
  esac
done

source ./configure.sh
export APISIX_ADDR="127.0.0.1:${PORT_APISIX_API}"
export AUTH="X-API-KEY: ${APIKEY_APISIX_ADMIN}"
export TYPE="Content-Type: application/json"

export OIDC_CLIENT_ID="${OIDC_CLIENT_ID}"
export OIDC_CLIENT_SECRET="${OIDC_CLIENT_SECRET}"
export OIDC_DISCOVERY_ADDR="${OIDC_DISCOVERY_ADDR}"
export OIDC_INTROSPECTION_ENDPOINT="${OIDC_INTROSPECTION_ENDPOINT}"

# Wait until APISIX Admin API is ready
wait_for_apisix() {
  local max_retries=30
  local interval=3
  local attempt=0
  echo "Waiting for APISIX Admin API to be ready (http://${APISIX_ADDR}) ..."
  while [ $attempt -lt $max_retries ]; do
    local http_code
    http_code=$(curl -s -o /dev/null -w "%{http_code}" \
      -H "${AUTH}" \
      "http://${APISIX_ADDR}/apisix/admin/routes")
    if [ "$http_code" = "200" ]; then
      echo "APISIX Admin API is ready (attempt $((attempt + 1)))"
      return 0
    fi
    attempt=$((attempt + 1))
    echo "APISIX not ready yet (HTTP $http_code), retrying in ${interval}s (${attempt}/${max_retries}) ..."
    sleep $interval
  done
  echo "ERROR: APISIX Admin API was not ready within $((max_retries * interval))s, aborting route setup." >&2
  exit 1
}

if [ "$SKIP_WAIT" = false ]; then
  wait_for_apisix
fi

./scripts/apisix_router/ai-gateway.sh
./scripts/apisix_router/casdoor.sh
./scripts/apisix_router/chatrag.sh
./scripts/apisix_router/completion-v2.sh
./scripts/apisix_router/costrict-apps.sh
./scripts/apisix_router/credit-manager.sh
./scripts/apisix_router/issue.sh
./scripts/apisix_router/oidc-auth.sh
./scripts/apisix_router/quota-manager.sh

echo "APISIX routes setup completed."