#!/bin/bash
#Generate release notes for a tag

#Fetch last tag or use $1
if [ -z "$1" ]; then
    last_tag=$(git tag | tail -n1)
else
    last_tag=$1
fi
#Note: to get the inital commit; use `git rev-list HEAD | tail -n 1`

#PEP 440 date based scheme
new_tag=$(date --rfc-3339=date | sed 's/-/./g')

#Output RST
echo "================="
echo "New in ${new_tag}"
echo "================="
echo
git shortlog --no-merges -n ${last_tag}..HEAD | sed 's/      / * /;s/^\(\([A-Za-z]\+ \)\+([0-9]\+)\):$/\1:\n\x00\1/' | sed '/^\x00.*$/ s/./-/g'

#Notes:
# Output ReStructured Text
# Shortlog from the last tag to currently checked-out commit
# Substitute shortlog indent for bullet marker
# Copy author line with prefixed null
# Swap all characters on null prefixed lines for dashes to give RST headings
