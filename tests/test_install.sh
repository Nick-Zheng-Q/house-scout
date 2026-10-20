#!/bin/sh
set -eu

repo=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd -P)
tmp=$(mktemp -d "${TMPDIR:-/tmp}/house-scout-install-test.XXXXXX")
trap 'rm -rf -- "$tmp"' EXIT HUP INT TERM

mkdir -p "$tmp/source/scripts" "$tmp/source/references"
cp "$repo/install.sh" "$repo/update.sh" "$repo/SKILL.md" "$repo/SKILL.en.md" "$repo/LICENSE" "$tmp/source/"
cp "$repo"/references/*.md "$tmp/source/references/"
cp "$repo/scripts/check_rentals.py" "$tmp/source/scripts/"
cp "$repo/scripts/check_commutes.py" "$tmp/source/scripts/"
cp "$repo/scripts/normalize_costs.py" "$tmp/source/scripts/"
cp "$repo/scripts/query_routes.py" "$tmp/source/scripts/"
cp "$repo/scripts/query_gtfs.py" "$tmp/source/scripts/"
cp "$repo/scripts/query_transit.py" "$tmp/source/scripts/"
mkdir "$tmp/dest"

"$tmp/source/install.sh" --dest-dir "$tmp/dest" > "$tmp/install.out"
[ -f "$tmp/dest/house-scout/SKILL.md" ]
[ -f "$tmp/dest/house-scout/SKILL.en.md" ]
[ -f "$tmp/dest/house-scout/LICENSE" ]
grep -q 'PolyForm Shield License 1.0.0' "$tmp/dest/house-scout/LICENSE"
[ -f "$tmp/dest/house-scout/references/search-guide.md" ]
[ -f "$tmp/dest/house-scout/references/search-guide.en.md" ]
[ -f "$tmp/dest/house-scout/references/platforms.md" ]
[ -f "$tmp/dest/house-scout/references/platforms.en.md" ]
for name in candidate-record check-input commute-input enrichment-guide platforms purchase-guide recommendation-guide rental-guide search-guide international-markets cost-comparison routing-guide transit-guide validation-status; do
  [ -f "$tmp/dest/house-scout/references/$name.md" ]
  [ -f "$tmp/dest/house-scout/references/$name.en.md" ]
done
[ -f "$tmp/dest/house-scout/references/enrichment-guide.md" ]
[ -f "$tmp/dest/house-scout/references/commute-input.md" ]
[ -f "$tmp/dest/house-scout/references/recommendation-guide.md" ]
[ -f "$tmp/dest/house-scout/references/rental-guide.md" ]
[ -f "$tmp/dest/house-scout/references/purchase-guide.md" ]
[ -f "$tmp/dest/house-scout/scripts/check_rentals.py" ]
[ -f "$tmp/dest/house-scout/scripts/check_commutes.py" ]
[ -f "$tmp/dest/house-scout/scripts/normalize_costs.py" ]
[ -f "$tmp/dest/house-scout/scripts/query_routes.py" ]
[ -f "$tmp/dest/house-scout/scripts/query_gtfs.py" ]
python3 "$tmp/dest/house-scout/scripts/query_routes.py" --help > /dev/null
python3 "$tmp/dest/house-scout/scripts/query_gtfs.py" --help > /dev/null
python3 "$tmp/dest/house-scout/scripts/query_transit.py" --help > /dev/null
printf '{"currency":"GBP","costs":[{"name":"rent","amount":300,"period":"week"}]}\n' > "$tmp/normalizer-input.json"
python3 "$tmp/dest/house-scout/scripts/normalize_costs.py" "$tmp/normalizer-input.json" > "$tmp/normalizer-output.json"
python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); assert d["known_monthly_subtotal"]==1300; assert d["necessary_cost_scope"]=="not_verified"' "$tmp/normalizer-output.json"
[ ! -f "$tmp/dest/house-scout/scripts/install.sh" ]
if "$tmp/source/install.sh" --dest-dir "$tmp/dest" > /dev/null 2>&1; then
  echo "Install should refuse to overwrite" >&2
  exit 1
fi

printf '\nTEST_UPDATE_MARKER\n' >> "$tmp/source/references/search-guide.md"
"$tmp/source/update.sh" --dest-dir "$tmp/dest" > "$tmp/update.out"
grep -q TEST_UPDATE_MARKER "$tmp/dest/house-scout/references/search-guide.md"
backup=$(find "$tmp/house-scout-backups" -mindepth 1 -maxdepth 1 -type d | head -1)
[ -n "$backup" ]
if grep -q TEST_UPDATE_MARKER "$backup/references/search-guide.md"; then
  echo "Backup should contain the previous version" >&2
  exit 1
fi

mkdir -p "$tmp/other/house-scout"
printf 'not a skill\n' > "$tmp/other/house-scout/SKILL.md"
if "$tmp/source/update.sh" --dest-dir "$tmp/other" > /dev/null 2>&1; then
  echo "Update should refuse an unrelated directory" >&2
  exit 1
fi

"$tmp/source/install.sh" --project > /dev/null
[ -f "$tmp/source/.agents/skills/house-scout/SKILL.md" ]
"$tmp/source/update.sh" --project > /dev/null

mkdir -p "$tmp/symlinks"
ln -s "$tmp/dest/house-scout" "$tmp/symlinks/house-scout"
if "$tmp/source/update.sh" --dest-dir "$tmp/symlinks" > /dev/null 2>&1; then
  echo "Update should refuse a symlinked installation" >&2
  exit 1
fi

# Fail only the staged-directory rename, then require the old installation back.
mkdir "$tmp/failing-bin"
cat > "$tmp/failing-bin/mv" <<'SH'
#!/bin/sh
case "${2-}" in
  */.house-scout-stage.*) exit 1 ;;
esac
exec /bin/mv "$@"
SH
chmod +x "$tmp/failing-bin/mv"
printf '\nROLLBACK_ATTEMPT_MARKER\n' >> "$tmp/source/references/search-guide.md"
if PATH="$tmp/failing-bin:$PATH" "$tmp/source/update.sh" --dest-dir "$tmp/dest" > "$tmp/rollback.out" 2>&1; then
  echo "Injected staged rename failure should fail update" >&2
  exit 1
fi
grep -q 'original installation restored' "$tmp/rollback.out"
grep -q TEST_UPDATE_MARKER "$tmp/dest/house-scout/references/search-guide.md"
if grep -q ROLLBACK_ATTEMPT_MARKER "$tmp/dest/house-scout/references/search-guide.md"; then
  echo "Failed update must not replace the previous installation" >&2
  exit 1
fi
[ -z "$(find "$tmp/dest" -maxdepth 1 -name '.house-scout-stage.*' -print)" ]

# Some ZIP extractors omit Unix executable bits; documented sh entrypoints still work.
chmod 644 "$tmp/source/install.sh" "$tmp/source/update.sh"
sh "$tmp/source/update.sh" --dest-dir "$tmp/dest" > "$tmp/no-mode-update.out"
grep -q ROLLBACK_ATTEMPT_MARKER "$tmp/dest/house-scout/references/search-guide.md"

echo "Installer tests passed"

