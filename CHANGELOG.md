# CHANGELOG


## v1.41.0 (2025-01-23)

### Features

- Added flag to download all unverified data, e.g. --unverified python aidata download dataset --voc
  --token <token> --config /tmp/uav/config.yml --base-path /mnt/ML_SCRATCH/uav --min-score 0.5
  --crop-roi --resize 224 --labels "all" --unverified
  ([`99d4061`](https://github.com/mbari-org/aidata/commit/99d4061656e43ee066b72474e5824b931e000462))


## v1.40.1 (2025-01-22)

### Bug Fixes

- Handle missing score and cluster attributes when combining versions
  ([`65a96ba`](https://github.com/mbari-org/aidata/commit/65a96ba9c73e6d2d2fccf4c7fff8ed02a672d560))


## v1.40.0 (2025-01-22)

### Features

- Download all versions by default and combine via NMS; this is potentially a breaking change for
  downstream that relies on the Baseline naming convention. Remove Baseline from the root directory
  name on datasets
  ([`f91a3bc`](https://github.com/mbari-org/aidata/commit/f91a3bc63c6ffd6faff6943a429aec068403cee2))


## v1.39.0 (2025-01-16)

### Features

- Add database id and box coordinates to the localizations.csv output
  ([`a9f38cf`](https://github.com/mbari-org/aidata/commit/a9f38cf606dbf2a0879737deff713ffd79c24c5b))


## v1.38.0 (2025-01-14)

### Features

- Handle missing secondary labels/scores during download
  ([`e24fd3c`](https://github.com/mbari-org/aidata/commit/e24fd3cb682ff141a2f4c01f44cb53673fc466fc))


## v1.37.0 (2025-01-14)

### Documentation

- Added descriptions for just recipes
  ([`6671d68`](https://github.com/mbari-org/aidata/commit/6671d6831642834726e84276989f3705a3dd9262))

### Features

- Added export of csv with media,cluster,label,score,label_s,score_s for downstream analysis
  ([`690ba60`](https://github.com/mbari-org/aidata/commit/690ba60ab2303a1a624f4d06db50f5a7776f6580))


## v1.36.2 (2025-01-10)

### Bug Fixes

- Larger batch size for ffmpeg roi crop
  ([`68a6fe9`](https://github.com/mbari-org/aidata/commit/68a6fe933f95f9ae20c8ae3e9e1df2ac311af222))


## v1.36.1 (2025-01-10)

### Bug Fixes

- Correct depth query
  ([`3801cc4`](https://github.com/mbari-org/aidata/commit/3801cc40aa7f0f06b8bc5d5d0e6142cefd756452))

- Handle crops from images with whitespaces
  ([`e6e2b5b`](https://github.com/mbari-org/aidata/commit/e6e2b5b05a502ac13635a70dafd4221e3cde3c41))


## v1.36.0 (2025-01-06)

### Bug Fixes

- Correct related attribute query
  ([`1eb5202`](https://github.com/mbari-org/aidata/commit/1eb52022630ff50b35fabf01bf02144992f5625c))

### Documentation

- Minor reorg and update docker info
  ([`ba00cf0`](https://github.com/mbari-org/aidata/commit/ba00cf0f0126e71f7937d906bb9750753c16ef69))

### Features

- Added support for minimum score in load boxes command and truncate exactly min boxes
  ([`91f3e65`](https://github.com/mbari-org/aidata/commit/91f3e657709bed9b75d9c51d389d10ee0cd311ec))


## v1.35.7 (2025-01-01)

### Bug Fixes

- Remove any unused media attributes
  ([`6a05cb1`](https://github.com/mbari-org/aidata/commit/6a05cb1800f42d31774dc5923194a8350aa590b9))


## v1.35.6 (2024-12-31)

### Bug Fixes

- Add missing arg for ffmpeg image crop that was munged during refactor
  ([`a8e3a17`](https://github.com/mbari-org/aidata/commit/a8e3a173ee4bf468aa4403af6bf3569fbd1ba9e1))

- Rename plugins that load media; image_path should be media_path to support both image/video loads
  ([`324fab8`](https://github.com/mbari-org/aidata/commit/324fab8a20b2224defb26beecf87c4d943ea209d))


## v1.35.5 (2024-12-27)

### Performance Improvements

- 2x speed-up for ROI crop
  ([`7b5c43e`](https://github.com/mbari-org/aidata/commit/7b5c43e5889fc4df926142538a8b112e4bf587f4))


## v1.35.4 (2024-12-21)

### Bug Fixes

- Correct query format for video name
  ([`441e2f6`](https://github.com/mbari-org/aidata/commit/441e2f625f775df83badadf72b38b5e0f63ab60f))

- Handle white space in video path
  ([`76ca6fe`](https://github.com/mbari-org/aidata/commit/76ca6fe95a61260d9bfa151b55990744c1692b0f))


## v1.35.3 (2024-12-21)


## v1.35.2 (2024-12-21)

### Bug Fixes

- Minor fix to assign mime first choice
  ([`e0913ef`](https://github.com/mbari-org/aidata/commit/e0913ef84ce168fb925e325db6d5713b608e92cf))

- Minor fix to report correct name when video already loaded
  ([`775bb93`](https://github.com/mbari-org/aidata/commit/775bb93cf5c0ce6ac3892ec57e7cd9af19e05b54))

- **cfe**: Index video correctly for cfe isiis
  ([`1b09ed8`](https://github.com/mbari-org/aidata/commit/1b09ed8b2f811214ac48bb323619e7f9f67f09aa))


## v1.35.1 (2024-12-21)

### Bug Fixes

- Correct indexing for cfe media load
  ([`deff02c`](https://github.com/mbari-org/aidata/commit/deff02c043760a77ef3ca33aae92c8bd5fb31ed1))

### Build System

- Add moviepy==2.1.1 to support video metadata extraction
  ([`cd7b06e`](https://github.com/mbari-org/aidata/commit/cd7b06ede3c4d92db9ba55b4bcae1b07dc04779b))

### Documentation

- Minor update in load help for clarity
  ([`70635f0`](https://github.com/mbari-org/aidata/commit/70635f039ee15a3f532509011a1eb97a26753203))


## v1.35.0 (2024-12-20)

### Documentation

- Minor typo
  ([`c746ecb`](https://github.com/mbari-org/aidata/commit/c746ecb9b70ac740d15613aebf6998e6feae8844))

### Features

- Load CFE ISIIS video
  ([`6c20301`](https://github.com/mbari-org/aidata/commit/6c20301de8d7194d53ec4188cc8bd625d74a2512))


## v1.34.2 (2024-12-19)


## v1.34.1 (2024-12-19)

### Bug Fixes

- Merge conflict
  ([`e876177`](https://github.com/mbari-org/aidata/commit/e87617733304a07666821d73f9d9cf427df6cc4a))

- Merge conflict
  ([`ccfdd89`](https://github.com/mbari-org/aidata/commit/ccfdd894a64d678ca82716ecb504654758dd5fd1))

### Performance Improvements

- Reduce delay for redis load and more robust handling of different label payload
  ([`032d958`](https://github.com/mbari-org/aidata/commit/032d9588c4150eaacd8a6058ee03a0bab185f343))


## v1.34.0 (2024-12-12)

### Features

- Handle 2015-03-07T20:53:01.065Z media timestamp and different cases of label in redis load
  ([`be97c0f`](https://github.com/mbari-org/aidata/commit/be97c0f0465e20e5c1e9905e13f1514d31e4ae3e))


## v1.33.0 (2024-12-06)

### Features

- Separate crops by label and output stats.json to compatible format as voc-cropper
  ([`0d068d8`](https://github.com/mbari-org/aidata/commit/0d068d8ed97f2893d42cedb78eca238c98942870))


## v1.32.0 (2024-12-03)

### Features

- Added support to download ROIs in optimized formats for training from either video or images with
  python aidata download dataset --crop-roi --resize 224 etc.
  ([`9469a49`](https://github.com/mbari-org/aidata/commit/9469a49fd0b0df137e4003cd18027a5f171c37c1))


## v1.31.1 (2024-11-21)

### Bug Fixes

- For coco/voc only download images and no video
  ([`779a1f0`](https://github.com/mbari-org/aidata/commit/779a1f07d6f725dc7a142bdf37a0b05e9f213bcf))


## v1.31.0 (2024-11-17)

### Features

- Remove any duplicate localizations on redis load
  ([`d3a54d2`](https://github.com/mbari-org/aidata/commit/d3a54d2c06a174cc3fc37a0305b9c9830abfd042))


## v1.30.3 (2024-11-08)

### Bug Fixes

- Correct handling of related attribute depth
  ([`8f85ed3`](https://github.com/mbari-org/aidata/commit/8f85ed309087e2e7acca67cd301407803cb01351))


## v1.30.2 (2024-10-29)

### Bug Fixes

- Correct handling of related media attributes, e.g. --depth 1000 or --section 1000m during download
  ([`4af87cc`](https://github.com/mbari-org/aidata/commit/4af87cc43245f427bb7fc14b1d1096416259f495))


## v1.30.1 (2024-10-28)

### Bug Fixes

- Correct handling of related media attributes, e.g. --depth 1000 or --section 1000m during download
  ([`82054b5`](https://github.com/mbari-org/aidata/commit/82054b57ef53decac7b5e16b033a528b76e1269d))


## v1.30.0 (2024-10-25)

### Features

- Exclude more than one label, e.g. --exclude Unknown --exclude Batray in load boxes
  ([`7b2cfc9`](https://github.com/mbari-org/aidata/commit/7b2cfc948da847acdade39ea0c4980a3d93ded95))


## v1.29.1 (2024-10-21)


## v1.29.0 (2024-10-21)

### Bug Fixes

- Merge conflicts
  ([`a72ee0d`](https://github.com/mbari-org/aidata/commit/a72ee0d45d394a2a60ceb5e66a209274e63938ca))

### Features

- **cfe**: Support loading individual cfe images
  ([`08480c3`](https://github.com/mbari-org/aidata/commit/08480c3ae3254e9bc344980799225d09d84b51e3))


## v1.28.0 (2024-10-18)

### Features

- Support any named exemplar
  ([`9846da2`](https://github.com/mbari-org/aidata/commit/9846da2fabcda60e5fe44f34af8d9a08afad42ce))


## v1.27.0 (2024-10-16)

### Features

- Added --max-saliency option to download
  ([`af6a0df`](https://github.com/mbari-org/aidata/commit/af6a0df30396395dbc344e37343495f6cdf4f433))


## v1.26.2 (2024-10-12)

### Bug Fixes

- Handle missing float/int attributes
  ([`58aa320`](https://github.com/mbari-org/aidata/commit/58aa320650e97f61f181b8f12b72258daa31a009))


## v1.26.1 (2024-10-09)

### Bug Fixes

- Correctly load single voc/sdcat file
  ([`96fe1dc`](https://github.com/mbari-org/aidata/commit/96fe1dc4451ddf96c614d66cbdecadb9bfcd28cd))


## v1.26.0 (2024-10-09)

### Documentation

- Minor update to command help to include voc
  ([`827e3d6`](https://github.com/mbari-org/aidata/commit/827e3d677318c79589fd1a6ce52ba021e0b35626))

- Minor update to command help to include voc
  ([`540b24e`](https://github.com/mbari-org/aidata/commit/540b24ef44bc82fa7ee4517445d79e77e81ba8f5))

### Features

- Added support for collapsing to a single class during download with --single-class
  ([`d915e3b`](https://github.com/mbari-org/aidata/commit/d915e3b25c1986555894d4b45889614b089a8a4f))

### Performance Improvements

- Handle missing video frame rate/codec, more performant queue based loads and handle different
  timecode payloads
  ([`c2e1209`](https://github.com/mbari-org/aidata/commit/c2e120928878803d51f811d53f244fca6ea6b460))


## v1.25.0 (2024-10-08)

### Documentation

- Added update to README.md
  ([`d327cfd`](https://github.com/mbari-org/aidata/commit/d327cfd11bd684307565d8cc04300a006056f502))

### Features

- Added support to load from voc
  ([`8752165`](https://github.com/mbari-org/aidata/commit/8752165706a836d697156114062eb71a5904662b))


## v1.24.0 (2024-10-07)

### Documentation

- Minor typo fis
  ([`4b1ff60`](https://github.com/mbari-org/aidata/commit/4b1ff60e0740f60aa6ee86466e8a92be18b2986d))

### Features

- Support exclusion of single label, e.g. Unknown with load boxes
  ([`626ab3b`](https://github.com/mbari-org/aidata/commit/626ab3b4cf0018b3b8dfac2ba3c1e1c6abbe7a5a))


## v1.23.2 (2024-10-04)

### Bug Fixes

- Support redis port/host/password
  ([`f7863eb`](https://github.com/mbari-org/aidata/commit/f7863eb9826758e43a240c79c5fcb54c18fbba4b))


## v1.23.1 (2024-10-01)

### Bug Fixes

- **uav**: Correct media date
  ([`6336d05`](https://github.com/mbari-org/aidata/commit/6336d05134accd3afa464fe7d91f62813bcbeb41))


## v1.23.0 (2024-09-29)

### Features

- Add support for --min-score in download dataset
  ([`ecefeff`](https://github.com/mbari-org/aidata/commit/ecefeffe1932af3f7dba2e6d109d3908fa8e3a16))


## v1.22.0 (2024-09-22)

### Bug Fixes

- Albumentations dependency break
  ([`272dbad`](https://github.com/mbari-org/aidata/commit/272dbad703ced81aae3d4c21595fce7662ed4291))

### Features

- Add support for --min-saliency in download dataset
  ([`6b26110`](https://github.com/mbari-org/aidata/commit/6b26110d663fed6fcddda02bbe20816807722102))


## v1.21.1 (2024-09-20)

### Performance Improvements

- Slimmer memory footprint for downloads. working for 360k download and export for CFE ROIs
  ([`1fd1e37`](https://github.com/mbari-org/aidata/commit/1fd1e37ad367c0e20016e533c519b119de977661))


## v1.21.0 (2024-09-19)

### Features

- Added support for --section in download
  ([`46754af`](https://github.com/mbari-org/aidata/commit/46754af01522cbf126911bbc1137eefdf496e858))


## v1.20.0 (2024-09-19)

### Documentation

- Add missing images
  ([`7404156`](https://github.com/mbari-org/aidata/commit/74041564549641413e59d0bce877109e1d646cb3))

- Correct link to docs
  ([`0ef4f4f`](https://github.com/mbari-org/aidata/commit/0ef4f4faca2dc754bbe61060a89561acb5320093))

- Just some refactoring of setup docs
  ([`afe109f`](https://github.com/mbari-org/aidata/commit/afe109f9e7bad0808d60b68244f9f48b9b9404ae))

### Features

- Transformresize ([#18](https://github.com/mbari-org/aidata/pull/18),
  [`9a3e877`](https://github.com/mbari-org/aidata/commit/9a3e8777e12dbfd87c93a1c28b1a3eb0e6fff5ee))

Adds the option --resize to the transform to transform with a resize. Useful for training models
  with scales of the same image. For tiny boxes that may result in downsizing, the option --min-dim
  supports removal at them; this defaults to 10 pixels in any dimension


## v1.19.0 (2024-09-16)

### Features

- Add Planktivore media support ([#17](https://github.com/mbari-org/aidata/pull/17),
  [`78a9de3`](https://github.com/mbari-org/aidata/commit/78a9de346578f884d64491fb0cd21bb350e6b18b))

* feat: added test and config for loading planktivore

* docs: more detail on test/dev setup and added in redis to test

* test: correct tests conf that aligns to doc

* docs: correct link to database

* chore: added in more just recipes for testing


## v1.18.0 (2024-09-05)

### Features

- Add support to different models
  ([`b1f7c52`](https://github.com/mbari-org/aidata/commit/b1f7c52f3df5032c255d124b762eaa0a5a571a25))


## v1.17.1 (2024-09-04)

### Performance Improvements

- Bump to better indexing
  ([`a24bfb7`](https://github.com/mbari-org/aidata/commit/a24bfb7e40814dd31c2991720df064f6d7e4b0a6))


## v1.17.0 (2024-09-03)

### Features

- Replace underscore with colon in redis hash store of exemplars
  ([`fb4363a`](https://github.com/mbari-org/aidata/commit/fb4363a18ea8d50dcf79847f012f1c12f082497b))


## v1.16.0 (2024-09-01)

### Features

- Added redis document id fetch
  ([`04f1a7a`](https://github.com/mbari-org/aidata/commit/04f1a7a84cc68d713073bb494409a4d8998fe9f9))


## v1.15.0 (2024-09-01)

### Features

- Replace index id with database id for exemplars
  ([`0ce8e17`](https://github.com/mbari-org/aidata/commit/0ce8e171b777238e7d99b0f10a8772e1c121b3cf))


## v1.14.0 (2024-08-30)

### Features

- Disable flagging exexmplars
  ([`a193a74`](https://github.com/mbari-org/aidata/commit/a193a74a8e3d58b191ce225fd8d1b328e6f4bc9f))


## v1.13.0 (2024-08-29)

### Documentation

- Updated docs and and config with better test setup
  ([`da554be`](https://github.com/mbari-org/aidata/commit/da554bef94c746536f0ef64828465393a01fbd42))

- Updated docs and and config with better test setup
  ([`8a0c57c`](https://github.com/mbari-org/aidata/commit/8a0c57cc820d9e6cb0384f6faf70341c0eead21f))

### Features

- Added support for depth parsing
  ([`7a0b61a`](https://github.com/mbari-org/aidata/commit/7a0b61a2a0c2fa1393912e69a1956d1458f72ae7))


## v1.12.2 (2024-08-26)

### Bug Fixes

- Handle empty query operators
  ([`b9089b1`](https://github.com/mbari-org/aidata/commit/b9089b1e6a73c6e663183cc451d92dd8f5437989))


## v1.12.1 (2024-08-22)

### Bug Fixes

- Trigger release to update __init__.py
  ([`553aa2d`](https://github.com/mbari-org/aidata/commit/553aa2ddeff37f75142007da2a02c9fa863ac9fb))

### Documentation

- Minor correction to reflect correct path to docs
  ([`a0c5485`](https://github.com/mbari-org/aidata/commit/a0c54857003e2b9bb9c1258d819b6c32c2bc1e1c))


## v1.12.0 (2024-08-16)

### Bug Fixes

- Correct handling of label map
  ([`828c7d4`](https://github.com/mbari-org/aidata/commit/828c7d48560760bb8a11920731ce1c72294fa4af))

- Handle conversion errors outside of normalized 0-1 coordinates
  ([`c210ab2`](https://github.com/mbari-org/aidata/commit/c210ab2d2c59c095ca4d890898cd368ac2225313))

### Build System

- Added missing albumentations library
  ([`523f4a9`](https://github.com/mbari-org/aidata/commit/523f4a99b9811effadff3dc9cf43a91e5208b1e1))

### Documentation

- Added detail on .env file
  ([`dcd3137`](https://github.com/mbari-org/aidata/commit/dcd313773c84e1f57a8504b0a1365212cf435d70))

- Correct link to internal docs
  ([`208c6a8`](https://github.com/mbari-org/aidata/commit/208c6a8c1e2550fb5e81a492a65fa19542322ce6))

- Moved CHANGELOG
  ([`e5e564d`](https://github.com/mbari-org/aidata/commit/e5e564da9b172d6815964d6fec8f3309ec969c6e))

- Removed docs which are now in another repo and added commands for ref in README.md
  ([`428d319`](https://github.com/mbari-org/aidata/commit/428d319d2a925acf830b52da7cc95a83501fb4c1))

- Resolve conflict
  ([`5c44451`](https://github.com/mbari-org/aidata/commit/5c44451a1d94824394515c2b37320f597ddb0a4c))

- Updated with correct link to docs
  ([`2c65a57`](https://github.com/mbari-org/aidata/commit/2c65a57020d923d6bb63179bea04cadee694971f))

### Features

- Addded voc_to_yolo
  ([`4646d14`](https://github.com/mbari-org/aidata/commit/4646d143d9c356e0cd6776ff8747e46bf017146b))

- Added transform for voc only
  ([`3b1dc6d`](https://github.com/mbari-org/aidata/commit/3b1dc6db4c6ae55919d157afaf3e781621f777df))

- Added transform for voc only
  ([`54b72d0`](https://github.com/mbari-org/aidata/commit/54b72d0224f0df7a13b20e41c7256bf5eead777a))


## v1.11.0 (2024-08-08)

### Features

- Added label counts to /labels/{project_name}
  ([`dae93ed`](https://github.com/mbari-org/aidata/commit/dae93ede973c8d2395e4f239e952cf799b3272fe))


## v1.10.0 (2024-08-05)

### Documentation

- Added project image
  ([`c45e7ea`](https://github.com/mbari-org/aidata/commit/c45e7ea2d091a94d4fe77e5b89d6a27a22209b3b))

- Fixed links and added clickable link to mantis
  ([`7688bbe`](https://github.com/mbari-org/aidata/commit/7688bbef6d6444a57eface9a62430c7f15f4a008))

### Features

- Added verified --verified to download
  ([`8c5f124`](https://github.com/mbari-org/aidata/commit/8c5f12475f3a5409c1fdfbe785155b8e5e6bd887))


## v1.9.0 (2024-08-05)

### Features

- Added database reset and cleane up docs
  ([`f87387a`](https://github.com/mbari-org/aidata/commit/f87387aacfda0addece80cfc734baf6ca57c5e05))


## v1.8.0 (2024-07-26)

### Features

- Add load to exemplar bool which is helpful for visualization
  ([`10b9443`](https://github.com/mbari-org/aidata/commit/10b944374d1e3f9aff1648e99367c191dd47f737))


## v1.7.4 (2024-07-26)

### Bug Fixes

- Correct default for max-images to load all
  ([`5e5d10a`](https://github.com/mbari-org/aidata/commit/5e5d10aa0e65376b5d0f2408ce0daf29f51ec406))


## v1.7.3 (2024-07-24)

### Bug Fixes

- Correct parsing of class names and cuda device enable
  ([`f339b18`](https://github.com/mbari-org/aidata/commit/f339b185643b008571ec55689b486ddeb9d4f31c))


## v1.7.2 (2024-07-23)

### Bug Fixes

- Correct handling of exemplars
  ([`a0ee097`](https://github.com/mbari-org/aidata/commit/a0ee09719719a2eff5044d7458b089033778500f))

### Build System

- Correct docker build path
  ([`2fedee1`](https://github.com/mbari-org/aidata/commit/2fedee1433fe49828304af87d2d36bde1f7dac91))

- Exclude py12 which is problematic with transformers library
  ([`1b2c09f`](https://github.com/mbari-org/aidata/commit/1b2c09f994f802946fbffed86997268606a114e8))

- Remove legacy "ENV key value" in Dockerfile.cuda
  ([`d7fd3eb`](https://github.com/mbari-org/aidata/commit/d7fd3eb9164ba1b01e0be2dcacf087cab29122ce))


## v1.7.1 (2024-07-23)

### Bug Fixes

- Correct handling of version arg
  ([`7ee9a42`](https://github.com/mbari-org/aidata/commit/7ee9a42b0d00d8f3aac363663903ca25fdd70f2a))


## v1.7.0 (2024-07-23)

### Features

- Added password pass through to redis
  ([`39b0726`](https://github.com/mbari-org/aidata/commit/39b07262437f9e9e3459c053924d42d4228d8348))


## v1.6.4 (2024-07-23)

### Performance Improvements

- Move model to gpu and some minor refactoring for clarity
  ([`999e59c`](https://github.com/mbari-org/aidata/commit/999e59c54b00eb9063db2daed779e9bd8f0bf3cc))


## v1.6.3 (2024-07-22)

### Bug Fixes

- Minor fix in exemplar args and more logging
  ([`2153af9`](https://github.com/mbari-org/aidata/commit/2153af9275a30751689025013297494f899af8f4))


## v1.6.2 (2024-07-19)

### Bug Fixes

- Handled empty labels, bad media, and more reporting of progress
  ([`a31ef83`](https://github.com/mbari-org/aidata/commit/a31ef83e2b72762b36e086cffd118ee517c3b84c))


## v1.6.1 (2024-07-18)

### Bug Fixes

- Bugs from typecheck
  ([`cf3020a`](https://github.com/mbari-org/aidata/commit/cf3020a8cbd428065edcc6925dbaaf700f5138ab))

### Build System

- Removed unused imports and bump torch to python3.11 compatible and
  ([`7d2d786`](https://github.com/mbari-org/aidata/commit/7d2d7866d21fd29823f55c24538c535a24ec8127))


## v1.6.0 (2024-07-05)

### Bug Fixes

- Remove whitespace and move exemplar to load
  ([`decd1e6`](https://github.com/mbari-org/aidata/commit/decd1e67fea4bb9e43d5162e1478ab4f4825cbf4))

### Features

- Added sdcat exemplar load
  ([`a8e42f0`](https://github.com/mbari-org/aidata/commit/a8e42f071d5b3942b2bdb2d183112b8703167ad4))


## v1.5.0 (2024-06-25)

### Documentation

- Improved doc on save
  ([`8d1f111`](https://github.com/mbari-org/aidata/commit/8d1f111848d6c7db3134e9f770b5daa09a011456))

### Features

- Pass through the id to the voc output
  ([`72d350f`](https://github.com/mbari-org/aidata/commit/72d350fa847568a56ecb0619bcd118a9fdf5faa8))


## v1.4.7 (2024-06-24)

### Bug Fixes

- Handle fewer records correctly
  ([`aa25d62`](https://github.com/mbari-org/aidata/commit/aa25d62f1f137cd41af4a305c8ed106405b59b2b))


## v1.4.6 (2024-05-22)


## v1.4.5 (2024-05-22)

### Bug Fixes

- Correct load_bulk_boxes args and attribute mapping for redis load
  ([`33497f5`](https://github.com/mbari-org/aidata/commit/33497f5156d745ff36666dc11c6d13943b117fd4))

- Revert to original pass through of datetime object
  ([`45dcd1e`](https://github.com/mbari-org/aidata/commit/45dcd1e0ce238da023b62f209d17f60e2eeabbe9))

### Performance Improvements

- Handle variable case attribues
  ([`01db568`](https://github.com/mbari-org/aidata/commit/01db568e178fdf6f5c08971bcc3caf74a7886e42))

- Remove audio and reduce frame rate to 24 for .git
  ([`2a5a9f9`](https://github.com/mbari-org/aidata/commit/2a5a9f972c1518a8dc96f3206590e13a06020188))

- Remove palette gen for speed-up of video gif creation
  ([`5adaa02`](https://github.com/mbari-org/aidata/commit/5adaa022f1e6609ffd09d4ee04ae571b902e5750))


## v1.4.4 (2024-05-21)

### Performance Improvements

- Speed-up 64x speed
  ([`e5902f2`](https://github.com/mbari-org/aidata/commit/e5902f2ba8fe66e62dcd8bda43e73ee5516f5d1a))


## v1.4.3 (2024-05-21)

### Bug Fixes

- Correct key for datetime attribute format
  ([`84eabaf`](https://github.com/mbari-org/aidata/commit/84eabaf5041ed52e080196bf4af7975e437abce7))

### Documentation

- Added in load/download docs and adding in CHANGELOG.md
  ([`d228937`](https://github.com/mbari-org/aidata/commit/d228937ee7b08b321b5b73b091d3ce6465c6d1cc))


## v1.4.2 (2024-05-16)

### Bug Fixes

- Correct import path
  ([`4c04a4d`](https://github.com/mbari-org/aidata/commit/4c04a4d5886ffa7bdb93b7ff65ee3fb4c3fab1dc))


## v1.4.1 (2024-05-16)

### Bug Fixes

- Add missing files
  ([`b2fe084`](https://github.com/mbari-org/aidata/commit/b2fe084179145f2a81d0266e62412c6efeb3b80c))


## v1.4.0 (2024-05-10)

### Documentation

- Minor fix to checkout and more explicit naming of path
  ([`eb509e6`](https://github.com/mbari-org/aidata/commit/eb509e635e3c66420d0835793381298f59eee7a3))

- Minor update to add token to examples
  ([`78971c4`](https://github.com/mbari-org/aidata/commit/78971c4dd5ab1efd390b5ab05a0985f2adc90866))

### Features

- Some refactoring but mostly addition of support for versioning
  ([`70b958a`](https://github.com/mbari-org/aidata/commit/70b958a99bd8d38cacb765555e53c90aaa1ca00e))


## v1.3.0 (2024-05-02)

### Bug Fixes

- Adjustments to match Fernandas generated test images
  ([`4cfcbff`](https://github.com/mbari-org/aidata/commit/4cfcbffe713abfbab4fcfefca4810fd905751927))

### Features

- Added support to pass in max-images which is useful with --dry-run
  ([`617e011`](https://github.com/mbari-org/aidata/commit/617e0110e3c1874082f43dc719d4c10dd22ccf82))


## v1.2.3 (2024-05-01)

### Bug Fixes

- Remove return to load all
  ([`bfe312f`](https://github.com/mbari-org/aidata/commit/bfe312f9939b861be3428eca4e14d776edd9be91))


## v1.2.2 (2024-04-29)

### Bug Fixes

- Skip over images with no metadata and minor logging fix
  ([`4790efe`](https://github.com/mbari-org/aidata/commit/4790efede4ba0f1e6aed3303c51296b732063915))


## v1.2.1 (2024-04-29)

### Bug Fixes

- Added missing host for CFE
  ([`5bbf029`](https://github.com/mbari-org/aidata/commit/5bbf0296b6584b400e1d01aded6bd1f2747070f0))

- Correct path for loading SONY images
  ([`6f8ce47`](https://github.com/mbari-org/aidata/commit/6f8ce47d59d7b5935d38af094b793fdbc9c0fc9b))

- Correct path to SONY plugin
  ([`6a8ea75`](https://github.com/mbari-org/aidata/commit/6a8ea75a7d7477b753e4285d47a36115ffedecac))

- Return dataframe and process in sorted order for convenience
  ([`1069369`](https://github.com/mbari-org/aidata/commit/10693697b639d0d513470e7a9ff07718a79003ab))

### Build System

- Added missing dependency
  ([`8fad096`](https://github.com/mbari-org/aidata/commit/8fad0969a1e3b847f012047e36dab49982955b3a))

### Documentation

- Added hint for dry-run and hostname
  ([`e141d9f`](https://github.com/mbari-org/aidata/commit/e141d9ff99603da7264e3129313f4faad81d0e49))


## v1.2.0 (2024-04-29)

### Bug Fixes

- Minor type
  ([`168d258`](https://github.com/mbari-org/aidata/commit/168d25882a18310900240c0f5dcf28caffa1a8d9))

### Features

- Support both png and jpg SONY images
  ([`a02a46a`](https://github.com/mbari-org/aidata/commit/a02a46ad2c74903e621cb9f69ec9de97aeec7a70))

- Support both png and jpg uppercase SONY images
  ([`db59ee5`](https://github.com/mbari-org/aidata/commit/db59ee55ba9abdebb2fb2ce8a777c58737727b85))


## v1.1.0 (2024-04-29)

### Features

- Added support for extracing sony mdata for UAV
  ([`60e8d76`](https://github.com/mbari-org/aidata/commit/60e8d76543a12861cbbf610a0a24b5bd589f44a0))


## v1.0.4 (2024-04-25)

### Bug Fixes

- Added missing host for UAV image load
  ([`0bc6cab`](https://github.com/mbari-org/aidata/commit/0bc6cab07b319fcdf18136c0b397a6d087a4deac))


## v1.0.3 (2024-03-26)

### Bug Fixes

- Correct path to data in test database
  ([`b1fc26e`](https://github.com/mbari-org/aidata/commit/b1fc26e209e7c699b3731009173f7d461fd129ea))


## v1.0.2 (2024-03-26)

### Bug Fixes

- Correct formatting for the cluster string
  ([`d934276`](https://github.com/mbari-org/aidata/commit/d9342769c5ab908b5b21eceabe0b6fcd947abbda))


## v1.0.1 (2024-03-25)

### Bug Fixes

- Fix bug that downloads everything
  ([`0d35dde`](https://github.com/mbari-org/aidata/commit/0d35ddee917f531c497b551c0e105a254268717f))

### Documentation

- Added missing doc images
  ([`5532f33`](https://github.com/mbari-org/aidata/commit/5532f33dcc3bf5400dfc27308ee677e760e151bb))

- Consistent example
  ([`db608bf`](https://github.com/mbari-org/aidata/commit/db608bf739ea1429ba19132e1b580d1a8240b9f0))


## v1.0.0 (2024-03-16)

### Features

- Initial commit
  ([`7f2ab8b`](https://github.com/mbari-org/aidata/commit/7f2ab8b79b3ee019a2dd0ee278a030d8380920e3))
