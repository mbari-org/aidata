# CHANGELOG


## v1.52.1 (2025-04-25)

### Bug Fixes

- Better handling of missing codec that throws None exception for some video
  ([`9d092bc`](https://github.com/mbari-org/aidata/commit/9d092bc250c77889f486471800b2ea10ab19ccb1))

### Documentation

- Updated yaml example to reflect changes from release v.0.48.0
  ([`51b5f1a`](https://github.com/mbari-org/aidata/commit/51b5f1ad3080f503317deee916887d1a4b13f19e))


## v1.52.0 (2025-04-25)

### Documentation

- Minor README.md typo and added some detail on augmentation
  ([`945f042`](https://github.com/mbari-org/aidata/commit/945f0427c505d697816c8007dd389356c34b17fe))

### Features

- Added support for microsecond isoparse 2025-04-25T04:11:23.770409 from redis queue
  ([`00da986`](https://github.com/mbari-org/aidata/commit/00da9862b9eb4f00bb2d9c66319266dc94d271c0))


## v1.51.0 (2025-04-22)

### Features

- Added support for new command e.g. aidata load clusters --config config.yml --token <token>>
  --input clusters.csv --version Baseline
  ([`2fa2e9b`](https://github.com/mbari-org/aidata/commit/2fa2e9bc4f036c148fd6700302a03d0dd549c464))


## v1.50.0 (2025-04-18)

### Features

- Added thumbnail and improved video metadata for video load
  ([`9b72355`](https://github.com/mbari-org/aidata/commit/9b72355cf7938caed1125e9e3bd9c2aa7a1c41ff))


## v1.49.0 (2025-04-15)

### Features

- Add --reset to aidata load queue to support resetting REDIS
  ([`6a7ecd5`](https://github.com/mbari-org/aidata/commit/6a7ecd5024e98621ea4712009379bda23d523c5a))


## v1.48.1 (2025-04-14)

### Bug Fixes

- Switch to defaulting to yaml config only for tator host and fetch video metadata from the file
  only
  ([`78a02d4`](https://github.com/mbari-org/aidata/commit/78a02d4db54d0e963edce57adf0cb10627605a13))


## v1.48.0 (2025-04-10)

### Documentation

- Updated instructions and recipes per latest build steps and some additional excludes in project
  common in dev
  ([`776af45`](https://github.com/mbari-org/aidata/commit/776af45b9645a10e5ec9b1b95b628985b716e9eb))

### Features

- Handle both media mounts with and without complete urls
  ([`225ecc6`](https://github.com/mbari-org/aidata/commit/225ecc6e00355f7736c2079a006deed5ec1cbcb8))


## v1.47.0 (2025-03-28)

### Features

- Create versions during upload if does not exists and more performance bulk loading for ROIs
  ([`f10abbd`](https://github.com/mbari-org/aidata/commit/f10abbd9eb88fa497e71f945a8e655d611b7dd98))


## v1.46.0 (2025-03-28)

### Features

- Added support for config files from a URL and local
  ([`df5d1cd`](https://github.com/mbari-org/aidata/commit/df5d1cdad19117afbd0ddd069cfb63ea151fb77f))


## v1.45.0 (2025-03-04)

### Build System

- Relax transformers dependency for more compatible install across common tools
  ([`c82c173`](https://github.com/mbari-org/aidata/commit/c82c173bb0a5499b61a33262392bf3baf202c04b))

### Features

- Add saliency and area to localization.csv for convenience as it is useful for exploring training
  data
  ([`77a5973`](https://github.com/mbari-org/aidata/commit/77a5973960eaf63682d669d3d13342a358864000))


## v1.44.1 (2025-02-14)

### Performance Improvements

- Only check first 100 urls for speed-up during load
  ([`5292b6d`](https://github.com/mbari-org/aidata/commit/5292b6d703aed794613a9e7a39f29a9e72ae2dfd))


## v1.44.0 (2025-02-13)

### Features

- Tap planktivore png images as well as jpg
  ([`bc84180`](https://github.com/mbari-org/aidata/commit/bc84180957fced8f4d61c46b16a5eb902adccbe3))


## v1.43.0 (2025-02-07)

### Features

- Trigger release for --check-duplicates
  ([`f978d8f`](https://github.com/mbari-org/aidata/commit/f978d8f604bf2b10c65afa7e45b0165ff6bbbd96))


## v1.42.0 (2025-02-07)

### Build System

- Build recipe with added provenance and SBOM
  ([`8389b6e`](https://github.com/mbari-org/aidata/commit/8389b6e752abf6c884681a4b39c83cee5c595517))

- Conditional docker build only on release
  ([`a02c966`](https://github.com/mbari-org/aidata/commit/a02c966e5417d084a0ae05d8624b8986cf2b5367))

- Relaxed requirements for compatibility with mbari-aidata since these are often used together
  ([`334e8d5`](https://github.com/mbari-org/aidata/commit/334e8d54d95b97b7fb47d4fa8e2307036faebfc8))

- Switch to pip install in Docker build, fix build context, and uncomment docker build in
  release.yml
  ([`45aed2e`](https://github.com/mbari-org/aidata/commit/45aed2ef83a0bc966056527612d6d1efc30fad93))

### Documentation

- Added default project and more correct docker output in database_setup.md
  ([`6a9dd7f`](https://github.com/mbari-org/aidata/commit/6a9dd7ffa34aa4947d8a0a86691dd492fb635413))

- Better link to dev guide for docker
  ([`a6e9af9`](https://github.com/mbari-org/aidata/commit/a6e9af9fd3b8fa315a69acbf190d02faeceebca7))

- More details in README.md on features
  ([`afe88e0`](https://github.com/mbari-org/aidata/commit/afe88e0203fc1c8838f24e18c5a77c4fa46f0b0d))

### Features

- Trigger a release with the latest deps
  ([`24f8830`](https://github.com/mbari-org/aidata/commit/24f883044670c61816b39cfcabb83af9a67f5a30))


## v1.41.9 (2025-01-28)

### Bug Fixes

- Trigger release to pypi and update command munged during refactoring for poetry build
  ([`2764364`](https://github.com/mbari-org/aidata/commit/27643648e932ee897a01749211205c61b02f5b01))


## v1.41.8 (2025-01-28)

### Bug Fixes

- Trigger release to test pypi
  ([`7d26fac`](https://github.com/mbari-org/aidata/commit/7d26fac0fe502dfe14a20ff186e5c9dde28372c6))

### Build System

- Downgraded click and export requirements.txt to sync with poetry build for flexible dev
  ([`d6c1f94`](https://github.com/mbari-org/aidata/commit/d6c1f943f5556f21a08b233930df113c4b7cb869))

### Documentation

- Added config.yml example
  ([`2a1f9b8`](https://github.com/mbari-org/aidata/commit/2a1f9b8e073b82f48b68df5b7ef5bbb67da5cf6b))


## v1.41.7 (2025-01-28)

### Bug Fixes

- Bump pandas to 2.2.2 to fix broken pytest
  ([`32dc477`](https://github.com/mbari-org/aidata/commit/32dc477c37eb41fe0bd4981331caa6718697593a))

### Build System

- Added missing pandas requirement
  ([`2105643`](https://github.com/mbari-org/aidata/commit/2105643e7de1b7e752c6b78b108745afaa082467))

- Renamed package to mbari-aidata
  ([`218fe75`](https://github.com/mbari-org/aidata/commit/218fe75cdba615a10a2cceb2f9f91da5c665a85f))


## v1.41.6 (2025-01-28)

### Bug Fixes

- Removed unnecessary release step and minor changes to README.md to reflect correct package name
  ([`11f6558`](https://github.com/mbari-org/aidata/commit/11f6558e602d9aa60e4eb94ea1c45ada2378e415))


## v1.41.5 (2025-01-28)

### Bug Fixes

- Added missing upload to semantic release and poetry build command
  ([`e258cd3`](https://github.com/mbari-org/aidata/commit/e258cd3c21da265d8ddf453f53d60993c7afaaf5))


## v1.41.4 (2025-01-28)

### Bug Fixes

- Triggering release to test pypi
  ([`329bc28`](https://github.com/mbari-org/aidata/commit/329bc28336fccf5005728be2c4b082ab250a9534))

### Build System

- Clear names for dependency install and do release upload
  ([`fa2b024`](https://github.com/mbari-org/aidata/commit/fa2b02406d601a9a48f1c4d0a398fd58be096775))

- Replace pytest with poetry enabled
  ([`9c45a21`](https://github.com/mbari-org/aidata/commit/9c45a218ea2836e5d95ed0182d7b6e6ce35cc409))

- Switching to poetry build
  ([`419ca7d`](https://github.com/mbari-org/aidata/commit/419ca7de60aa519efa6e6b35b0be2e80f9d9e38b))


## v1.41.3 (2025-01-25)

### Bug Fixes

- Correct concurrent task array init
  ([`163eb25`](https://github.com/mbari-org/aidata/commit/163eb2502a880aef482cdc25ec88d5a817f21600))


## v1.41.2 (2025-01-24)

### Performance Improvements

- 2x speed-up in crop
  ([`6c8f1fd`](https://github.com/mbari-org/aidata/commit/6c8f1fd9ae21864368669f4565a7e490e2b55e84))


## v1.41.1 (2025-01-24)

### Bug Fixes

- Correct option named not-verified to unverified
  ([`e97c2e2`](https://github.com/mbari-org/aidata/commit/e97c2e2010b523f48800db13f3859d9915679345))


## v1.41.0 (2025-01-23)

### Features

- Added flag to download all unverified data, e.g. --unverified python aidata download dataset --voc
  --token <token> --config /tmp/uav/config.yml --base-path /mnt/ML_SCRATCH/uav --min-score 0.5
  --crop-roi --resize 224 --labels "all" --unverified
  ([`4dfa7da`](https://github.com/mbari-org/aidata/commit/4dfa7da7ea9fff5ed5b9015502a4f4c23d947b44))


## v1.40.1 (2025-01-22)

### Bug Fixes

- Handle missing score and cluster attributes when combining versions
  ([`604c911`](https://github.com/mbari-org/aidata/commit/604c9117c69db32eaf9a854d3ff5de8003beead3))


## v1.40.0 (2025-01-22)

### Features

- Download all versions by default and combine via NMS; this is potentially a breaking change for
  downstream that relies on the Baseline naming convention. Remove Baseline from the root directory
  name on datasets
  ([`7c8c1dd`](https://github.com/mbari-org/aidata/commit/7c8c1dddda32d5b1729a4bbafc49a20bdfacbcb7))


## v1.39.0 (2025-01-16)

### Features

- Add database id and box coordinates to the localizations.csv output
  ([`9d948db`](https://github.com/mbari-org/aidata/commit/9d948dbbd8f034c4f132ded8e6fc52a28851e8d5))


## v1.38.0 (2025-01-14)

### Features

- Handle missing secondary labels/scores during download
  ([`e1cec96`](https://github.com/mbari-org/aidata/commit/e1cec969cbe72d2cf0fcf956ac95530122ee1c05))


## v1.37.0 (2025-01-14)

### Documentation

- Added descriptions for just recipes
  ([`b187851`](https://github.com/mbari-org/aidata/commit/b187851c65b7d026ce6304c123b620737945479d))

### Features

- Added export of csv with media,cluster,label,score,label_s,score_s for downstream analysis
  ([`f2fe1fe`](https://github.com/mbari-org/aidata/commit/f2fe1feded48f16440b46bc29d10548df0a44ad9))


## v1.36.2 (2025-01-10)

### Bug Fixes

- Larger batch size for ffmpeg roi crop
  ([`c3325b8`](https://github.com/mbari-org/aidata/commit/c3325b8e50f20f560d8db7bc45575e311eeb203e))


## v1.36.1 (2025-01-10)

### Bug Fixes

- Correct depth query
  ([`85c125c`](https://github.com/mbari-org/aidata/commit/85c125c7791501dbec6923e39852b3d59d4c0d1b))

- Handle crops from images with whitespaces
  ([`57d1abf`](https://github.com/mbari-org/aidata/commit/57d1abf61f514b0c65a8d29e63d5f840f4273b50))


## v1.36.0 (2025-01-06)

### Bug Fixes

- Correct related attribute query
  ([`cef33e8`](https://github.com/mbari-org/aidata/commit/cef33e84ffe6af9125eef93a2938626f2393efa4))

### Documentation

- Minor reorg and update docker info
  ([`c3915e4`](https://github.com/mbari-org/aidata/commit/c3915e49a42cda895bbddb3e99e3a6ca56ccfd2b))

### Features

- Added support for minimum score in load boxes command and truncate exactly min boxes
  ([`3ed40b8`](https://github.com/mbari-org/aidata/commit/3ed40b83919e777c53e159fd4d509ef93e830011))


## v1.35.7 (2025-01-01)

### Bug Fixes

- Remove any unused media attributes
  ([`0dee5d6`](https://github.com/mbari-org/aidata/commit/0dee5d6fed9c910b0b459bee03a1b28b90e518a8))


## v1.35.6 (2024-12-31)

### Bug Fixes

- Add missing arg for ffmpeg image crop that was munged during refactor
  ([`7e9cb34`](https://github.com/mbari-org/aidata/commit/7e9cb3441b9ceae0e9ffcd466b6ace8259293e37))

- Rename plugins that load media; image_path should be media_path to support both image/video loads
  ([`1d547e8`](https://github.com/mbari-org/aidata/commit/1d547e8bbfee6f5b28daaf64919f94869c8c6972))


## v1.35.5 (2024-12-27)

### Performance Improvements

- 2x speed-up for ROI crop
  ([`6d405c7`](https://github.com/mbari-org/aidata/commit/6d405c70d390e3de3b77bd684a18b721f479835d))


## v1.35.4 (2024-12-21)

### Bug Fixes

- Correct query format for video name
  ([`d60ed95`](https://github.com/mbari-org/aidata/commit/d60ed95e5b2d40b61fd59765e87aca0c393dac5c))

- Handle white space in video path
  ([`723651a`](https://github.com/mbari-org/aidata/commit/723651a40133ba44e0943e35dc920aba548c1912))


## v1.35.3 (2024-12-21)


## v1.35.2 (2024-12-21)

### Bug Fixes

- Minor fix to assign mime first choice
  ([`593f339`](https://github.com/mbari-org/aidata/commit/593f33929b161d687d2e66d4498deefacc8007e7))

- Minor fix to report correct name when video already loaded
  ([`fbab8ee`](https://github.com/mbari-org/aidata/commit/fbab8ee8926197971b53bceb7fd41751caf32678))

- **cfe**: Index video correctly for cfe isiis
  ([`fae5709`](https://github.com/mbari-org/aidata/commit/fae5709567e5ce15032bd5d98cad238fbb44740f))


## v1.35.1 (2024-12-21)

### Bug Fixes

- Correct indexing for cfe media load
  ([`4a821af`](https://github.com/mbari-org/aidata/commit/4a821af3aeaff98ed6216aafffaad3afd648008e))

### Build System

- Add moviepy==2.1.1 to support video metadata extraction
  ([`e2382f8`](https://github.com/mbari-org/aidata/commit/e2382f84bfe5b8bbcaf606c8dc3e38c881ce3b17))

### Documentation

- Minor update in load help for clarity
  ([`0691b85`](https://github.com/mbari-org/aidata/commit/0691b85258a36cac51fde1746560bff64948b5ab))


## v1.35.0 (2024-12-20)

### Documentation

- Minor typo
  ([`0bef10a`](https://github.com/mbari-org/aidata/commit/0bef10a026cc374cd78020d1a6bc04fcc0e34f4f))

### Features

- Load CFE ISIIS video
  ([`15c236d`](https://github.com/mbari-org/aidata/commit/15c236d406101c88af7f86facd166bc92587cd05))


## v1.34.2 (2024-12-19)


## v1.34.1 (2024-12-19)

### Bug Fixes

- Merge conflict
  ([`b096402`](https://github.com/mbari-org/aidata/commit/b0964020e962cb37e618d219efc23a5296d138e5))

- Merge conflict
  ([`c11f77a`](https://github.com/mbari-org/aidata/commit/c11f77a006b2a1c22292338a290f42208163f03e))

### Performance Improvements

- Reduce delay for redis load and more robust handling of different label payload
  ([`4abd444`](https://github.com/mbari-org/aidata/commit/4abd44421f528919cfaf06b6efba37bdc9d106c0))


## v1.34.0 (2024-12-12)

### Features

- Handle 2015-03-07T20:53:01.065Z media timestamp and different cases of label in redis load
  ([`e46a739`](https://github.com/mbari-org/aidata/commit/e46a7391f67c5b62012a4193af66b5917b139d75))


## v1.33.0 (2024-12-06)

### Features

- Separate crops by label and output stats.json to compatible format as voc-cropper
  ([`0c95b7e`](https://github.com/mbari-org/aidata/commit/0c95b7ec61801870a0a75693ac91775177c9963e))


## v1.32.0 (2024-12-03)

### Features

- Added support to download ROIs in optimized formats for training from either video or images with
  python aidata download dataset --crop-roi --resize 224 etc.
  ([`a60c466`](https://github.com/mbari-org/aidata/commit/a60c4664dc52d4fb1a58d7f22a11aa063276679f))


## v1.31.1 (2024-11-21)

### Bug Fixes

- For coco/voc only download images and no video
  ([`2beb2e6`](https://github.com/mbari-org/aidata/commit/2beb2e6e0ed8e28b38e5a252283038d52b56f86f))


## v1.31.0 (2024-11-17)

### Features

- Remove any duplicate localizations on redis load
  ([`d6cd406`](https://github.com/mbari-org/aidata/commit/d6cd4066fc7e0fb947a6ba01a88e6adf5104f6ce))


## v1.30.3 (2024-11-08)

### Bug Fixes

- Correct handling of related attribute depth
  ([`190b3dc`](https://github.com/mbari-org/aidata/commit/190b3dcbe3604c4dd971757cdafe9c2502594d85))


## v1.30.2 (2024-10-29)

### Bug Fixes

- Correct handling of related media attributes, e.g. --depth 1000 or --section 1000m during download
  ([`ff12787`](https://github.com/mbari-org/aidata/commit/ff12787f5f77b35b6ac6f6dd8a63eeb29fe4333f))


## v1.30.1 (2024-10-28)

### Bug Fixes

- Correct handling of related media attributes, e.g. --depth 1000 or --section 1000m during download
  ([`27d0ace`](https://github.com/mbari-org/aidata/commit/27d0acec976ad58b7b2df3fa72485348ec486c00))


## v1.30.0 (2024-10-25)

### Features

- Exclude more than one label, e.g. --exclude Unknown --exclude Batray in load boxes
  ([`6f1fb51`](https://github.com/mbari-org/aidata/commit/6f1fb51a56322a4dbc7dc1ee6442d323989f05ce))


## v1.29.1 (2024-10-21)


## v1.29.0 (2024-10-21)

### Bug Fixes

- Merge conflicts
  ([`ece4b53`](https://github.com/mbari-org/aidata/commit/ece4b53c06e51808b29bc9e935b9fa3b29276f75))

### Features

- **cfe**: Support loading individual cfe images
  ([`d0fea5d`](https://github.com/mbari-org/aidata/commit/d0fea5dded33357ba8d89f1688ce5e806b5ed50b))


## v1.28.0 (2024-10-18)

### Features

- Support any named exemplar
  ([`f097d7a`](https://github.com/mbari-org/aidata/commit/f097d7aec7fef99a94f652185ade7fe693c71cb0))


## v1.27.0 (2024-10-16)

### Features

- Added --max-saliency option to download
  ([`592439f`](https://github.com/mbari-org/aidata/commit/592439f21e6e8d4353c8ee157962a3fcfb759035))


## v1.26.2 (2024-10-12)

### Bug Fixes

- Handle missing float/int attributes
  ([`8c68ef9`](https://github.com/mbari-org/aidata/commit/8c68ef9b73dc11adba57e7f5f80435941572a287))


## v1.26.1 (2024-10-09)

### Bug Fixes

- Correctly load single voc/sdcat file
  ([`4e10f4b`](https://github.com/mbari-org/aidata/commit/4e10f4babec0bf019384e8d6b63c2e963e38ffd9))


## v1.26.0 (2024-10-09)

### Documentation

- Minor update to command help to include voc
  ([`a61d50d`](https://github.com/mbari-org/aidata/commit/a61d50de8f35fa8b864e72dfe4d6d8797e035bb1))

- Minor update to command help to include voc
  ([`45177b8`](https://github.com/mbari-org/aidata/commit/45177b82f699c2085c4cab87fdc2ccc8d1fc6ebf))

### Features

- Added support for collapsing to a single class during download with --single-class
  ([`72b2aa1`](https://github.com/mbari-org/aidata/commit/72b2aa1c33ca630ba38b5b55c2e1d31b6b70f8ca))

### Performance Improvements

- Handle missing video frame rate/codec, more performant queue based loads and handle different
  timecode payloads
  ([`876036a`](https://github.com/mbari-org/aidata/commit/876036a2f3dba2f3818efa3f9d2d83d592f9127a))


## v1.25.0 (2024-10-08)

### Documentation

- Added update to README.md
  ([`7330522`](https://github.com/mbari-org/aidata/commit/7330522b640d0bf3f554253018992a8cf30c1dfd))

### Features

- Added support to load from voc
  ([`3b653ec`](https://github.com/mbari-org/aidata/commit/3b653ec84c4ddbb89786f4eec59ce876058d0455))


## v1.24.0 (2024-10-07)

### Documentation

- Minor typo fis
  ([`7a75bee`](https://github.com/mbari-org/aidata/commit/7a75beee47d8cfa564ac491c21da661e5b7664b6))

### Features

- Support exclusion of single label, e.g. Unknown with load boxes
  ([`3be99be`](https://github.com/mbari-org/aidata/commit/3be99be38c83c212cb98c843a4ff9563227f68ee))


## v1.23.2 (2024-10-04)

### Bug Fixes

- Support redis port/host/password
  ([`3a25060`](https://github.com/mbari-org/aidata/commit/3a250608c78c4a64f4f1a4f057e2c921ded0fa95))


## v1.23.1 (2024-10-01)

### Bug Fixes

- **uav**: Correct media date
  ([`76bf902`](https://github.com/mbari-org/aidata/commit/76bf9022df938971416a2478571407f1259d6815))


## v1.23.0 (2024-09-29)

### Features

- Add support for --min-score in download dataset
  ([`915aa1f`](https://github.com/mbari-org/aidata/commit/915aa1fac9a5c309fc3e1a5b9ff8060f6d26c949))


## v1.22.0 (2024-09-22)

### Bug Fixes

- Albumentations dependency break
  ([`b483324`](https://github.com/mbari-org/aidata/commit/b48332418c278b8b4e40987b376cdbb70be0c8ed))

### Features

- Add support for --min-saliency in download dataset
  ([`014f5af`](https://github.com/mbari-org/aidata/commit/014f5af460ff5e70bac69452a6f9012425519016))


## v1.21.1 (2024-09-20)

### Performance Improvements

- Slimmer memory footprint for downloads. working for 360k download and export for CFE ROIs
  ([`4f035ac`](https://github.com/mbari-org/aidata/commit/4f035ac5d915e852f97523f6ef2b393bd69a9a99))


## v1.21.0 (2024-09-19)

### Features

- Added support for --section in download
  ([`a89e695`](https://github.com/mbari-org/aidata/commit/a89e69503e8fc4d20bda05f823ea9c1bcc6b180a))


## v1.20.0 (2024-09-19)

### Documentation

- Add missing images
  ([`4a2171e`](https://github.com/mbari-org/aidata/commit/4a2171e5a988885d06bc2888216f1c235bf07bf0))

- Correct link to docs
  ([`2c7a544`](https://github.com/mbari-org/aidata/commit/2c7a544390188374cae509ea1388be91b37a02ce))

- Just some refactoring of setup docs
  ([`6531f40`](https://github.com/mbari-org/aidata/commit/6531f40270117ce01440a41a3c5a6e356d72a2fd))

### Features

- Transformresize ([#18](https://github.com/mbari-org/aidata/pull/18),
  [`ce33725`](https://github.com/mbari-org/aidata/commit/ce337254fd3fa243d5c5d85b7e5607ac1f90327c))

Adds the option --resize to the transform to transform with a resize. Useful for training models
  with scales of the same image. For tiny boxes that may result in downsizing, the option --min-dim
  supports removal at them; this defaults to 10 pixels in any dimension


## v1.19.0 (2024-09-16)

### Features

- Add Planktivore media support ([#17](https://github.com/mbari-org/aidata/pull/17),
  [`5be41a9`](https://github.com/mbari-org/aidata/commit/5be41a90686016a9b783b7200e53d38367fe515b))

* feat: added test and config for loading planktivore

* docs: more detail on test/dev setup and added in redis to test

* test: correct tests conf that aligns to doc

* docs: correct link to database

* chore: added in more just recipes for testing


## v1.18.0 (2024-09-05)

### Features

- Add support to different models
  ([`13fb78e`](https://github.com/mbari-org/aidata/commit/13fb78e2a524a730a9334dded16cde8bb0c9fc98))


## v1.17.1 (2024-09-04)

### Performance Improvements

- Bump to better indexing
  ([`5405abe`](https://github.com/mbari-org/aidata/commit/5405abea10e5915a055235cb0037187d523236cc))


## v1.17.0 (2024-09-03)

### Features

- Replace underscore with colon in redis hash store of exemplars
  ([`d7a07bc`](https://github.com/mbari-org/aidata/commit/d7a07bc647e12521ebf95298ab786fbc31caebf2))


## v1.16.0 (2024-09-01)

### Features

- Added redis document id fetch
  ([`3ab3b72`](https://github.com/mbari-org/aidata/commit/3ab3b728df78489a68835135bf3d617fb9cb7442))


## v1.15.0 (2024-09-01)

### Features

- Replace index id with database id for exemplars
  ([`64f6dde`](https://github.com/mbari-org/aidata/commit/64f6dde52d45fd9f4f0344137b2d3a9db53f8fc2))


## v1.14.0 (2024-08-30)

### Features

- Disable flagging exexmplars
  ([`fa74c55`](https://github.com/mbari-org/aidata/commit/fa74c55c28424b97df58c041579c19f6d236dd85))


## v1.13.0 (2024-08-29)

### Documentation

- Updated docs and and config with better test setup
  ([`f45e94f`](https://github.com/mbari-org/aidata/commit/f45e94f4098cc8fab0e418c06f4776d807ce8fdd))

- Updated docs and and config with better test setup
  ([`7210a84`](https://github.com/mbari-org/aidata/commit/7210a84652f0fbcbb5136c8d0f711a06627ef5e1))

### Features

- Added support for depth parsing
  ([`9449cde`](https://github.com/mbari-org/aidata/commit/9449cdec7f47c0b2d2b70e1720b906af9bf9031e))


## v1.12.2 (2024-08-26)

### Bug Fixes

- Handle empty query operators
  ([`b957f7a`](https://github.com/mbari-org/aidata/commit/b957f7a557f992a23ca23bf4bedc2c3a8738cab0))


## v1.12.1 (2024-08-22)

### Bug Fixes

- Trigger release to update __init__.py
  ([`d278ce3`](https://github.com/mbari-org/aidata/commit/d278ce34374ca00d07df860db6412e4985343ee5))

### Documentation

- Minor correction to reflect correct path to docs
  ([`13c24b5`](https://github.com/mbari-org/aidata/commit/13c24b5999d94468abf5a1a2a70739d1fd1e37d7))


## v1.12.0 (2024-08-16)

### Bug Fixes

- Correct handling of label map
  ([`7827810`](https://github.com/mbari-org/aidata/commit/7827810261a053e2307c46174f48c000cc31f26c))

- Handle conversion errors outside of normalized 0-1 coordinates
  ([`e410cd4`](https://github.com/mbari-org/aidata/commit/e410cd40fef67dcf6f03e83fec6e44deb0f7eb48))

### Build System

- Added missing albumentations library
  ([`623df2f`](https://github.com/mbari-org/aidata/commit/623df2fa325e80aae6f18a68c755f8197848e1f0))

### Documentation

- Added detail on .env file
  ([`66b83a0`](https://github.com/mbari-org/aidata/commit/66b83a017b74526c1ab9ecd52e3237637433bb39))

- Correct link to internal docs
  ([`c0e4f87`](https://github.com/mbari-org/aidata/commit/c0e4f87e549de5af1c1071844051eba69619934c))

- Moved CHANGELOG
  ([`f3df55c`](https://github.com/mbari-org/aidata/commit/f3df55c250b1bbaf58508c40151b718b661dae93))

- Removed docs which are now in another repo and added commands for ref in README.md
  ([`bdd122a`](https://github.com/mbari-org/aidata/commit/bdd122ab997e2e718c8de10378998ee0a01aa65d))

- Resolve conflict
  ([`783fa25`](https://github.com/mbari-org/aidata/commit/783fa250d5175e9f5cf7e7cf6d611b33d2d3c8a5))

- Updated with correct link to docs
  ([`1577fa3`](https://github.com/mbari-org/aidata/commit/1577fa39ee414fc94ca2757a26cf0fee30eae683))

### Features

- Addded voc_to_yolo
  ([`cb4e798`](https://github.com/mbari-org/aidata/commit/cb4e7987e43fa8939f09a3950351925c95cec2e7))

- Added transform for voc only
  ([`ade3713`](https://github.com/mbari-org/aidata/commit/ade3713302c8c6a0045166c99594d268c5cf7c21))

- Added transform for voc only
  ([`9147c28`](https://github.com/mbari-org/aidata/commit/9147c280fcaa3f421080a07884b6a7caa87af32e))


## v1.11.0 (2024-08-08)

### Features

- Added label counts to /labels/{project_name}
  ([`d6e5cce`](https://github.com/mbari-org/aidata/commit/d6e5cce4d9af0d7062b3a67fa3d25590df7fb829))


## v1.10.0 (2024-08-05)

### Documentation

- Added project image
  ([`6798ca7`](https://github.com/mbari-org/aidata/commit/6798ca79ba062d6648f3ec5bd18bf857201cc6cd))

- Fixed links and added clickable link to mantis
  ([`eef0f32`](https://github.com/mbari-org/aidata/commit/eef0f32889a4da6241fe7fec8a42c190531544b4))

### Features

- Added verified --verified to download
  ([`bb2b274`](https://github.com/mbari-org/aidata/commit/bb2b2749d4d71c29176e69e9b24dc0b5be7e4f48))


## v1.9.0 (2024-08-05)

### Features

- Added database reset and cleane up docs
  ([`572bdd5`](https://github.com/mbari-org/aidata/commit/572bdd512d990774255786eb6bbd7579ba6e8c71))


## v1.8.0 (2024-07-26)

### Features

- Add load to exemplar bool which is helpful for visualization
  ([`5d1feb2`](https://github.com/mbari-org/aidata/commit/5d1feb2136decf00276777dd5c4945858564c33e))


## v1.7.4 (2024-07-26)

### Bug Fixes

- Correct default for max-images to load all
  ([`9f284ab`](https://github.com/mbari-org/aidata/commit/9f284ab9c25db245c7a74b018784c2d5fa242c06))


## v1.7.3 (2024-07-24)

### Bug Fixes

- Correct parsing of class names and cuda device enable
  ([`58b0dea`](https://github.com/mbari-org/aidata/commit/58b0deaf0964970b2aef4878172c589b633ecc84))


## v1.7.2 (2024-07-23)

### Bug Fixes

- Correct handling of exemplars
  ([`accbb9e`](https://github.com/mbari-org/aidata/commit/accbb9e1df0ac0959826144b49bd765d02a0e84e))

### Build System

- Correct docker build path
  ([`4406a96`](https://github.com/mbari-org/aidata/commit/4406a96c0021c32dff74b0d5abd8741d9fec0cd9))

- Exclude py12 which is problematic with transformers library
  ([`2116ad3`](https://github.com/mbari-org/aidata/commit/2116ad3a9b17d40671b65427db70c0a830349a8a))

- Remove legacy "ENV key value" in Dockerfile.cuda
  ([`84fa73c`](https://github.com/mbari-org/aidata/commit/84fa73cb0fa375cf26abe6efbaf38cb095960f75))


## v1.7.1 (2024-07-23)

### Bug Fixes

- Correct handling of version arg
  ([`8eb99b5`](https://github.com/mbari-org/aidata/commit/8eb99b5ff77c8b04739f397b641c31c05861aad1))


## v1.7.0 (2024-07-23)

### Features

- Added password pass through to redis
  ([`900bbef`](https://github.com/mbari-org/aidata/commit/900bbefc4f509d1c2ba763aa8e4041bc53b4bf1d))


## v1.6.4 (2024-07-23)

### Performance Improvements

- Move model to gpu and some minor refactoring for clarity
  ([`a9d2f59`](https://github.com/mbari-org/aidata/commit/a9d2f59c16b09e19c3c526b94b08877a8ee958cc))


## v1.6.3 (2024-07-22)

### Bug Fixes

- Minor fix in exemplar args and more logging
  ([`f34e643`](https://github.com/mbari-org/aidata/commit/f34e6439bd7ff387eeba2c07334e0fe7338cb742))


## v1.6.2 (2024-07-19)

### Bug Fixes

- Handled empty labels, bad media, and more reporting of progress
  ([`e31b691`](https://github.com/mbari-org/aidata/commit/e31b69130e58c44aff7302244fc26be25f332f3d))


## v1.6.1 (2024-07-18)

### Bug Fixes

- Bugs from typecheck
  ([`222d641`](https://github.com/mbari-org/aidata/commit/222d64150968458890fb8cd5db37952816ef00dc))

### Build System

- Removed unused imports and bump torch to python3.11 compatible and
  ([`c9afcbb`](https://github.com/mbari-org/aidata/commit/c9afcbb8b9c5ce69e1cdcb993823c3388b392282))


## v1.6.0 (2024-07-05)

### Bug Fixes

- Remove whitespace and move exemplar to load
  ([`a7d8607`](https://github.com/mbari-org/aidata/commit/a7d860775b45ef6c47f4eda924f22424b7c75690))

### Features

- Added sdcat exemplar load
  ([`46ea57e`](https://github.com/mbari-org/aidata/commit/46ea57e07c0e355d251e6bad8c04ac1be7d4eaf2))


## v1.5.0 (2024-06-25)

### Documentation

- Improved doc on save
  ([`7c37c42`](https://github.com/mbari-org/aidata/commit/7c37c42858dc493ae1bcfa3c33c98fcd8d96f651))

### Features

- Pass through the id to the voc output
  ([`e28a211`](https://github.com/mbari-org/aidata/commit/e28a2119f16e1de82bacac345fc960572b69d5f9))


## v1.4.7 (2024-06-24)

### Bug Fixes

- Handle fewer records correctly
  ([`a3528de`](https://github.com/mbari-org/aidata/commit/a3528debf63483a964e82e1d9ceb9997af2aae3e))


## v1.4.6 (2024-05-22)


## v1.4.5 (2024-05-22)

### Bug Fixes

- Correct load_bulk_boxes args and attribute mapping for redis load
  ([`09241be`](https://github.com/mbari-org/aidata/commit/09241be561212b417b6c0377aeb317356a7e192f))

- Revert to original pass through of datetime object
  ([`5af3119`](https://github.com/mbari-org/aidata/commit/5af31192f8c5eb46d94c132689d833c1f81c4451))

### Performance Improvements

- Handle variable case attribues
  ([`2538007`](https://github.com/mbari-org/aidata/commit/253800716601da75163cca127ea79f05baf9374f))

- Remove audio and reduce frame rate to 24 for .git
  ([`604a463`](https://github.com/mbari-org/aidata/commit/604a4632ea83c749b3dbcb2410bb870895fa9006))

- Remove palette gen for speed-up of video gif creation
  ([`5ce9a12`](https://github.com/mbari-org/aidata/commit/5ce9a129324b049459779167211d613bc4a278c1))


## v1.4.4 (2024-05-21)

### Performance Improvements

- Speed-up 64x speed
  ([`f0cd15c`](https://github.com/mbari-org/aidata/commit/f0cd15c979dc1e68fd5f3b94a7b120d98e101fe0))


## v1.4.3 (2024-05-21)

### Bug Fixes

- Correct key for datetime attribute format
  ([`f1bcad7`](https://github.com/mbari-org/aidata/commit/f1bcad72dd71a432b87de37594fa3a100ac316c9))

### Documentation

- Added in load/download docs and adding in CHANGELOG.md
  ([`f3ac92c`](https://github.com/mbari-org/aidata/commit/f3ac92c908d3da698853f27e3485f5ad91dfa3bf))


## v1.4.2 (2024-05-16)

### Bug Fixes

- Correct import path
  ([`0206f3d`](https://github.com/mbari-org/aidata/commit/0206f3d7f128c9fbda9a5b9fb6ba6888aacac8eb))


## v1.4.1 (2024-05-16)

### Bug Fixes

- Add missing files
  ([`b95710a`](https://github.com/mbari-org/aidata/commit/b95710a579b1ca2afc2239fe7d4917b589fd9b99))


## v1.4.0 (2024-05-10)

### Documentation

- Minor fix to checkout and more explicit naming of path
  ([`7be3aa3`](https://github.com/mbari-org/aidata/commit/7be3aa3292665ff7142835a13261b0398721b1f1))

- Minor update to add token to examples
  ([`7c499a5`](https://github.com/mbari-org/aidata/commit/7c499a58e77d7d0c9935533e8d6c4bc1b527e639))

### Features

- Some refactoring but mostly addition of support for versioning
  ([`cfe9ba1`](https://github.com/mbari-org/aidata/commit/cfe9ba13df6a764d26e905dc79679563f90e3fab))


## v1.3.0 (2024-05-02)

### Bug Fixes

- Adjustments to match Fernandas generated test images
  ([`1ef27b7`](https://github.com/mbari-org/aidata/commit/1ef27b777a218f7f21971ccd8e0038d7e1bb081c))

### Features

- Added support to pass in max-images which is useful with --dry-run
  ([`fe8d2de`](https://github.com/mbari-org/aidata/commit/fe8d2de7d731fb0b93b6a8bc8894347b60cabab2))


## v1.2.3 (2024-05-01)

### Bug Fixes

- Remove return to load all
  ([`460b449`](https://github.com/mbari-org/aidata/commit/460b449edac9719a3fcf6629c3c6bbfe20e065d7))


## v1.2.2 (2024-04-29)

### Bug Fixes

- Skip over images with no metadata and minor logging fix
  ([`c926ca8`](https://github.com/mbari-org/aidata/commit/c926ca8f238fc721ae0a1d872ea46d5b83b63299))


## v1.2.1 (2024-04-29)

### Bug Fixes

- Correct path for loading SONY images
  ([`42048fb`](https://github.com/mbari-org/aidata/commit/42048fb8b755edeaaa3fcca048565bfc1f690755))

- Return dataframe and process in sorted order for convenience
  ([`52025fb`](https://github.com/mbari-org/aidata/commit/52025fb44b608c9cdf5db4b0bd11de24e21a69e6))

### Build System

- Added missing dependency
  ([`3f1a267`](https://github.com/mbari-org/aidata/commit/3f1a2678ddd4dcf898ca0ef53be3d9b223a4140a))

### Documentation

- Added hint for dry-run and hostname
  ([`f314d4e`](https://github.com/mbari-org/aidata/commit/f314d4e044f8b8f8808d9b542c7f3ca5f48448db))


## v1.2.0 (2024-04-29)

### Bug Fixes

- Minor type
  ([`f70d7bd`](https://github.com/mbari-org/aidata/commit/f70d7bd437551d1020d0e2e54c699b7b6032adfd))

### Features

- Support both png and jpg SONY images
  ([`75adcca`](https://github.com/mbari-org/aidata/commit/75adcca387411bfd8be4a2de25a9d2e574699a7a))

- Support both png and jpg uppercase SONY images
  ([`343651b`](https://github.com/mbari-org/aidata/commit/343651b00db40a8ae23c0307bba1b055a1f4aff4))


## v1.1.0 (2024-04-29)

### Features

- Added support for extracing sony mdata for UAV
  ([`6cd2faa`](https://github.com/mbari-org/aidata/commit/6cd2faaf23c604d574b434cc69496ff1210af3c7))


## v1.0.3 (2024-03-26)

### Bug Fixes

- Correct path to data in test database
  ([`fa9f7dc`](https://github.com/mbari-org/aidata/commit/fa9f7dc11321d80987c2028abf2c7a0bf7d13f5c))


## v1.0.2 (2024-03-26)

### Bug Fixes

- Correct formatting for the cluster string
  ([`41678b3`](https://github.com/mbari-org/aidata/commit/41678b3637892dcb1701dd683e9c8f52d96faf1b))


## v1.0.1 (2024-03-25)

### Bug Fixes

- Fix bug that downloads everything
  ([`685c72a`](https://github.com/mbari-org/aidata/commit/685c72a3ab527f9a665d69542d9c79b5e8e7bc41))

### Documentation

- Added missing doc images
  ([`6282c57`](https://github.com/mbari-org/aidata/commit/6282c57d2fb0224ceaa8b03fb4ef86b29f5e5bfd))

- Consistent example
  ([`e599e5c`](https://github.com/mbari-org/aidata/commit/e599e5ca7bb1506d5c0f22562fedb100b8e03016))


## v1.0.0 (2024-03-16)

### Features

- Initial commit
  ([`9ce6cc4`](https://github.com/mbari-org/aidata/commit/9ce6cc4825d5d691ef75ac3ba38800c60010494b))
