#!/usr/bin/env bash
#
# Exercise the Notes API with curl. Produces:
#   cookie.txt   — session jar (curl -b/-c)
#   errors.txt   — failed actions or invalid data
#   success.txt  — successful actions and responses
#
# Usage: ./bash_script.sh
#        BASE_URL=http://127.0.0.1:5000 ./bash_script.sh
#

set -u

BASE_URL="${BASE_URL:-http://localhost:5000}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COOKIE_JAR="${SCRIPT_DIR}/cookie.txt"
ERRORS_LOG="${SCRIPT_DIR}/errors.txt"
SUCCESS_LOG="${SCRIPT_DIR}/success.txt"
BODY="${TMPDIR:-/tmp}/notes_api_curl_body.$$"

cleanup() { rm -f "$BODY"; }
trap cleanup EXIT

: >"$ERRORS_LOG"
: >"$SUCCESS_LOG"
rm -f "$COOKIE_JAR"

log_error() {
  printf '%s %s\n' "$(date -Iseconds 2>/dev/null || date '+%Y-%m-%dT%H:%M:%S%z')" "$*" >>"$ERRORS_LOG"
}

log_success() {
  printf '%s %s\n' "$(date -Iseconds 2>/dev/null || date '+%Y-%m-%dT%H:%M:%S%z')" "$*" >>"$SUCCESS_LOG"
}

# curl_json METHOD URL JSON_BODY  — uses cookie jar when present
curl_json() {
  local method="$1"
  local url="$2"
  local data="${3:-}"
  local -a curl_args=(
    -sS
    -H "Content-Type: application/json"
    -o "$BODY"
    -w "%{http_code}"
  )
  if [[ -f "$COOKIE_JAR" ]]; then
    curl_args+=(-b "$COOKIE_JAR" -c "$COOKIE_JAR")
  fi
  if [[ "$method" == "GET" || "$method" == "DELETE" ]]; then
    curl_args+=(-X "$method" "$url")
  else
    curl_args+=(-X "$method" "$url" -d "$data")
  fi
  local code
  code="$(curl "${curl_args[@]}")"
  printf '%s' "$code"
}

# POST JSON without cookies (e.g. register another user without touching current session)
curl_json_no_cookie() {
  local method="$1"
  local url="$2"
  local data="${3:-}"
  curl -sS -H "Content-Type: application/json" -o "$BODY" -w "%{http_code}" -X "$method" "$url" -d "$data"
}

# GET without body (always with jar when present)
curl_get() {
  local url="$1"
  local -a curl_args=(-sS -o "$BODY" -w "%{http_code}")
  if [[ -f "$COOKIE_JAR" ]]; then
    curl_args+=(-b "$COOKIE_JAR" -c "$COOKIE_JAR")
  fi
  curl_args+=(-X GET "$url")
  curl "${curl_args[@]}"
}

describe() { printf '\n== %s ==\n' "$*"; }

# --- API root ---
describe "GET /"
code="$(curl -sS -o "$BODY" -w "%{http_code}" "${BASE_URL}/")"
if [[ "$code" =~ ^2 ]]; then
  log_success "GET / http=$code body=$(tr -d '\n' <"$BODY" | head -c 200)"
else
  log_error "GET / http=$code body=$(tr -d '\n' <"$BODY" | head -c 200)"
fi

# --- Auth: invalid register (password does not meet requirements) ---
describe "POST /api/auth/register (invalid)"
code="$(curl_json POST "${BASE_URL}/api/auth/register" '{"username":"ab","email":"bad","password":"short"}')"
body="$(cat "$BODY")"
if [[ "$code" =~ ^2 ]]; then
  log_success "register invalid unexpected 2xx http=$code $body"
else
  log_error "register invalid http=$code $body"
fi

# --- Auth: primary user register ---
USER1="apiuser_$$"
EMAIL1="${USER1}@test.local"
PASS1='Aa1!aaaaaaaa'

describe "POST /api/auth/register (valid $USER1)"
code="$(curl_json POST "${BASE_URL}/api/auth/register" "{\"username\":\"${USER1}\",\"email\":\"${EMAIL1}\",\"password\":\"${PASS1}\"}")"
body="$(cat "$BODY")"
if [[ "$code" == "201" ]]; then
  log_success "register $USER1 http=$code $body"
else
  log_error "register $USER1 http=$code $body"
fi

# --- Auth: duplicate ---
describe "POST /api/auth/register (duplicate)"
code="$(curl_json POST "${BASE_URL}/api/auth/register" "{\"username\":\"${USER1}\",\"email\":\"${EMAIL1}\",\"password\":\"${PASS1}\"}")"
body="$(cat "$BODY")"
if [[ "$code" =~ ^2 ]]; then
  log_success "register duplicate unexpected 2xx http=$code $body"
else
  log_error "register duplicate http=$code $body"
fi

# --- Auth: failed login ---
describe "POST /api/auth/login (wrong password)"
code="$(curl_json POST "${BASE_URL}/api/auth/login" "{\"email\":\"${EMAIL1}\",\"password\":\"WrongPass1!\"}")"
body="$(cat "$BODY")"
if [[ "$code" =~ ^2 ]]; then
  log_success "login bad pass unexpected 2xx http=$code $body"
else
  log_error "login bad password http=$code $body"
fi

# --- Auth: successful login (creates cookie.txt) ---
describe "POST /api/auth/login (OK)"
touch "$COOKIE_JAR"
code="$(curl_json POST "${BASE_URL}/api/auth/login" "{\"email\":\"${EMAIL1}\",\"password\":\"${PASS1}\"}")"
body="$(cat "$BODY")"
if [[ "$code" == "200" ]]; then
  log_success "login $EMAIL1 http=$code $body"
else
  log_error "login $EMAIL1 http=$code $body"
fi

# --- Notes: create without title ---
describe "POST /api/notes/create (no title)"
code="$(curl_json POST "${BASE_URL}/api/notes/create" '{"content":"content only"}')"
body="$(cat "$BODY")"
if [[ "$code" =~ ^2 ]]; then
  log_success "create note no title unexpected 2xx http=$code $body"
else
  log_error "create note no title http=$code $body"
fi

# --- Notes: create OK ---
describe "POST /api/notes/create (OK)"
code="$(curl_json POST "${BASE_URL}/api/notes/create" '{"title":"Curl note","content":"Test body","visibility":"private"}')"
body="$(cat "$BODY")"
if [[ "$code" == "201" ]]; then
  log_success "create note http=$code $body"
else
  log_error "create note http=$code $body"
fi

# --- Notes: list ---
describe "GET /api/notes/"
code="$(curl_get "${BASE_URL}/api/notes/")"
body="$(cat "$BODY")"
if [[ "$code" == "200" ]]; then
  log_success "list notes http=$code $(echo "$body" | tr -d '\n' | head -c 400)"
else
  log_error "list notes http=$code $body"
fi

NOTE_ID="$(python3 -c "
import json, sys
raw = sys.stdin.read() or '[]'
try:
    d = json.loads(raw)
except Exception:
    sys.exit(1)
if isinstance(d, list) and d:
    print(d[0].get('id', '') or '')
" <"$BODY" || true)"

if [[ -z "${NOTE_ID:-}" ]]; then
  log_error "could not get NOTE_ID from list response; skipping GET/PUT/DELETE/share by id"
else
  describe "GET /api/notes/${NOTE_ID}"
  code="$(curl_get "${BASE_URL}/api/notes/${NOTE_ID}")"
  body="$(cat "$BODY")"
  if [[ "$code" == "200" ]]; then
    log_success "get note $NOTE_ID http=$code $(echo "$body" | tr -d '\n' | head -c 300)"
  else
    log_error "get note $NOTE_ID http=$code $body"
  fi

  describe "GET /api/notes/999999 (missing)"
  code="$(curl_get "${BASE_URL}/api/notes/999999")"
  body="$(cat "$BODY")"
  if [[ "$code" =~ ^2 ]]; then
    log_success "get missing note unexpected 2xx http=$code $body"
  else
    log_error "get missing note http=$code $body"
  fi

  describe "PUT /api/notes/${NOTE_ID}"
  code="$(curl_json PUT "${BASE_URL}/api/notes/${NOTE_ID}" '{"title":"Updated note","content":"Updated via curl"}')"
  body="$(cat "$BODY")"
  if [[ "$code" == "200" ]]; then
    log_success "update note $NOTE_ID http=$code $(echo "$body" | tr -d '\n' | head -c 300)"
  else
    log_error "update note $NOTE_ID http=$code $body"
  fi

  # Second user for sharing
  USER2="apiuser2_$$"
  EMAIL2="${USER2}@test.local"
  describe "POST /api/auth/register (user 2 for share, no cookie)"
  code="$(curl_json_no_cookie POST "${BASE_URL}/api/auth/register" "{\"username\":\"${USER2}\",\"email\":\"${EMAIL2}\",\"password\":\"${PASS1}\"}")"
  body="$(cat "$BODY")"
  if [[ "$code" == "201" ]]; then
    log_success "register $USER2 http=$code $body"
  else
    log_error "register $USER2 http=$code $body"
  fi

  describe "POST /api/notes/share"
  code="$(curl_json POST "${BASE_URL}/api/notes/share" "{\"note_id\":${NOTE_ID},\"target_email\":\"${EMAIL2}\"}")"
  body="$(cat "$BODY")"
  if [[ "$code" == "200" ]]; then
    log_success "share note $NOTE_ID -> $EMAIL2 http=$code $body"
  else
    log_error "share note http=$code $body"
  fi

  describe "DELETE /api/notes/${NOTE_ID}"
  code="$(curl -sS -b "$COOKIE_JAR" -c "$COOKIE_JAR" -o "$BODY" -w "%{http_code}" -X DELETE "${BASE_URL}/api/notes/${NOTE_ID}")"
  body="$(cat "$BODY")"
  if [[ "$code" == "200" ]]; then
    log_success "delete note $NOTE_ID http=$code $body"
  else
    log_error "delete note $NOTE_ID http=$code $body"
  fi
fi

describe "GET /api/notes/ without cookie (must reject; API requires session)"
code="$(curl -sS -o "$BODY" -w "%{http_code}" -X GET "${BASE_URL}/api/notes/")"
body="$(cat "$BODY")"
if [[ "$code" =~ ^2 ]]; then
  log_success "list notes no cookie unexpected 2xx http=$code (should require cookie) $(echo "$body" | tr -d '\n' | head -c 200)"
else
  log_error "list notes no cookie http=$code expected rejection without session $(echo "$body" | tr -d '\n' | head -c 200)"
fi

printf '\nDone. See:\n  %s\n  %s\n  %s\n' "$COOKIE_JAR" "$SUCCESS_LOG" "$ERRORS_LOG"
