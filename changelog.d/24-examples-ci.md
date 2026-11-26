### Added

- CI: the `Examples` workflow runs `examples/quickstart.sh` and `examples/quickstart.py` against the production API daily, on demand, and on pull requests that touch them; without the `API_KEY` secret it skips the calls with a notice (#24)

### Changed

- `examples/quickstart.sh` exits non-zero when a call returns an HTTP error, still printing the error body (#24)
