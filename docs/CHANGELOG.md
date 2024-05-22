# CHANGELOG



## v1.4.6 (2024-05-22)

### Fix

* fix: revert to original pass through of datetime object ([`45dcd1e`](https://github.com/mbari-org/aidata/commit/45dcd1e0ce238da023b62f209d17f60e2eeabbe9))

* fix: correct load_bulk_boxes args and attribute mapping for redis load ([`33497f5`](https://github.com/mbari-org/aidata/commit/33497f5156d745ff36666dc11c6d13943b117fd4))

### Performance

* perf: remove audio and reduce frame rate to 24 for .git ([`2a5a9f9`](https://github.com/mbari-org/aidata/commit/2a5a9f972c1518a8dc96f3206590e13a06020188))

* perf: handle variable case attribues ([`01db568`](https://github.com/mbari-org/aidata/commit/01db568e178fdf6f5c08971bcc3caf74a7886e42))


## v1.4.5 (2024-05-22)

### Performance

* perf: remove palette gen for speed-up of video gif creation ([`5adaa02`](https://github.com/mbari-org/aidata/commit/5adaa022f1e6609ffd09d4ee04ae571b902e5750))


## v1.4.4 (2024-05-21)

### Performance

* perf: speed-up 64x speed ([`e5902f2`](https://github.com/mbari-org/aidata/commit/e5902f2ba8fe66e62dcd8bda43e73ee5516f5d1a))


## v1.4.3 (2024-05-21)

### Documentation

* docs: added in load/download docs and adding in  CHANGELOG.md ([`d228937`](https://github.com/mbari-org/aidata/commit/d228937ee7b08b321b5b73b091d3ce6465c6d1cc))

### Fix

* fix: correct key for datetime attribute format ([`84eabaf`](https://github.com/mbari-org/aidata/commit/84eabaf5041ed52e080196bf4af7975e437abce7))


## v1.4.2 (2024-05-16)

### Fix

* fix: correct import path ([`4c04a4d`](https://github.com/mbari-org/aidata/commit/4c04a4d5886ffa7bdb93b7ff65ee3fb4c3fab1dc))


## v1.4.1 (2024-05-16)

### Fix

* fix: add missing files ([`b2fe084`](https://github.com/mbari-org/aidata/commit/b2fe084179145f2a81d0266e62412c6efeb3b80c))


## v1.4.0 (2024-05-10)

### Documentation

* docs: minor fix to checkout and more explicit naming of path ([`eb509e6`](https://github.com/mbari-org/aidata/commit/eb509e635e3c66420d0835793381298f59eee7a3))

* docs: minor update to add token to examples ([`78971c4`](https://github.com/mbari-org/aidata/commit/78971c4dd5ab1efd390b5ab05a0985f2adc90866))

### Feature

* feat: some refactoring but mostly addition of support for versioning ([`70b958a`](https://github.com/mbari-org/aidata/commit/70b958a99bd8d38cacb765555e53c90aaa1ca00e))


## v1.3.0 (2024-05-02)

### Feature

* feat: added support to pass in max-images which is useful with --dry-run ([`617e011`](https://github.com/mbari-org/aidata/commit/617e0110e3c1874082f43dc719d4c10dd22ccf82))

### Fix

* fix: adjustments to match Fernandas generated test images ([`4cfcbff`](https://github.com/mbari-org/aidata/commit/4cfcbffe713abfbab4fcfefca4810fd905751927))


## v1.2.3 (2024-05-01)

### Fix

* fix: remove return to load all ([`bfe312f`](https://github.com/mbari-org/aidata/commit/bfe312f9939b861be3428eca4e14d776edd9be91))


## v1.2.2 (2024-04-29)

### Fix

* fix: skip over images with no metadata and minor logging fix ([`4790efe`](https://github.com/mbari-org/aidata/commit/4790efede4ba0f1e6aed3303c51296b732063915))


## v1.2.1 (2024-04-29)

### Build

* build: added missing dependency ([`8fad096`](https://github.com/mbari-org/aidata/commit/8fad0969a1e3b847f012047e36dab49982955b3a))

### Documentation

* docs: added hint for dry-run and hostname ([`e141d9f`](https://github.com/mbari-org/aidata/commit/e141d9ff99603da7264e3129313f4faad81d0e49))

### Fix

* fix: return dataframe and process in sorted order for convenience ([`1069369`](https://github.com/mbari-org/aidata/commit/10693697b639d0d513470e7a9ff07718a79003ab))

* fix: correct path to SONY plugin ([`6a8ea75`](https://github.com/mbari-org/aidata/commit/6a8ea75a7d7477b753e4285d47a36115ffedecac))

* fix: correct path for loading SONY images ([`6f8ce47`](https://github.com/mbari-org/aidata/commit/6f8ce47d59d7b5935d38af094b793fdbc9c0fc9b))

* fix: added missing host for CFE ([`5bbf029`](https://github.com/mbari-org/aidata/commit/5bbf0296b6584b400e1d01aded6bd1f2747070f0))


## v1.2.0 (2024-04-29)

### Feature

* feat: support both png and jpg uppercase SONY images ([`db59ee5`](https://github.com/mbari-org/aidata/commit/db59ee55ba9abdebb2fb2ce8a777c58737727b85))

* feat: support both png and jpg SONY images ([`a02a46a`](https://github.com/mbari-org/aidata/commit/a02a46ad2c74903e621cb9f69ec9de97aeec7a70))

### Fix

* fix: minor type ([`168d258`](https://github.com/mbari-org/aidata/commit/168d25882a18310900240c0f5dcf28caffa1a8d9))


## v1.1.0 (2024-04-29)

### Feature

* feat: added support for extracing sony mdata for UAV ([`60e8d76`](https://github.com/mbari-org/aidata/commit/60e8d76543a12861cbbf610a0a24b5bd589f44a0))


## v1.0.4 (2024-04-25)

### Fix

* fix: added missing host for UAV image load ([`0bc6cab`](https://github.com/mbari-org/aidata/commit/0bc6cab07b319fcdf18136c0b397a6d087a4deac))


## v1.0.3 (2024-03-26)

### Fix

* fix: correct path to data in test database ([`b1fc26e`](https://github.com/mbari-org/aidata/commit/b1fc26e209e7c699b3731009173f7d461fd129ea))


## v1.0.2 (2024-03-26)

### Fix

* fix: correct formatting for the cluster string ([`d934276`](https://github.com/mbari-org/aidata/commit/d9342769c5ab908b5b21eceabe0b6fcd947abbda))


## v1.0.1 (2024-03-25)

### Documentation

* docs: consistent example ([`db608bf`](https://github.com/mbari-org/aidata/commit/db608bf739ea1429ba19132e1b580d1a8240b9f0))

* docs: added missing doc images ([`5532f33`](https://github.com/mbari-org/aidata/commit/5532f33dcc3bf5400dfc27308ee677e760e151bb))

### Fix

* fix: fix bug that downloads everything ([`0d35dde`](https://github.com/mbari-org/aidata/commit/0d35ddee917f531c497b551c0e105a254268717f))

### Unknown

* doc: update to fix typo ([`6abefda`](https://github.com/mbari-org/aidata/commit/6abefda888915bb03ca9a905b8ef1ffdc8d8a973))


## v1.0.0 (2024-03-16)

### Feature

* feat: initial commit ([`7f2ab8b`](https://github.com/mbari-org/aidata/commit/7f2ab8b79b3ee019a2dd0ee278a030d8380920e3))
