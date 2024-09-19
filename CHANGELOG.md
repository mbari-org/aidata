# CHANGELOG

## v1.21.0 (2024-09-19)

### Feature

* feat: added support for --section in download ([`46754af`](https://github.com/mbari-org/aidata/commit/46754af01522cbf126911bbc1137eefdf496e858))

## v1.20.0 (2024-09-19)

### Documentation

* docs: add missing images ([`7404156`](https://github.com/mbari-org/aidata/commit/74041564549641413e59d0bce877109e1d646cb3))

* docs: correct link to docs ([`0ef4f4f`](https://github.com/mbari-org/aidata/commit/0ef4f4faca2dc754bbe61060a89561acb5320093))

* docs: just some refactoring of setup docs ([`afe109f`](https://github.com/mbari-org/aidata/commit/afe109f9e7bad0808d60b68244f9f48b9b9404ae))

### Feature

* feat: transformresize (#18)

Adds the option --resize to the transform to transform with a resize.  Useful for training models with scales of the same image.   For tiny boxes that may result in downsizing, the option --min-dim supports removal at them; this defaults to 10 pixels in any dimension ([`9a3e877`](https://github.com/mbari-org/aidata/commit/9a3e8777e12dbfd87c93a1c28b1a3eb0e6fff5ee))

## v1.19.0 (2024-09-16)

### Feature

* feat: add Planktivore media support  (#17)

* feat: added test and config for loading planktivore

* docs: more detail on test/dev setup and added in redis to test

* test: correct tests conf that aligns to doc

* docs: correct link to database

* chore: added in more just recipes for testing ([`78a9de3`](https://github.com/mbari-org/aidata/commit/78a9de346578f884d64491fb0cd21bb350e6b18b))

## v1.18.0 (2024-09-05)

### Feature

* feat: add support to different models ([`b1f7c52`](https://github.com/mbari-org/aidata/commit/b1f7c52f3df5032c255d124b762eaa0a5a571a25))

## v1.17.1 (2024-09-04)

### Performance

* perf: bump to better indexing ([`a24bfb7`](https://github.com/mbari-org/aidata/commit/a24bfb7e40814dd31c2991720df064f6d7e4b0a6))

## v1.17.0 (2024-09-03)

### Feature

* feat: replace underscore with colon in redis hash store of exemplars ([`fb4363a`](https://github.com/mbari-org/aidata/commit/fb4363a18ea8d50dcf79847f012f1c12f082497b))

## v1.16.0 (2024-09-01)

### Feature

* feat: added redis document id fetch ([`04f1a7a`](https://github.com/mbari-org/aidata/commit/04f1a7a84cc68d713073bb494409a4d8998fe9f9))

## v1.15.0 (2024-09-01)

### Feature

* feat: replace index id with database id for exemplars ([`0ce8e17`](https://github.com/mbari-org/aidata/commit/0ce8e171b777238e7d99b0f10a8772e1c121b3cf))

## v1.14.0 (2024-08-30)

### Feature

* feat: disable flagging exexmplars ([`a193a74`](https://github.com/mbari-org/aidata/commit/a193a74a8e3d58b191ce225fd8d1b328e6f4bc9f))

## v1.13.0 (2024-08-29)

### Documentation

* docs: updated docs and and config with better test setup ([`da554be`](https://github.com/mbari-org/aidata/commit/da554bef94c746536f0ef64828465393a01fbd42))

* docs: updated docs and and config with better test setup ([`8a0c57c`](https://github.com/mbari-org/aidata/commit/8a0c57cc820d9e6cb0384f6faf70341c0eead21f))

### Feature

* feat: added support for depth parsing ([`7a0b61a`](https://github.com/mbari-org/aidata/commit/7a0b61a2a0c2fa1393912e69a1956d1458f72ae7))

## v1.12.2 (2024-08-26)

### Fix

* fix: handle empty query operators ([`b9089b1`](https://github.com/mbari-org/aidata/commit/b9089b1e6a73c6e663183cc451d92dd8f5437989))

## v1.12.1 (2024-08-22)

### Documentation

* docs: minor correction to reflect correct path to docs ([`a0c5485`](https://github.com/mbari-org/aidata/commit/a0c54857003e2b9bb9c1258d819b6c32c2bc1e1c))

### Fix

* fix: trigger release to update __init__.py ([`553aa2d`](https://github.com/mbari-org/aidata/commit/553aa2ddeff37f75142007da2a02c9fa863ac9fb))

## v1.12.0 (2024-08-16)

### Build

* build: added missing albumentations library ([`523f4a9`](https://github.com/mbari-org/aidata/commit/523f4a99b9811effadff3dc9cf43a91e5208b1e1))

### Documentation

* docs: removed docs which are now in another repo and added commands for ref in README.md ([`428d319`](https://github.com/mbari-org/aidata/commit/428d319d2a925acf830b52da7cc95a83501fb4c1))

* docs: moved CHANGELOG ([`e5e564d`](https://github.com/mbari-org/aidata/commit/e5e564da9b172d6815964d6fec8f3309ec969c6e))

* docs: added detail on .env file ([`dcd3137`](https://github.com/mbari-org/aidata/commit/dcd313773c84e1f57a8504b0a1365212cf435d70))

* docs: resolve conflict ([`5c44451`](https://github.com/mbari-org/aidata/commit/5c44451a1d94824394515c2b37320f597ddb0a4c))

* docs: correct link to internal docs ([`208c6a8`](https://github.com/mbari-org/aidata/commit/208c6a8c1e2550fb5e81a492a65fa19542322ce6))

* docs: updated with correct link to docs ([`2c65a57`](https://github.com/mbari-org/aidata/commit/2c65a57020d923d6bb63179bea04cadee694971f))

### Feature

* feat: addded voc_to_yolo ([`4646d14`](https://github.com/mbari-org/aidata/commit/4646d143d9c356e0cd6776ff8747e46bf017146b))

* feat: added transform for voc only ([`3b1dc6d`](https://github.com/mbari-org/aidata/commit/3b1dc6db4c6ae55919d157afaf3e781621f777df))

* feat: added transform for voc only ([`54b72d0`](https://github.com/mbari-org/aidata/commit/54b72d0224f0df7a13b20e41c7256bf5eead777a))

### Fix

* fix: correct handling of label map ([`828c7d4`](https://github.com/mbari-org/aidata/commit/828c7d48560760bb8a11920731ce1c72294fa4af))

* fix: handle conversion errors outside of normalized 0-1 coordinates ([`c210ab2`](https://github.com/mbari-org/aidata/commit/c210ab2d2c59c095ca4d890898cd368ac2225313))

## v1.11.0 (2024-08-08)

### Feature

* feat: added label counts to /labels/{project_name} ([`dae93ed`](https://github.com/mbari-org/aidata/commit/dae93ede973c8d2395e4f239e952cf799b3272fe))

## v1.10.0 (2024-08-05)

### Documentation

* docs: fixed links and added clickable link to mantis ([`7688bbe`](https://github.com/mbari-org/aidata/commit/7688bbef6d6444a57eface9a62430c7f15f4a008))

* docs: added project image ([`c45e7ea`](https://github.com/mbari-org/aidata/commit/c45e7ea2d091a94d4fe77e5b89d6a27a22209b3b))

### Feature

* feat: added verified --verified to download ([`8c5f124`](https://github.com/mbari-org/aidata/commit/8c5f12475f3a5409c1fdfbe785155b8e5e6bd887))

## v1.9.0 (2024-08-05)

### Feature

* feat: added database reset and cleane up docs ([`f87387a`](https://github.com/mbari-org/aidata/commit/f87387aacfda0addece80cfc734baf6ca57c5e05))

## v1.8.0 (2024-07-26)

### Feature

* feat: add load to exemplar bool which is helpful for visualization ([`10b9443`](https://github.com/mbari-org/aidata/commit/10b944374d1e3f9aff1648e99367c191dd47f737))

## v1.7.4 (2024-07-26)

### Fix

* fix: correct default for max-images to load all ([`5e5d10a`](https://github.com/mbari-org/aidata/commit/5e5d10aa0e65376b5d0f2408ce0daf29f51ec406))

## v1.7.3 (2024-07-24)

### Fix

* fix: correct parsing of class names and cuda device enable ([`f339b18`](https://github.com/mbari-org/aidata/commit/f339b185643b008571ec55689b486ddeb9d4f31c))

## v1.7.2 (2024-07-23)

### Build

* build: remove legacy &#34;ENV key value&#34; in Dockerfile.cuda ([`d7fd3eb`](https://github.com/mbari-org/aidata/commit/d7fd3eb9164ba1b01e0be2dcacf087cab29122ce))

* build: correct docker build path ([`2fedee1`](https://github.com/mbari-org/aidata/commit/2fedee1433fe49828304af87d2d36bde1f7dac91))

* build: exclude py12 which is problematic with transformers library ([`1b2c09f`](https://github.com/mbari-org/aidata/commit/1b2c09f994f802946fbffed86997268606a114e8))

### Fix

* fix: correct handling of exemplars ([`a0ee097`](https://github.com/mbari-org/aidata/commit/a0ee09719719a2eff5044d7458b089033778500f))

## v1.7.1 (2024-07-23)

### Fix

* fix: correct handling of version arg ([`7ee9a42`](https://github.com/mbari-org/aidata/commit/7ee9a42b0d00d8f3aac363663903ca25fdd70f2a))

## v1.7.0 (2024-07-23)

### Feature

* feat: added password pass through to redis ([`39b0726`](https://github.com/mbari-org/aidata/commit/39b07262437f9e9e3459c053924d42d4228d8348))

## v1.6.4 (2024-07-23)

### Performance

* perf: move model to gpu and some minor refactoring for clarity ([`999e59c`](https://github.com/mbari-org/aidata/commit/999e59c54b00eb9063db2daed779e9bd8f0bf3cc))

## v1.6.3 (2024-07-22)

### Fix

* fix: minor fix in exemplar args and more logging ([`2153af9`](https://github.com/mbari-org/aidata/commit/2153af9275a30751689025013297494f899af8f4))

## v1.6.2 (2024-07-19)

### Fix

* fix: handled empty labels, bad media, and more reporting of progress ([`a31ef83`](https://github.com/mbari-org/aidata/commit/a31ef83e2b72762b36e086cffd118ee517c3b84c))

## v1.6.1 (2024-07-18)

### Build

* build: removed unused imports and bump torch to python3.11 compatible and ([`7d2d786`](https://github.com/mbari-org/aidata/commit/7d2d7866d21fd29823f55c24538c535a24ec8127))

### Fix

* fix: bugs from typecheck ([`cf3020a`](https://github.com/mbari-org/aidata/commit/cf3020a8cbd428065edcc6925dbaaf700f5138ab))

## v1.6.0 (2024-07-05)

### Feature

* feat: added sdcat exemplar load ([`a8e42f0`](https://github.com/mbari-org/aidata/commit/a8e42f071d5b3942b2bdb2d183112b8703167ad4))

### Fix

* fix: remove whitespace and move exemplar to load ([`decd1e6`](https://github.com/mbari-org/aidata/commit/decd1e67fea4bb9e43d5162e1478ab4f4825cbf4))

### Unknown

* working exemplar test load ([`88ddc2e`](https://github.com/mbari-org/aidata/commit/88ddc2e4eedd796d5105114d467e50b03e81bb3c))

## v1.5.0 (2024-06-25)

### Documentation

* docs: improved doc on save ([`8d1f111`](https://github.com/mbari-org/aidata/commit/8d1f111848d6c7db3134e9f770b5daa09a011456))

### Feature

* feat: pass through the id to the voc output ([`72d350f`](https://github.com/mbari-org/aidata/commit/72d350fa847568a56ecb0619bcd118a9fdf5faa8))

## v1.4.7 (2024-06-24)

### Fix

* fix: handle fewer records correctly ([`aa25d62`](https://github.com/mbari-org/aidata/commit/aa25d62f1f137cd41af4a305c8ed106405b59b2b))

## v1.4.6 (2024-05-22)

## v1.4.5 (2024-05-22)

### Fix

* fix: revert to original pass through of datetime object ([`45dcd1e`](https://github.com/mbari-org/aidata/commit/45dcd1e0ce238da023b62f209d17f60e2eeabbe9))

* fix: correct load_bulk_boxes args and attribute mapping for redis load ([`33497f5`](https://github.com/mbari-org/aidata/commit/33497f5156d745ff36666dc11c6d13943b117fd4))

### Performance

* perf: remove audio and reduce frame rate to 24 for .git ([`2a5a9f9`](https://github.com/mbari-org/aidata/commit/2a5a9f972c1518a8dc96f3206590e13a06020188))

* perf: handle variable case attribues ([`01db568`](https://github.com/mbari-org/aidata/commit/01db568e178fdf6f5c08971bcc3caf74a7886e42))

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
