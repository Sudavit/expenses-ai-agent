#!/bin/sh -eu

die() { echo "$@"; exit 1; }
gnu_sed() { sed --version &> /dev/null; }

project_name=${1:?"usage: $0 <project-name>"}
files=$(git grep -l AAI | grep -v $(basename $0))

if sed --version >/dev/null 2>&1; then
    sed -i "s/AAI/$project_name/g" $files         # GNU
else
    sed -i "" "s/AAI/$project_name/g" $files      # BSD/MacOS
fi
git mv src/AAI src/$project_name
echo 'Now write a good README.md!!!'
