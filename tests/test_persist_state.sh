#!/usr/bin/env bash

set -u

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REPO_DIR=$(cd "$SCRIPT_DIR/.." && pwd)
PERSIST_SCRIPT="$REPO_DIR/scripts/persist_state.sh"
TEST_ROOT=$(mktemp -d "${TMPDIR:-/tmp}/persist-state.XXXXXX")
PASS_COUNT=0

cleanup() {
  case "$TEST_ROOT" in
    */persist-state.*) rm -rf -- "$TEST_ROOT" ;;
    *) echo "Geçici dizin güvenlik kontrolü başarısız: $TEST_ROOT" >&2 ;;
  esac
}
trap cleanup EXIT

fail() {
  echo "BAŞARISIZ: $*" >&2
  exit 1
}

pass() {
  PASS_COUNT=$((PASS_COUNT + 1))
  echo "GEÇTİ $PASS_COUNT/20: $1"
}

# Defter senaryoları için: base defteri remote'a koy (work + other görür).
seed_ledger() {
  cat >"$WORK_DIR/credits_ledger.json" <<'EOF'
{
  "entries": [
    {"month": "2026-08", "series": "seed", "part": 1, "reserved": 900, "actual": 100, "ts": "2026-08-01T00:00:00+00:00"}
  ]
}
EOF
  git -C "$WORK_DIR" add credits_ledger.json
  git -C "$WORK_DIR" commit -q -m "defter tabanı"
  git -C "$WORK_DIR" push -q origin main
}

# Uzak tarafı hazırla: other klonu defterine "aimagine" girdisini ekleyip push'lar.
push_other_ledger() {
  OTHER_DIR="$CASE_DIR/other"
  git clone -q "$REMOTE_DIR" "$OTHER_DIR"
  git -C "$OTHER_DIR" config user.name "Uzak Kullanıcı"
  git -C "$OTHER_DIR" config user.email "uzak@example.com"
  git -C "$OTHER_DIR" config core.autocrlf false
  cat >"$OTHER_DIR/credits_ledger.json" <<'EOF'
{
  "entries": [
    {"month": "2026-08", "series": "seed", "part": 1, "reserved": 900, "actual": 100, "ts": "2026-08-01T00:00:00+00:00"},
    {"month": "2026-08", "series": "aimagine", "part": 7, "reserved": 1900, "actual": 1214, "ts": "2026-08-09T01:00:00+00:00"}
  ]
}
EOF
  git -C "$OTHER_DIR" add credits_ledger.json
  git -C "$OTHER_DIR" commit -q -m "uzak defter girdisi"
  git -C "$OTHER_DIR" push -q origin main
}

# Yerel taraf: work klonu defterine "flashpoints" girdisini yazar (commit'siz).
write_local_ledger() {
  cat >"$WORK_DIR/credits_ledger.json" <<'EOF'
{
  "entries": [
    {"month": "2026-08", "series": "seed", "part": 1, "reserved": 900, "actual": 100, "ts": "2026-08-01T00:00:00+00:00"},
    {"month": "2026-08", "series": "flashpoints", "part": 6, "reserved": 900, "actual": 315, "ts": "2026-08-09T02:00:00+00:00"}
  ]
}
EOF
}

assert_merged_remote_ledger() {
  local name=$1
  local remote_ledger
  remote_ledger=$(git --git-dir="$REMOTE_DIR" show main:credits_ledger.json)
  printf '%s' "$remote_ledger" | grep -q '"series": "aimagine"' ||
    fail "$name uzak girdiyi kaybetti"
  printf '%s' "$remote_ledger" | grep -q '"series": "flashpoints"' ||
    fail "$name yerel girdiyi kaybetti"
  [ "$(printf '%s\n' "$remote_ledger" | grep -c '"series"')" -eq 3 ] ||
    fail "$name girdi sayısı 3 değil"
}

new_sandbox() {
  local name=$1
  CASE_DIR="$TEST_ROOT/$name"
  REMOTE_DIR="$CASE_DIR/remote.git"
  SEED_DIR="$CASE_DIR/seed"
  WORK_DIR="$CASE_DIR/work"

  mkdir -p "$CASE_DIR"
  git init --bare -q "$REMOTE_DIR" || fail "$name bare remote oluşturulamadı"
  git init -q -b main "$SEED_DIR" || fail "$name seed repo oluşturulamadı"
  git -C "$SEED_DIR" config user.name "Test Kullanıcısı"
  git -C "$SEED_DIR" config user.email "test@example.com"
  git -C "$SEED_DIR" config core.autocrlf false
  printf 'temel\n' >"$SEED_DIR/state.txt"
  git -C "$SEED_DIR" add state.txt
  git -C "$SEED_DIR" commit -q -m "temel"
  git -C "$SEED_DIR" remote add origin "$REMOTE_DIR"
  git -C "$SEED_DIR" push -q -u origin main
  git --git-dir="$REMOTE_DIR" symbolic-ref HEAD refs/heads/main
  git -c core.autocrlf=false clone -q "$REMOTE_DIR" "$WORK_DIR"
  git -C "$WORK_DIR" config user.name "Test Kullanıcısı"
  git -C "$WORK_DIR" config user.email "test@example.com"
  git -C "$WORK_DIR" config core.autocrlf false
}

remote_commit_count() {
  git --git-dir="$REMOTE_DIR" rev-list --count refs/heads/main
}

run_persist() {
  (
    cd "$WORK_DIR" || exit 1
    PERSIST_RETRY_DELAY_SECONDS=0 "$PERSIST_SCRIPT" "test persist" "$@"
  )
}

expect_killer() {
  local name=$1
  local before=$2
  shift 2
  local log="$CASE_DIR/persist.log"

  if run_persist "$@" >"$log" 2>&1; then
    sed 's/^/  /' "$log" >&2
    fail "$name exit 0 döndürdü"
  fi
  if [ "$(remote_commit_count)" -ne "$before" ]; then
    sed 's/^/  /' "$log" >&2
    fail "$name commit sayısını değiştirdi"
  fi
}

new_sandbox "01-untracked-marker"
before=$(remote_commit_count)
printf '<<<<<<< sol\nveri\n=======\nveri\n>>>>>>> sağ\n' >"$WORK_DIR/untracked.txt"
expect_killer "untracked marker" "$before" untracked.txt
git -C "$WORK_DIR" diff --cached --quiet || fail "untracked marker dosyayı stage etti"
pass "untracked marker exit 1, stage yok, commit sayısı sabit"

new_sandbox "02-tracked-marker"
before=$(remote_commit_count)
printf '<<<<<<< sol\nveri\n=======\nveri\n>>>>>>> sağ\n' >"$WORK_DIR/state.txt"
expect_killer "tracked marker" "$before" state.txt
git -C "$WORK_DIR" diff --cached --quiet || fail "tracked marker dosyayı stage etti"
pass "tracked değişen marker exit 1, stage yok, commit sayısı sabit"

new_sandbox "03-left-only"
before=$(remote_commit_count)
printf '<<<<<<< sol\nveri\n' >"$WORK_DIR/state.txt"
expect_killer "sol tek marker" "$before" state.txt
pass "sol tek marker exit 1, commit sayısı sabit"

new_sandbox "04-right-only"
before=$(remote_commit_count)
printf 'veri\n>>>>>>> sağ\n' >"$WORK_DIR/state.txt"
expect_killer "sağ tek marker" "$before" state.txt
pass "sağ tek marker exit 1, commit sayısı sabit"

new_sandbox "05-separator-only"
printf 'temel\n=======\ngeçerli veri\n' >"$WORK_DIR/state.txt"
run_persist state.txt >"$CASE_DIR/persist.log" 2>&1 || {
  sed 's/^/  /' "$CASE_DIR/persist.log" >&2
  fail "tek ayraç geçerli kabul edilmedi"
}
git --git-dir="$REMOTE_DIR" show main:state.txt | grep -q '^=======$' ||
  fail "tek ayraç remote'a push edilmedi"
pass "tek başına ayraç geçerli, commit ve push başarılı"

new_sandbox "06-separator-left"
before=$(remote_commit_count)
printf '<<<<<<< sol\nveri\n=======\n' >"$WORK_DIR/state.txt"
expect_killer "ayraç ve sol marker" "$before" state.txt
pass "ayraç ve sol marker exit 1, commit sayısı sabit"

new_sandbox "07-dirty-index"
before=$(remote_commit_count)
printf 'staged veri\n' >"$WORK_DIR/state.txt"
git -C "$WORK_DIR" add state.txt
expect_killer "kirli index" "$before" state.txt
pass "kirli index exit 1, commit sayısı sabit"

new_sandbox "08-unmerged-index"
before=$(remote_commit_count)
base_blob=$(printf 'temel\n' | git -C "$WORK_DIR" hash-object -w --stdin)
ours_blob=$(printf 'bizim\n' | git -C "$WORK_DIR" hash-object -w --stdin)
theirs_blob=$(printf 'onların\n' | git -C "$WORK_DIR" hash-object -w --stdin)
{
  printf '100644 %s 1\tstate.txt\n' "$base_blob"
  printf '100644 %s 2\tstate.txt\n' "$ours_blob"
  printf '100644 %s 3\tstate.txt\n' "$theirs_blob"
} | git -C "$WORK_DIR" update-index --index-info
expect_killer "ls-files -u dolu" "$before" state.txt
pass "ls-files -u dolu exit 1, commit sayısı sabit"

new_sandbox "09-rebase-state"
before=$(remote_commit_count)
git_dir=$(git -C "$WORK_DIR" rev-parse --git-dir)
mkdir -p "$WORK_DIR/$git_dir/rebase-merge"
expect_killer "yarım rebase" "$before" state.txt
pass "yarım rebase dizini exit 1, commit sayısı sabit"

new_sandbox "10-autostash-conflict"
printf 'yerel değişiklik\n' >"$WORK_DIR/state.txt"
OTHER_DIR="$CASE_DIR/other"
git clone -q "$REMOTE_DIR" "$OTHER_DIR"
git -C "$OTHER_DIR" config user.name "Uzak Kullanıcı"
git -C "$OTHER_DIR" config user.email "uzak@example.com"
git -C "$OTHER_DIR" config core.autocrlf false
printf 'uzak değişiklik\n' >"$OTHER_DIR/state.txt"
git -C "$OTHER_DIR" add state.txt
git -C "$OTHER_DIR" commit -q -m "uzak değişiklik"
git -C "$OTHER_DIR" push -q origin main
before=$(remote_commit_count)
expect_killer "autostash conflict" "$before" state.txt
git_dir=$(git -C "$WORK_DIR" rev-parse --git-dir)
[ ! -e "$WORK_DIR/$git_dir/rebase-merge" ] || fail "autostash conflict rebase-merge bıraktı"
[ ! -e "$WORK_DIR/$git_dir/rebase-apply" ] || fail "autostash conflict rebase-apply bıraktı"
pass "autostash conflict exit 1, abort edildi, commit sayısı sabit"

new_sandbox "11-add-failure"
before=$(remote_commit_count)
printf 'zararsız değişiklik\n' >"$WORK_DIR/state.txt"
REAL_GIT=$(command -v git)
FAKE_BIN="$CASE_DIR/bin"
mkdir -p "$FAKE_BIN"
cat >"$FAKE_BIN/git" <<EOF
#!/usr/bin/env bash
if [ "\${1:-}" = "add" ]; then
  echo "sahte git add hatası" >&2
  exit 42
fi
exec "$REAL_GIT" "\$@"
EOF
chmod +x "$FAKE_BIN/git"
if (
  cd "$WORK_DIR" || exit 1
  PATH="$FAKE_BIN:$PATH" PERSIST_RETRY_DELAY_SECONDS=0 \
    "$PERSIST_SCRIPT" "test persist" state.txt
) >"$CASE_DIR/persist.log" 2>&1; then
  fail "git add hatası exit 0 döndürdü"
fi
[ "$(remote_commit_count)" -eq "$before" ] || fail "git add hatası commit sayısını değiştirdi"
pass "git add hatası exit 1, commit sayısı sabit"

new_sandbox "12-deleted-file"
before_remote=$(remote_commit_count)
rm -- "$WORK_DIR/state.txt"
run_persist state.txt >"$CASE_DIR/persist.log" 2>&1 ||
  fail "silinen tracked dosya persist edilemedi"
if git --git-dir="$REMOTE_DIR" cat-file -e main:state.txt 2>/dev/null; then
  fail "silinen tracked dosya remote'da kaldı"
fi
[ "$(remote_commit_count)" -eq $((before_remote + 1)) ] ||
  fail "silinen tracked dosya remote commit sayısını artırmadı"
pass "silinen tracked dosya add -A ile stage edildi ve push edildi"

new_sandbox "13-clean-change"
before_remote=$(remote_commit_count)
printf 'zararsız yeni durum\n' >"$WORK_DIR/state.txt"
run_persist state.txt >"$CASE_DIR/persist.log" 2>&1 ||
  fail "temiz değişiklik persist edilemedi"
[ "$(remote_commit_count)" -eq $((before_remote + 1)) ] ||
  fail "temiz değişiklik remote commit sayısını artırmadı"
pass "markersız temiz değişiklik commit ve push edildi"

new_sandbox "14-rev-list-guard"
printf 'önceden commit edilmiş durum\n' >"$WORK_DIR/state.txt"
git -C "$WORK_DIR" add state.txt
git -C "$WORK_DIR" commit -q -m "yerel öndeki commit"
local_head=$(git -C "$WORK_DIR" rev-parse HEAD)
run_persist state.txt >"$CASE_DIR/persist.log" 2>&1 ||
  fail "rev-list guard yerel commit'i push edemedi"
remote_head=$(git --git-dir="$REMOTE_DIR" rev-parse refs/heads/main)
[ "$remote_head" = "$local_head" ] ||
  fail "rev-list guard remote'u yerel HEAD'e taşımadı"
pass "değişiklik yokken rev-list guard öndeki yerel commit'i push etti"

new_sandbox "15-trailing-whitespace"
before_remote=$(remote_commit_count)
printf '{"a":2}   \n' >"$WORK_DIR/state.txt"
run_persist state.txt >"$CASE_DIR/persist.log" 2>&1 ||
  fail "trailing whitespace içeren meşru değişiklik persist edilemedi"
grep -q 'trailing whitespace' "$CASE_DIR/persist.log" ||
  fail "trailing whitespace uyarısı loglanmadı"
[ "$(remote_commit_count)" -eq $((before_remote + 1)) ] ||
  fail "trailing whitespace değişikliği remote commit sayısını artırmadı"
remote_state=$(git --git-dir="$REMOTE_DIR" show main:state.txt)
case "$remote_state" in
  *"   ") ;;
  *) fail "trailing whitespace içeren içerik remote'da korunmadı" ;;
esac
pass "trailing whitespace uyarısı loglandı, commit ve push devam etti"

new_sandbox "16-nested-crlf-marker"
before=$(remote_commit_count)
mkdir -p "$WORK_DIR/nested/alt"
printf 'x\r\n<<<<<<< HEAD\r\n' >"$WORK_DIR/nested/alt/marker.txt"
expect_killer "alt dizindeki CRLF marker" "$before" nested/
git -C "$WORK_DIR" diff --cached --quiet ||
  fail "alt dizindeki CRLF marker dosyayı stage etti"
pass "üst dizin pathspec altındaki CRLF untracked marker exit 1, stage yok, commit sayısı sabit"

new_sandbox "17-ledger-autostash-merge"
seed_ledger
push_other_ledger
write_local_ledger
run_persist credits_ledger.json >"$CASE_DIR/persist.log" 2>&1 || {
  sed 's/^/  /' "$CASE_DIR/persist.log" >&2
  fail "defter autostash çakışması otomatik birleşmedi"
}
grep -q "Autostash çakışması defter birleşimiyle çözüldü" "$CASE_DIR/persist.log" ||
  fail "defter autostash birleşim mesajı loglanmadı"
assert_merged_remote_ledger "defter autostash birleşimi"
[ -z "$(git -C "$WORK_DIR" stash list)" ] ||
  fail "defter autostash birleşimi stash girdisi bıraktı"
[ -z "$(git -C "$WORK_DIR" ls-files -u)" ] ||
  fail "defter autostash birleşimi çözülmemiş index bıraktı"
pass "defter autostash çakışması birleşti, iki taraf da push'ta korundu"

new_sandbox "18-ledger-rebase-merge"
seed_ledger
push_other_ledger
write_local_ledger
git -C "$WORK_DIR" add credits_ledger.json
git -C "$WORK_DIR" commit -q -m "yerel defter girdisi"
run_persist credits_ledger.json >"$CASE_DIR/persist.log" 2>&1 || {
  sed 's/^/  /' "$CASE_DIR/persist.log" >&2
  fail "defter rebase çakışması otomatik birleşmedi"
}
grep -q "Rebase çakışması defter birleşimiyle çözüldü" "$CASE_DIR/persist.log" ||
  fail "defter rebase birleşim mesajı loglanmadı"
assert_merged_remote_ledger "defter rebase birleşimi"
git_dir=$(git -C "$WORK_DIR" rev-parse --git-dir)
[ ! -e "$WORK_DIR/$git_dir/rebase-merge" ] || fail "defter rebase birleşimi rebase-merge bıraktı"
pass "commit'li defter rebase çakışması birleşti ve push edildi"

new_sandbox "19-ledger-mixed-conflict"
seed_ledger
push_other_ledger
printf 'uzak state\n' >"$OTHER_DIR/state.txt"
git -C "$OTHER_DIR" add state.txt
git -C "$OTHER_DIR" commit -q -m "uzak state değişikliği"
git -C "$OTHER_DIR" push -q origin main
write_local_ledger
printf 'yerel state\n' >"$WORK_DIR/state.txt"
before=$(remote_commit_count)
expect_killer "karışık çakışma" "$before" credits_ledger.json state.txt
git_dir=$(git -C "$WORK_DIR" rev-parse --git-dir)
[ ! -e "$WORK_DIR/$git_dir/rebase-merge" ] || fail "karışık çakışma rebase-merge bıraktı"
pass "defter + defter-dışı karışık çakışma fail-closed kaldı"

new_sandbox "20-ledger-bad-schema"
printf '[{"ts": "2026-08-01T00:00:00+00:00"}]\n' >"$WORK_DIR/credits_ledger.json"
git -C "$WORK_DIR" add credits_ledger.json
git -C "$WORK_DIR" commit -q -m "bozuk şemalı defter tabanı"
git -C "$WORK_DIR" push -q origin main
OTHER_DIR="$CASE_DIR/other"
git clone -q "$REMOTE_DIR" "$OTHER_DIR"
git -C "$OTHER_DIR" config user.name "Uzak Kullanıcı"
git -C "$OTHER_DIR" config user.email "uzak@example.com"
git -C "$OTHER_DIR" config core.autocrlf false
printf '[{"ts": "2026-08-01T00:00:00+00:00"}, {"ts": "uzak"}]\n' >"$OTHER_DIR/credits_ledger.json"
git -C "$OTHER_DIR" add credits_ledger.json
git -C "$OTHER_DIR" commit -q -m "uzak bozuk şema"
git -C "$OTHER_DIR" push -q origin main
printf '[{"ts": "2026-08-01T00:00:00+00:00"}, {"ts": "yerel"}]\n' >"$WORK_DIR/credits_ledger.json"
before=$(remote_commit_count)
expect_killer "bozuk şemalı defter" "$before" credits_ledger.json
pass "bozuk şemalı defter çakışması fail-closed kaldı"

echo "SONUÇ: 20/20 senaryo geçti"
