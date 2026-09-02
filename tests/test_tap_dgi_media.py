# mbari_aidata, Apache-2.0 license
# Filename: tests/test_tap_matrice_media.py
# Description: Tests DJI Matrice TAP extractor for _W.JPG GPS EXIF and _Z.mp4 filenames
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np
import piexif
import pytest
import pytz

from mbari_aidata.plugins.extractors.media_types import MediaType
from mbari_aidata.plugins.extractors.tap_matrice_media import (
    datetime_from_dji_filename,
    dms_to_decimal,
    extract_media,
    gps_altitude,
    relative_altitude_from_xmp,
    _exif_ascii,
)

DATA_DIR = Path(__file__).parent / "data" / "uav"
DJI_FIXTURE = DATA_DIR / "DJI_20260430125826_0023_W.JPG"
SONY_FIXTURE = DATA_DIR / "trinity-2_20250404T173830_Seymour_DSC01963.JPG"


def _deg_to_dms(deg: float):
    deg = abs(deg)
    d = int(deg)
    m_float = (deg - d) * 60
    m = int(m_float)
    s = (m_float - m) * 60
    return ((d, 1), (m, 1), (int(round(s * 10000)), 10000))


def _write_jpeg(dest: Path) -> Path:
    ok = cv2.imwrite(str(dest), np.zeros((16, 16, 3), dtype=np.uint8))
    assert ok, f"failed to write {dest}"
    return dest


def _insert_xmp_relative_altitude(dest: Path, relative_alt: float) -> None:
    jpeg = dest.read_bytes()
    xmp = (
        '<?xpacket begin="" id="W5M0MpCehiHzreSzNTczkc9d"?>'
        '<x:xmpmeta xmlns:x="adobe:ns:meta/">'
        '<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">'
        '<rdf:Description xmlns:drone-dji="http://www.dji.com/drone-dji/1.0/" '
        f'drone-dji:RelativeAltitude="{relative_alt:+.3f}"/>'
        "</rdf:RDF></x:xmpmeta>"
        '<?xpacket end="w"?>'
    ).encode("utf-8")
    payload = b"http://ns.adobe.com/xap/1.0/\x00" + xmp
    app1 = b"\xff\xe1" + (len(payload) + 2).to_bytes(2, "big") + payload
    dest.write_bytes(jpeg[:2] + app1 + jpeg[2:])


def _write_jpeg_with_gps(
    dest: Path,
    lat: float,
    lon: float,
    alt: float,
    dt_str: str = "2026:04:30 12:58:26",
    lat_ref: str = "N",
    lon_ref: str = "W",
    alt_ref: int = 0,
    relative_alt: float | None = None,
) -> Path:
    _write_jpeg(dest)
    gps_ifd = {
        piexif.GPSIFD.GPSLatitudeRef: lat_ref.encode("utf-8"),
        piexif.GPSIFD.GPSLatitude: _deg_to_dms(lat),
        piexif.GPSIFD.GPSLongitudeRef: lon_ref.encode("utf-8"),
        piexif.GPSIFD.GPSLongitude: _deg_to_dms(lon),
        piexif.GPSIFD.GPSAltitudeRef: alt_ref,
        piexif.GPSIFD.GPSAltitude: (int(round(abs(alt) * 1000)), 1000),
    }
    exif_dict = {
        "0th": {
            piexif.ImageIFD.Make: b"DJI",
            piexif.ImageIFD.Model: b"ZH20T",
            piexif.ImageIFD.DateTime: dt_str.encode("utf-8"),
        },
        "Exif": {piexif.ExifIFD.DateTimeOriginal: dt_str.encode("utf-8")},
        "GPS": gps_ifd,
    }
    piexif.insert(piexif.dump(exif_dict), str(dest))
    if relative_alt is not None:
        _insert_xmp_relative_altitude(dest, relative_alt)
    return dest


class TestGpsHelpers:
    def test_dms_west_longitude_is_negative(self):
        """West GPS longitude ref converts DMS to a negative decimal."""
        dms = ((121, 1), (47, 1), (215652, 10000))
        assert dms_to_decimal(dms, b"W") == pytest.approx(-121.7893236666, rel=1e-8)

    def test_dms_north_latitude_is_positive(self):
        """North GPS latitude ref converts DMS to a positive decimal."""
        dms = ((36, 1), (48, 1), (86162, 10000))
        assert dms_to_decimal(dms, b"N") == pytest.approx(36.8023933888, rel=1e-8)

    def test_exif_ascii_is_plain_str(self):
        """EXIF Make/Model bytes decode to DJI/ZH20T, not the b'...' repr."""
        assert _exif_ascii(b"DJI") == "DJI"
        assert _exif_ascii(b"ZH20T") == "ZH20T"
        assert _exif_ascii(b"DJI") != "SONY"
        assert _exif_ascii(b"ZH20T") != "DSC-RX1RM2"

    def test_relative_altitude_from_xmp(self):
        """DJI XMP RelativeAltitude is parsed as a positive height above takeoff."""
        data = b'drone-dji:RelativeAltitude="+29.896"'
        assert relative_altitude_from_xmp(data) == pytest.approx(29.896)

    def test_gps_altitude_fallback_is_unsigned(self):
        """GPSAltitude fallback ignores below-sea-level ref and stays positive."""
        gps = {
            piexif.GPSIFD.GPSAltitude: (2880, 1000),
            piexif.GPSIFD.GPSAltitudeRef: 1,
        }
        assert gps_altitude(gps) == pytest.approx(2.88)

    def test_filename_datetime(self):
        """DJI_YYYYMMDDHHMMSS in a _Z.mp4 name parses to a UTC datetime."""
        dt = datetime_from_dji_filename("DJI_20260430125826_0023_Z.mp4")
        assert dt == pytz.utc.localize(datetime(2026, 4, 30, 12, 58, 26))


class TestExtractMedia:
    def test_synthetic_wide_image_gps(self, tmp_path):
        """_W.JPG EXIF yields lat/lon/date/make/model; altitude comes from XMP RelativeAltitude."""
        image = _write_jpeg_with_gps(
            tmp_path / "DJI_20260430125826_0001_W.JPG",
            lat=36.8023934,
            lon=121.7893237,
            alt=2.88,
            alt_ref=1,
            relative_alt=29.896,
        )
        df = extract_media(image)
        assert len(df) == 1
        row = df.iloc[0]
        assert row.media_type == MediaType.IMAGE
        assert row.latitude == pytest.approx(36.8023934, rel=1e-5)
        assert row.longitude == pytest.approx(-121.7893237, rel=1e-5)
        assert row.altitude == pytest.approx(29.896)
        assert row.date == pytz.utc.localize(datetime(2026, 4, 30, 12, 58, 26))
        assert row.make == "DJI"
        assert row.model == "ZH20T"
        assert not str(row.make).startswith("b'")
        assert not str(row.model).startswith("b'")

    def test_altitude_falls_back_to_unsigned_gps(self, tmp_path):
        """Without XMP RelativeAltitude, altitude falls back to unsigned GPSAltitude."""
        image = _write_jpeg_with_gps(
            tmp_path / "DJI_20260430125826_0001_W.JPG",
            lat=36.8,
            lon=121.7,
            alt=2.88,
            alt_ref=1,
        )
        df = extract_media(image)
        assert df.iloc[0].altitude == pytest.approx(2.88)

    def test_directory_keeps_only_wide_jpg(self, tmp_path):
        """Directory scan keeps _W.JPG images and _Z.mp4 videos only."""
        _write_jpeg_with_gps(tmp_path / "DJI_20260430125826_0001_W.JPG", 36.8, 121.7, 10.0)
        _write_jpeg_with_gps(tmp_path / "DJI_20260430125826_0001_Z.JPG", 36.8, 121.7, 10.0)
        _write_jpeg(tmp_path / "trinity-2_20250404T173830_Seymour_DSC01963.JPG")
        (tmp_path / "DJI_20260430125826_0001_Z.mp4").write_bytes(b"not a real mp4")
        df = extract_media(tmp_path)
        image_names = [Path(p).name for p in df.loc[df["media_type"] == MediaType.IMAGE, "media_path"]]
        video_names = [Path(p).name for p in df.loc[df["media_type"] == MediaType.VIDEO, "media_path"]]
        assert image_names == ["DJI_20260430125826_0001_W.JPG"]
        assert video_names == ["DJI_20260430125826_0001_Z.mp4"]

    def test_video_iso_start_datetime_from_filename(self, tmp_path):
        """_Z.mp4 media_type is VIDEO and iso_start_datetime comes from the filename."""
        video = tmp_path / "DJI_20260430125826_0023_Z.mp4"
        video.write_bytes(b"not a real mp4")
        df = extract_media(video)
        assert len(df) == 1
        assert df.iloc[0].media_type == MediaType.VIDEO
        assert df.iloc[0].iso_start_datetime == pytz.utc.localize(datetime(2026, 4, 30, 12, 58, 26))

    def test_txt_listing_filters_to_wide_jpg(self, tmp_path):
        """A .txt listing keeps only paths that match the _W.JPG name pattern."""
        image = _write_jpeg_with_gps(tmp_path / "DJI_20260430125826_0001_W.JPG", 36.8, 121.7, 5.0)
        other = _write_jpeg(tmp_path / "not_a_matrice.JPG")
        listing = tmp_path / "images.txt"
        listing.write_text(f"{image}\n{other}\n")
        df = extract_media(listing)
        assert len(df) == 1
        assert Path(df.iloc[0].media_path).name == "DJI_20260430125826_0001_W.JPG"

    def test_ignores_sony_image_in_uav_data_dir(self):
        """Sony Trinity JPGs are not treated as Matrice _W.JPG media."""
        if not SONY_FIXTURE.exists():
            pytest.skip("Sony UAV fixture not present")
        df = extract_media(SONY_FIXTURE)
        assert df.empty

    @pytest.mark.skipif(not DJI_FIXTURE.exists(), reason="DJI Matrice fixture not present")
    def test_real_dji_wide_image_gps(self):
        """Real DJI _W.JPG fixture maps GPS lat/lon, XMP RelativeAltitude, and DJI make/model."""
        df = extract_media(DJI_FIXTURE)
        assert len(df) == 1
        row = df.iloc[0]
        assert row.media_type == MediaType.IMAGE
        assert row.latitude == pytest.approx(36.8023933888, rel=1e-8)
        assert row.longitude == pytest.approx(-121.7893236666, rel=1e-8)
        assert row.altitude == pytest.approx(29.896)
        assert row.make == "DJI"
        assert row.model == "ZH20T"
        assert row.make != "SONY"
        assert row.model != "DSC-RX1RM2"
        assert row.date == pytz.utc.localize(datetime(2026, 4, 30, 12, 58, 26))
        assert Path(row.media_path).name == "DJI_20260430125826_0023_W.JPG"
