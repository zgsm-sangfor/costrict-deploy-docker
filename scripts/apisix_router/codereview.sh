#!/bin/sh


curl -i http://$APISIX_ADDR/apisix/admin/upstreams -H "$AUTH" -H "$TYPE" -X PUT -d '{
    "id": "review-manager",
    "nodes": {
      "review-manager:8080": 1
    },
    "type": "roundrobin"
  }'

curl -i http://$APISIX_ADDR/apisix/admin/upstreams -H "$AUTH" -H "$TYPE" -X PUT -d '{
    "id": "issue-manager",
    "nodes": {
      "issue-manager:8080": 1
    },
    "type": "roundrobin"
  }'

curl -i http://$APISIX_ADDR/apisix/admin/routes -H "$AUTH" -H "$TYPE" -X PUT -d '{
    "id": "review-manager",
    "name": "review-manager-api",
    "uris": ["/review-manager/*"],
    "upstream_id": "review-manager",
    "plugins": {
      "limit-req": {
        "rate": 300,
        "burst": 300,
        "rejected_code": 429,
        "key_type": "var_combination",
        "key": "$remote_addr $http_x_forwarded_for"
      },
      "limit-count": {
        "count": 10000,
        "time_window": 86400,
        "rejected_code": 429,
        "key_type": "var_combination",
        "key": "$remote_addr $http_x_forwarded_for"
      },
      "request-id": {
        "header_name": "X-Request-Id",
        "include_in_response": true,
        "algorithm": "uuid"
      }
    }
  }'

curl -i http://$APISIX_ADDR/apisix/admin/routes -H "$AUTH" -H "$TYPE" -X PUT -d '{
    "id": "issue-resources",
    "name": "issue-resources",
    "uris": ["/issue/*","/issue-manager/*"],
    "upstream_id": "issue-manager"
  }'