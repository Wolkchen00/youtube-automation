#!/usr/bin/env bash

set -u

if [ "$#" -lt 2 ]; then
  echo "Kullanım: $0 \"<commit mesajı>\" <path...>" >&2
  exit 1
fi

commit_message=$1
shift
paths=("$@")
retry_delay=${PERSIST_RETRY_DELAY_SECONDS:-10}

fail() {
  echo "Persist hatası: $*" >&2
  exit 1
}

check_preconditions() {
  local state_path
  local ref
  local diff_status

  for state_path in rebase-merge rebase-apply; do
    state_path=$(git rev-parse --git-path "$state_path") ||
      fail "Git durum yolu okunamadı: $state_path"
    if [ -e "$state_path" ]; then
      fail "Yarım kalmış Git işlemi bulundu: $state_path"
    fi
  done

  for ref in MERGE_HEAD CHERRY_PICK_HEAD; do
    if git rev-parse -q --verify "$ref" >/dev/null 2>&1; then
      fail "Yarım kalmış Git işlemi bulundu: $ref"
    fi
  done

  if [ -n "$(git ls-files -u)" ]; then
    fail "Çözülmemiş index girdileri bulundu"
  fi

  git diff --cached --quiet
  diff_status=$?
  if [ "$diff_status" -eq 1 ]; then
    fail "Beklenmeyen staged değişiklik bulundu"
  elif [ "$diff_status" -ne 0 ]; then
    fail "Index durumu denetlenemedi"
  fi
}

append_scan_file() {
  local candidate=$1
  local existing

  for existing in "${scan_files[@]}"; do
    if [ "$existing" = "$candidate" ]; then
      return
    fi
  done
  scan_files+=("$candidate")
}

scan_for_conflicts() {
  local file
  local has_left
  local has_right
  local has_separator
  local marker_found=false
  local diff_check_output
  local diff_check_status
  local marker_check_output
  local marker_warning
  local marker_location
  local marker_file
  local marker_line_number
  local marker_line
  local diff_marker_found=false
  scan_files=()

  while IFS= read -r -d '' file; do
    append_scan_file "$file"
  done < <(git diff --name-only -z --)

  while IFS= read -r -d '' file; do
    append_scan_file "$file"
  done < <(git ls-files -o --exclude-standard -z -- "${paths[@]}")

  for file in "${scan_files[@]}"; do
    if [ ! -e "$file" ]; then
      continue
    fi

    has_left=false
    has_right=false
    has_separator=false
    grep -q -- '^<<<<<<< ' "$file" && has_left=true
    grep -q -- '^>>>>>>> ' "$file" && has_right=true
    grep -q -- '^=======$' "$file" && has_separator=true

    if [ "$has_left" = true ] || [ "$has_right" = true ]; then
      echo "Çakışma markerı bulundu: $file" >&2
      marker_found=true
    elif [ "$has_separator" = true ]; then
      echo "Tek başına ayraç geçerli kabul edildi: $file"
    fi
  done

  if [ "$marker_found" = true ]; then
    fail "Marker taraması başarısız"
  fi

  diff_check_output=$(git diff --check 2>&1)
  diff_check_status=$?
  if [ "$diff_check_status" -ne 0 ]; then
    printf 'git diff --check uyarıları:\n%s\n' "$diff_check_output" >&2
    marker_check_output=$(
      printf '%s\n' "$diff_check_output" |
        grep -E ': leftover conflict marker$' || true
    )
    if [ -n "$marker_check_output" ]; then
      while IFS= read -r marker_warning; do
        marker_location=${marker_warning%: leftover conflict marker}
        marker_line_number=${marker_location##*:}
        marker_file=${marker_location%:*}
        marker_line=$(sed -n "${marker_line_number}p" -- "$marker_file")
        marker_line=${marker_line%$'\r'}

        if [[ "$marker_line" == "<<<<<<< "* ]] ||
          [[ "$marker_line" == ">>>>>>> "* ]]; then
          diff_marker_found=true
        elif [ "$marker_line" = "=======" ]; then
          if grep -q -- '^<<<<<<< ' "$marker_file" ||
            grep -q -- '^>>>>>>> ' "$marker_file"; then
            diff_marker_found=true
          fi
        fi
      done <<<"$marker_check_output"
    fi
    if [ "$diff_marker_found" = true ]; then
      fail "git diff --check çakışma markerı buldu"
    fi
    echo "Yalnız kozmetik diff uyarıları bulundu, persist devam ediyor" >&2
  fi
}

path_is_known() {
  local path=$1
  local output

  if [ -e "$path" ] || [ -L "$path" ]; then
    return 0
  fi

  output=$(git ls-files -- "$path") || return 2
  if [ -n "$output" ]; then
    return 0
  fi

  output=$(git ls-files -o --exclude-standard -- "$path") || return 2
  if [ -n "$output" ]; then
    return 0
  fi

  return 1
}

stage_paths() {
  local path
  local known_status

  for path in "${paths[@]}"; do
    path_is_known "$path"
    known_status=$?
    if [ "$known_status" -eq 1 ]; then
      echo "Path atlandı, tracked değil ve mevcut değil: $path"
      continue
    elif [ "$known_status" -ne 0 ]; then
      fail "Path denetlenemedi: $path"
    fi

    if ! git add -A -- "$path"; then
      fail "git add başarısız: $path"
    fi
  done
}

git config user.name "github-actions[bot]" ||
  fail "Git kullanıcı adı ayarlanamadı"
git config user.email "github-actions[bot]@users.noreply.github.com" ||
  fail "Git kullanıcı e-postası ayarlanamadı"

for attempt in 1 2 3; do
  echo "Persist denemesi: $attempt/3"
  check_preconditions

  if ! git pull --rebase --autostash origin main; then
    git rebase --abort >/dev/null 2>&1 || true
    fail "git pull --rebase --autostash başarısız"
  fi

  if [ -n "$(git ls-files -u)" ]; then
    git rebase --abort >/dev/null 2>&1 || true
    fail "Autostash sonrasında çözülmemiş index girdileri bulundu"
  fi

  scan_for_conflicts
  stage_paths

  if git diff --cached --quiet; then
    ahead_count=$(git rev-list --count origin/main..HEAD) ||
      fail "rev-list guard çalıştırılamadı"
    if [ "$ahead_count" -eq 0 ]; then
      echo "Persist edilecek değişiklik yok"
      exit 0
    fi
    echo "Yerel commit remote'un önünde, push yapılacak"
  else
    if ! git commit -m "$commit_message"; then
      fail "Commit oluşturulamadı"
    fi
  fi

  if git push origin main; then
    echo "Persist push başarılı"
    exit 0
  fi

  echo "Push denemesi başarısız: $attempt/3" >&2
  if [ "$attempt" -lt 3 ] && [ "$retry_delay" != "0" ]; then
    sleep "$retry_delay"
  fi
done

fail "Üç push denemesi de başarısız"
