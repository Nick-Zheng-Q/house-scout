#!/bin/sh
# Update an existing installation from this checkout.
set -eu
source_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)
exec sh "$source_dir/install.sh" --update "$@"
