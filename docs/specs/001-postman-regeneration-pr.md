# S-001: Postman collection regenerates as a pull request

status: approved
serves: G-2

## Problem

The Postman collection is generated from the live `openapi.json` by
`tools/generate_postman.py`, but only when someone remembers to run it. After as-rest
deploys a contract change, the committed collection stays behind until a docs pull request
regenerates it, and once #18's check runs on every pull request, an unrelated pull request
fails on that drift. G-2 asks that the collection always come from the current contract.
This is W-2 of the accepted plan #9, built on W-1 (#18); it comes from #19.

## Behaviour

A workflow, `.github/workflows/postman-regenerate.yml`, runs once a day at 06:00 UTC and on
demand (`workflow_dispatch`), on a GitHub-hosted runner (the repository is public). It runs
`tools/generate_postman.py` against the live contract and compares the result with
`postman/appstorespy.postman_collection.json` on `main`:

- Equal: the run succeeds and changes nothing. When a regeneration pull request is still
  open (main caught up through another pull request), it closes that pull request with a
  comment saying `main` already matches the contract, and deletes its branch
- Different: it commits the regenerated collection, and only that file, to the branch
  `postman/regenerate`, based on the current `main`, and opens a pull request to `main`
  titled `Regenerate the Postman collection from openapi.json <info.version>`. When that
  pull request is already open, it force-updates the branch and retitles the pull request
  instead of opening a second one. The pull request body names the contract version and
  the URL it was read from, and says the collection was generated, not edited by hand
- Before it pushes, the run runs `tools/generate_postman.py --check` (from #18) on the
  regenerated tree, and fails without pushing when the check fails
- A failed fetch of the contract, or a contract that isn't JSON, fails the run with its
  error and leaves branches and pull requests as they were

The workflow writes with the run's `GITHUB_TOKEN` (`contents: write`, `pull-requests:
write`), with a concurrency group so two runs never race on the branch. A pull request
opened with that token starts no `pull_request` workflows, so #18's check does not run on
it by itself; the run's own `--check` step stands in for it. The repository setting "Allow
GitHub Actions to create and approve pull requests" must be on, a step for the maintainer.

The `README.md` section on the Postman collection says the collection regenerates daily
as a pull request, and how to start the run by hand.

## Acceptance criteria

- S-001-1: `.github/workflows/postman-regenerate.yml` runs on a daily `schedule` at 06:00 UTC and on `workflow_dispatch`, on a GitHub-hosted runner, with only `contents: write` and `pull-requests: write` permissions and a concurrency group
- S-001-2: when the regenerated collection equals the one on `main` and no regeneration pull request is open, the run succeeds and creates no branch, commit, or pull request
- S-001-3: when it differs and no regeneration pull request is open, the run pushes `postman/regenerate`, one commit on the current `main` changing only `postman/appstorespy.postman_collection.json`, and opens one pull request to `main` titled `Regenerate the Postman collection from openapi.json <info.version>`
- S-001-4: when it differs and a regeneration pull request is open, the run force-updates `postman/regenerate` and retitles that pull request, and the repository still has exactly one open pull request from that branch
- S-001-5: when it equals `main` and a regeneration pull request is open, the run closes that pull request with a comment saying `main` already matches the contract, and deletes `postman/regenerate`
- S-001-6: the run runs `tools/generate_postman.py --check` on the regenerated tree before pushing, and a failing check fails the run with nothing pushed
- S-001-7: a failed fetch of the contract fails the run, with no branch pushed and no pull request opened, changed, or closed
- S-001-8: `README.md` says the collection regenerates daily as a pull request and names the workflow to run by hand

## Out of scope

- A trigger from as-rest on deploy (`repository_dispatch`): it needs a token in as-rest; this workflow's `workflow_dispatch` is the hook a later trigger can call
- Documenting the contract change in the README: that is G-1's work, which the regeneration pull request signals but does not do
- A changelog fragment in the regeneration pull request (see Decisions for you in the spec pull request)

## Decisions relied on

- none

## Issues

The build issues, filled in once they are filed: one `- owner/repo#N: S-001-1, S-001-2` per
line, naming the criteria that issue delivers. Each criterion belongs to exactly one.

## Verification

Filled in when the spec reaches `built`: one line per criterion id, saying how it was
checked against the default branch (beyond its tests) and the result.
