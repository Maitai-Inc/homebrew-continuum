#!/usr/bin/env bash
# Stage an already tested formula without writing to the protected default branch.
set -euo pipefail
: "${VERSION:?}" "${GITHUB_REPOSITORY:?}" "${GITHUB_STEP_SUMMARY:?}"
formula_hash=$(git hash-object Formula/continuum.rb)
branch="codex/continuum-${VERSION}-${formula_hash:0:12}"
git check-ref-format --branch "$branch" >/dev/null
if git ls-remote --exit-code --heads origin "refs/heads/${branch}" >/dev/null; then
  echo "Candidate ${branch} already exists."
else
  status=$?
  if [ "$status" -ne 2 ]; then
    echo "Could not inspect candidate branch; refusing to publish." >&2
    exit "$status"
  fi
  git switch -c "$branch"
  git add Formula/continuum.rb
  git -c user.name="github-actions[bot]" \
    -c user.email="41898282+github-actions[bot]@users.noreply.github.com" \
    commit -q -m "continuum ${VERSION}"
  git push origin "HEAD:refs/heads/${branch}"
fi
# This repository intentionally does not let GITHUB_TOKEN create/approve PRs.
# Give a reviewer a ready-to-submit comparison without expanding bot permissions.
printf '### Continuum %s ready for review\n\nThe candidate passed the macOS and Linux formula checks. [Open its pull request](https://github.com/%s/compare/main...%s?expand=1). Merge after review to publish.\n' \
  "$VERSION" "$GITHUB_REPOSITORY" "$branch" >> "$GITHUB_STEP_SUMMARY"
