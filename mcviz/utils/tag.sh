#!/bin/bash

last_tag=$(git tag | tail -n1)
new_tag=$(date --rfc-3339=date | sed 's/-/./g')

echo "-----------------"
echo "New in ${new_tag}"
echo "-----------------"
echo
git shortlog --no-merges -n ${last_tag}..HEAD
