#!/bin/bash

# This script merges all branches into main branch
# Branches are merged in order of most recent commit date first

set -e

# Fetch latest branches and commits
git fetch --all

# Checkout main branch
git checkout main

# Get list of branches except main, with last commit date, sorted by date descending
branches=$(git for-each-ref --sort=-committerdate --format='%(refname:short)' refs/heads/ | grep -v '^main$')

echo "Branches to merge into main in order of most recent commit date:"
echo "$branches"

# Merge each branch into main
for branch in $branches; do
    echo "Merging branch: $branch"
    git merge --no-ff "$branch" -m "Merge branch '$branch' into main"
done

echo "All branches merged into main."
