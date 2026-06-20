# CHANGELOG

<!-- version list -->

## v1.76.1 (2026-06-20)

### Bug Fixes

- **ci**: Add --changelog flag to semantic-release and migrate deprecated changelog_file config
  ([`a7bbb0f`](https://github.com/mbari-org/aidata/commit/a7bbb0ff07138bca2a0278a0c862903549c6f57a))


## v1.76.0 (2026-06-20)

### Features

- Dynamically include all localization attributes in localizations.csv (#66)
  ([#66](https://github.com/mbari-org/aidata/pull/66),
  [`2909453`](https://github.com/mbari-org/aidata/commit/2909453e8bb0f2420194624e9aa8ba353d8c6840))


## v1.75.0 (2026-06-19)

### Features

- Add configurable train/val/test fractions to `transform split` (#61)
  ([#61](https://github.com/mbari-org/aidata/pull/61),
  [`91422fb`](https://github.com/mbari-org/aidata/commit/91422fb6b90c6b51e106645c57b8bf6da5f4a575))


## v1.74.0 (2026-06-16)

### Features

- Triggering release with update last updated date in README.md
  ([`daa8cbd`](https://github.com/mbari-org/aidata/commit/daa8cbdb188584769d3338b2827cf23e2ff367d7))


## v1.73.2 (2026-06-15)

### Bug Fixes

- Docker build failure due to missing gcc and deprecated CI actions (#57)
  ([#57](https://github.com/mbari-org/aidata/pull/57),
  [`dee3593`](https://github.com/mbari-org/aidata/commit/dee35934eced5caa1147ee7b35eca60d66ebf244))


## v1.73.1 (2026-06-13)

### Build System

- **deps**: Bump the pip group across 1 directory with 5 updates (#50)
  ([#50](https://github.com/mbari-org/aidata/pull/50),
  [`068127c`](https://github.com/mbari-org/aidata/commit/068127c48d19aeda829ddfde94aa3484dea07a6f))

### Performance Improvements

- Batch ROI crops by frame to reduce ffmpeg process overhead (#56)
  ([#56](https://github.com/mbari-org/aidata/pull/56),
  [`935dd71`](https://github.com/mbari-org/aidata/commit/935dd71f926fb9a019b818e9ebf636295af5d668))


## v1.73.0 (2026-06-01)

### Features

- Add --fill option for black/white ROI crop padding (#53)
  ([#53](https://github.com/mbari-org/aidata/pull/53),
  [`74eaf87`](https://github.com/mbari-org/aidata/commit/74eaf8700be780272885d110fee9ecf1bbf0f1ba))


## v1.72.0 (2026-05-06)

### Features

- Crop ROIs from external videos (#51) ([#51](https://github.com/mbari-org/aidata/pull/51),
  [`d647ae1`](https://github.com/mbari-org/aidata/commit/d647ae19fc0817e0b5fa5dffb75a5a1b83039193))


## v1.71.3 (2026-03-27)

### Performance Improvements

- Free GPU memory between caches to improve batching speed
  ([`de2907c`](https://github.com/mbari-org/aidata/commit/de2907cd677e980a2b92fc41071d2d21a104829d))


## v1.71.2 (2026-03-10)

### Bug Fixes

- Get_media_ids should map the name to the id instead of elemental_id to the id for box loads
  ([`95e5fa4`](https://github.com/mbari-org/aidata/commit/95e5fa43e86b7f43cf17b8af76391ce73065357e))

- Minor type in column check for box
  ([`8252aa5`](https://github.com/mbari-org/aidata/commit/8252aa58a7ec066d324723fc82057896bb6f8c1b))


## v1.71.1 (2026-02-16)

### Bug Fixes

- Remove additional id parsing from filename for vector load; assume filename stem is the unique
  identifier
  ([`e49ea5f`](https://github.com/mbari-org/aidata/commit/e49ea5f4fa47952026808d012838374187faa328))


## v1.71.0 (2026-02-09)

### Bug Fixes

- Handle media with missing width and height during download
  ([`ff5d756`](https://github.com/mbari-org/aidata/commit/ff5d7569cc8adc139684aa3cc7ed9ec6137c80b3))

- **vars**: Assume all uuid images are png not jpg
  ([`72d2eb1`](https://github.com/mbari-org/aidata/commit/72d2eb122f4064e387448eb006e6608fa4bba960))

### Features

- Skip duplicates during media load, but do not exit if there are duplicates - continue to load
  non-duplicatest.
  ([`cc7a348`](https://github.com/mbari-org/aidata/commit/cc7a34881a20a674acfa17d0abca8d625136c448))


## v1.70.1 (2026-02-05)

### Bug Fixes

- Handle empty timestamps
  ([`00087c9`](https://github.com/mbari-org/aidata/commit/00087c937a8f447d7e870481bd4e25e75c863f25))


## v1.70.0 (2026-02-05)

### Documentation

- Minor README update
  ([`7fb373f`](https://github.com/mbari-org/aidata/commit/7fb373fa90d76996eb30c2fd8451166306637a46))

### Features

- Add support for importing VARS generated media from m3-download (#48)
  ([#48](https://github.com/mbari-org/aidata/pull/48),
  [`962408e`](https://github.com/mbari-org/aidata/commit/962408e762f5279552b84e1efd5ec14dda0f29d8))


## v1.69.0 (2026-01-03)

### Features

- Trigger release
  ([`185809d`](https://github.com/mbari-org/aidata/commit/185809dcd2c509d2e6ba90fb3d92a519e1771477))


## v1.68.0 (2026-01-01)

### Features

- Parse EXIF data from SONY url hosted images efficiently
  ([`548ce50`](https://github.com/mbari-org/aidata/commit/548ce50c9889396057de3ce962c5015a53d4115f))


## v1.67.0 (2026-01-01)

### Features

- Detect URLs and bypass local file system existence and path relativity checks when the input is a
  URL.
  ([`fe2709e`](https://github.com/mbari-org/aidata/commit/fe2709ee1b97eb858b6f79e609e2bcd6c5dedbc5))


## v1.66.0 (2025-12-26)

### Features

- Write frame number to localizations.csv
  ([`192c4a4`](https://github.com/mbari-org/aidata/commit/192c4a43d0577e15e6b74754e010563a63642f9a))


## v1.65.0 (2025-12-19)

### Features

- Add predicted_label to localizations.csv
  ([`f737740`](https://github.com/mbari-org/aidata/commit/f737740a06b0d75990c7e948cee2fba377d87404))


## v1.64.0 (2025-12-18)

### Features

- Export uuid and verified to localizations.csv to simplify downstream processing
  ([`c9c4cc4`](https://github.com/mbari-org/aidata/commit/c9c4cc475c680947cdcb6bfd8a1507ff43ea8469))


## v1.63.4 (2025-12-14)

### Bug Fixes

- Correct transformed image name in voc xml
  ([`6363171`](https://github.com/mbari-org/aidata/commit/636317154a8738368594aa97bbbaab64bdb85542))


## v1.63.3 (2025-12-14)

### Bug Fixes

- Correct xml_path name for download
  ([`1097669`](https://github.com/mbari-org/aidata/commit/1097669f5e397c00545c53b4212bb6e04e453026))


## v1.63.2 (2025-12-14)

### Performance Improvements

- Override score for improved NMS of combined versions and better naming convention for voc
  generated .xml files
  ([`8219bdd`](https://github.com/mbari-org/aidata/commit/8219bdd3b337b4573dbed2dff784831c584b3d73))


## v1.63.1 (2025-12-03)

### Performance Improvements

- Bump half-life to 15 frames
  ([`dcaa734`](https://github.com/mbari-org/aidata/commit/dcaa73482e83ba8e5f206de39526beacb1956fdd))


## v1.63.0 (2025-12-03)

### Features

- Add more tracking attributes for label assist
  ([`9df3893`](https://github.com/mbari-org/aidata/commit/9df3893cadbf99f9b9152020790fff04c39dfdd4))


## v1.62.3 (2025-12-02)

### Bug Fixes

- Removed bounded track load
  ([`c08801d`](https://github.com/mbari-org/aidata/commit/c08801d5dfd5a6225cb6494704d80e7b289789ec))


## v1.62.2 (2025-12-01)

### Bug Fixes

- Handle negative box values and some minor refactoring to simplify clamping
  ([`2cc852e`](https://github.com/mbari-org/aidata/commit/2cc852e2b49f536fb3fd4da641e25f9f0208afb3))


## v1.62.1 (2025-11-27)

### Performance Improvements

- Add short delay during video upload for slower clients
  ([`9c2028d`](https://github.com/mbari-org/aidata/commit/9c2028d0fc1bbc2623801c06a580e92632bdd6c8))


## v1.62.0 (2025-11-27)

### Features

- Add time decay weighted average prediction load
  ([`8449250`](https://github.com/mbari-org/aidata/commit/8449250a366ea288addb54dfc1e564c01dca1844))


## v1.61.1 (2025-11-25)

### Performance Improvements

- Return at 100% load
  ([`fb1de89`](https://github.com/mbari-org/aidata/commit/fb1de8981602989d542152b589bfe24aea9fa46b))


## v1.61.0 (2025-11-24)

### Build System

- Revised torch install in poetry and removed unused files
  ([`5d10bbe`](https://github.com/mbari-org/aidata/commit/5d10bbeb9637ab7345272a8456ac17ac74ac1ac9))

### Documentation

- Revise mbari-aidata tool description in README
  ([`1fd7747`](https://github.com/mbari-org/aidata/commit/1fd7747695ec015ce1852dcb071cb5d1ed88e021))

### Features

- Triggering release for latest build
  ([`cd375ef`](https://github.com/mbari-org/aidata/commit/cd375efc689344bc2e9f1d412fa67ad44ffcaae8))


## v1.60.6 (2025-11-11)

### Performance Improvements

- Upload video without waiting for transcode and better handling of parsing depth from i2MAP with
  regexp
  ([`5643d92`](https://github.com/mbari-org/aidata/commit/5643d924d9a3da7f3d874761cdfea4ab87b009e7))


## v1.60.5 (2025-10-26)

### Performance Improvements

- Remove redundant NMS code
  ([`d5d83ba`](https://github.com/mbari-org/aidata/commit/d5d83baeffa0d531919ecbf1620a494ddcb42c53))


## v1.60.4 (2025-10-25)

### Bug Fixes

- Correct coco and voc NMS combination for multiple versions
  ([`94300ac`](https://github.com/mbari-org/aidata/commit/94300acf18ae14f8712e5100fc03eb798da241e9))

### Documentation

- Minor update to README.md formatting
  ([`08ce283`](https://github.com/mbari-org/aidata/commit/08ce2833fbeff31dd01015f4c34dae58327dcb8f))


## v1.60.3 (2025-10-23)

### Bug Fixes

- Correct output_file for crop based on either elemental_id or id if elemental_id missing.
  ([`a45ca26`](https://github.com/mbari-org/aidata/commit/a45ca26361406634795b9adae70c1ba1f00d25cf))


## v1.60.2 (2025-10-22)

### Bug Fixes

- Correct crop_id for labels
  ([`70320f4`](https://github.com/mbari-org/aidata/commit/70320f47bb0ccc664c377c6b663631b1cfacd4b3))


## v1.60.1 (2025-10-16)

### Bug Fixes

- Change media mapping from name to elemental_id (#32)
  ([#32](https://github.com/mbari-org/aidata/pull/32),
  [`5fea02b`](https://github.com/mbari-org/aidata/commit/5fea02b8440e5226ad4b474cd94c4dd90f8fc005))

### Documentation

- Added detail on NMS
  ([`52be3cd`](https://github.com/mbari-org/aidata/commit/52be3cd478e31b7b982746f5f8b85053db599eb9))


## v1.60.0 (2025-10-03)

### Features

- Add split command to transform CLI group for dataset splitting (#30) (#31)
  ([#31](https://github.com/mbari-org/aidata/pull/31),
  [`ee3bfb3`](https://github.com/mbari-org/aidata/commit/ee3bfb3f5655bc40223f163654fdaec555722d7c))


## v1.59.0 (2025-09-25)

### Documentation

- Removed redundant link to docs
  ([`ef2b211`](https://github.com/mbari-org/aidata/commit/ef2b21161c812f2c94b9779c791f44fe1ff44f2d))

### Features

- Triggering release to include ssl verify
  ([`7fcfc6d`](https://github.com/mbari-org/aidata/commit/7fcfc6d030f1424cfae30f34aea6850cfad64132))


## v1.58.1 (2025-09-12)

### Bug Fixes

- Correct handling of .txt based media load
  ([`77b9b4c`](https://github.com/mbari-org/aidata/commit/77b9b4ca10889988e3c7257b9ead321120af0af2))


## v1.58.0 (2025-08-25)

### Features

- Add support for media text load (#25) ([#25](https://github.com/mbari-org/aidata/pull/25),
  [`925eb53`](https://github.com/mbari-org/aidata/commit/925eb53c17dbd6185195fffa1df10d1faadc9e41))


## v1.57.0 (2025-08-19)

### Features

- More friendly format for download directory when combining multiple versions; versionA_versionB,
  instead of versionA,versionB
  ([`3602dc1`](https://github.com/mbari-org/aidata/commit/3602dc11a7d6414d013d45b72d8073e3cd2ff039))


## v1.56.1 (2025-08-10)

### Bug Fixes

- Stricter duplication to allow for roi load
  ([`ba5144c`](https://github.com/mbari-org/aidata/commit/ba5144ce2040ea1cce495d113ca1a05046c20d00))


## v1.56.0 (2025-08-10)

### Build System

- Update poetry; pin tqdm
  ([`ac059a5`](https://github.com/mbari-org/aidata/commit/ac059a5cbbddfad4d4326006694ba24c9955ce45))

### Features

- Support extracting datetime from low_mag_cam-1713221040057971.. and high_mag_cam-1713221004871098
  from planktivore files
  ([`f898f0c`](https://github.com/mbari-org/aidata/commit/f898f0c3955f6146e6421044182e12428b55d4b5))


## v1.55.4 (2025-07-22)

### Build System

- Correct GITHUB_TOKEN
  ([`8810f52`](https://github.com/mbari-org/aidata/commit/8810f5241b5ea42c4f6618d688429e773c2e468b))

### Performance Improvements

- Better choice to model load
  ([`8949736`](https://github.com/mbari-org/aidata/commit/8949736d3016937bd67176407f136dc0ba37d1e1))


## v1.55.3 (2025-07-08)

### Bug Fixes

- Check image path lengths for exemplar load and remove some unused code
  ([`8ffccf1`](https://github.com/mbari-org/aidata/commit/8ffccf1b3762158149382407f7b6508155df2eca))

### Documentation

- Minor format correction and update on media access features
  ([`117a263`](https://github.com/mbari-org/aidata/commit/117a26377e99187b794f5c34dfb66c2b05c10143))


## v1.55.2 (2025-06-05)

### Bug Fixes

- Correct datetime iso_start_datetime for video load and renaming attribute iso_datetime to
  iso_start_datetime for consistency across all video record loads
  ([`fc38a32`](https://github.com/mbari-org/aidata/commit/fc38a3274287d0220d007af6ffd53611735e28c1))


## v1.55.1 (2025-06-03)

### Bug Fixes

- Correct column assignment for roi cluster load and handle reserved name class
  ([`2570007`](https://github.com/mbari-org/aidata/commit/25700075084de990c1c147a828eb73f261aef94e))

### Build System

- Disable cuda build and push latest tag
  ([`d9cc2f2`](https://github.com/mbari-org/aidata/commit/d9cc2f2169ea372b9deada2174e6c554c565af77))


## v1.55.0 (2025-06-02)

### Build System

- Add --no-cache to slim docker build footprint
  ([`2eba83c`](https://github.com/mbari-org/aidata/commit/2eba83ce229ca15de2c9fd230aa0deea06a8e0e1))

### Features

- Support update or create from cluster csv file; defaulting to create
  ([`c9555ed`](https://github.com/mbari-org/aidata/commit/c9555ed5d5789b3d56ef68cc0ed8f6e5d6b5582c))


## v1.54.0 (2025-06-02)

### Documentation

- Add more details on features and icons consistent with other docs
  ([`a50a28d`](https://github.com/mbari-org/aidata/commit/a50a28d05cdeecc2129e3160bb9055d9d16bd55d))

- Minor update to clarity on DEVELOPMENT.md
  ([`7d79317`](https://github.com/mbari-org/aidata/commit/7d7931794fea4d4b4dc57a77a61ca3dbc3d2be62))

### Features

- Support both huggingface and local models with aidata load exemplars command
  ([`ce1f09f`](https://github.com/mbari-org/aidata/commit/ce1f09f50fa9d5c728d3b0f5c87ff900064c8ed4))


## v1.53.0 (2025-05-23)

### Features

- Handle enum attributes in tator loads simply as strings for now
  ([`0b96bc1`](https://github.com/mbari-org/aidata/commit/0b96bc12be21f1fb38872ac65736e0b172f109b2))


## v1.52.2 (2025-05-23)

### Bug Fixes

- Capture metadata from Path not str
  ([`49d75b0`](https://github.com/mbari-org/aidata/commit/49d75b0d7dc8893e4326a7bf665a82f7df946001))

### Performance Improvements

- Faster processing of redis queue, improved handling of resolving url and local files, and handle
  i2MAP special case processing prores/mov but previewing in mp4
  ([`f1929c1`](https://github.com/mbari-org/aidata/commit/f1929c13561cce7c44ee862c06d09e7740996230))


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

- Initial Release
