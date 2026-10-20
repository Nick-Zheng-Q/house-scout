#!/bin/sh
# Install this checkout's runtime Skill files. Run from any directory.
set -eu

usage() {
  echo "Usage: $0 [--project | --dest-dir DIR]" >&2
  echo "       $0 --update [--project | --dest-dir DIR]" >&2
  exit 2
}

mode=install
if [ "${1-}" = "--update" ]; then
  mode=update
  shift
fi

source_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)
dest_dir=${HOME:?}/.agents/skills
case "${1-}" in
  '') ;;
  --project)
    dest_dir=$source_dir/.agents/skills
    shift
    ;;
  --dest-dir)
    [ "$#" -ge 2 ] && [ -n "$2" ] || usage
    dest_dir=$2
    shift 2
    ;;
  *) usage ;;
esac
[ "$#" -eq 0 ] || usage

for file in SKILL.md SKILL.en.md LICENSE references/candidate-record.md references/candidate-record.en.md references/check-input.md references/check-input.en.md references/commute-input.md references/commute-input.en.md references/search-guide.md references/search-guide.en.md references/platforms.md references/platforms.en.md references/enrichment-guide.md references/enrichment-guide.en.md references/recommendation-guide.md references/recommendation-guide.en.md references/rental-guide.md references/rental-guide.en.md references/purchase-guide.md references/purchase-guide.en.md references/international-markets.md references/international-markets.en.md references/cost-comparison.md references/cost-comparison.en.md references/routing-guide.md references/routing-guide.en.md scripts/query_routes.py scripts/query_gtfs.py scripts/query_transit.py references/transit-guide.md references/transit-guide.en.md references/validation-status.md references/validation-status.en.md scripts/normalize_costs.py scripts/check_rentals.py scripts/check_commutes.py; do
  [ -f "$source_dir/$file" ] || { echo "Missing source file: $source_dir/$file" >&2; exit 1; }
done
grep -qx 'name: house-scout' "$source_dir/SKILL.md" || {
  echo "Source SKILL.md is not house-scout" >&2
  exit 1
}

mkdir -p "$dest_dir"
dest_dir=$(CDPATH= cd -- "$dest_dir" && pwd -P)
target=$dest_dir/house-scout
if [ -L "$target" ]; then
  echo "Refusing to replace symlink: $target" >&2
  exit 1
fi
if [ "$mode" = install ]; then
  if [ -e "$target" ]; then
    echo "Already installed: $target; run update.sh instead" >&2
    exit 1
  fi
else
  if [ ! -f "$target/SKILL.md" ] || ! grep -qx 'name: house-scout' "$target/SKILL.md"; then
    echo "No house-scout installation found at $target; run install.sh first" >&2
    exit 1
  fi
fi

stage=$(mktemp -d "$dest_dir/.house-scout-stage.XXXXXX")
cleanup() {
  if [ -n "$stage" ] && [ -d "$stage" ]; then rm -rf -- "$stage"; fi
}
trap cleanup EXIT HUP INT TERM
cp "$source_dir/SKILL.md" "$stage/SKILL.md"
cp "$source_dir/SKILL.en.md" "$stage/SKILL.en.md"
cp "$source_dir/LICENSE" "$stage/LICENSE"
cp -R "$source_dir/references" "$stage/references"
mkdir "$stage/scripts"
cp "$source_dir/scripts/check_rentals.py" "$stage/scripts/check_rentals.py"
cp "$source_dir/scripts/check_commutes.py" "$stage/scripts/check_commutes.py"
cp "$source_dir/scripts/normalize_costs.py" "$stage/scripts/normalize_costs.py"
cp "$source_dir/scripts/query_routes.py" "$stage/scripts/query_routes.py"
cp "$source_dir/scripts/query_gtfs.py" "$stage/scripts/query_gtfs.py"
cp "$source_dir/scripts/query_transit.py" "$stage/scripts/query_transit.py"

if [ "$mode" = install ]; then
  mv -- "$stage" "$target"
  stage=
  echo "Installed house-scout: $target"
else
  backup_dir=$(dirname -- "$dest_dir")/house-scout-backups
  mkdir -p "$backup_dir"
  backup=$backup_dir/house-scout-$(date +%Y%m%d-%H%M%S)-$$
  mv -- "$target" "$backup"
  if ! mv -- "$stage" "$target"; then
    mv -- "$backup" "$target"
    echo "Update failed; original installation restored" >&2
    exit 1
  fi
  stage=
  echo "Updated house-scout: $target"
  echo "Previous version backed up: $backup"
fi
