#!/usr/bin/env bash
echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") WARN HTTP 502 from /demo" >> logs/toy-web.log
