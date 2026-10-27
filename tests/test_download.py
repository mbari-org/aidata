# mbari_aidata, Apache-2.0 license
# Filename: tests/test_download.py
# Description: Tests for dataset download CLI options

from types import SimpleNamespace
import sys

from click.testing import CliRunner

from mbari_aidata.commands.download import download


def _setup_download_mocks(monkeypatch, version_names):
    captured = {}

    def fake_download(*args, **kwargs):
        captured.update(kwargs)
        return True

    fake_logger = SimpleNamespace(create_logger_file=lambda *args, **kwargs: None, info=lambda *args, **kwargs: None, exception=lambda *args, **kwargs: None)
    fake_coco_voc = SimpleNamespace(download=fake_download)

    class FakeApi:
        def get_version_list(self, _project_id):
            return [SimpleNamespace(name=name) for name in version_names]

    fake_common = SimpleNamespace(
        init_yaml_config=lambda _config: {"tator": {"project": "p1", "host": "http://example"}},
        init_api_project=lambda *_args, **_kwargs: (FakeApi(), SimpleNamespace(id=1)),
        find_project=lambda *_args, **_kwargs: SimpleNamespace(id=1, name="project"),
    )

    monkeypatch.setitem(sys.modules, "mbari_aidata.logger", fake_logger)
    monkeypatch.setitem(sys.modules, "mbari_aidata.generators.coco_voc", fake_coco_voc)
    monkeypatch.setitem(sys.modules, "mbari_aidata.plugins.loaders.tator.common", fake_common)
    return captured


def test_download_rejects_version_and_exclude_versions_together():
    runner = CliRunner()
    result = runner.invoke(
        download,
        [
            "--token",
            "token",
            "--config",
            "config.yml",
            "--version",
            "v1",
            "--exclude-versions",
            "v2",
        ],
    )

    assert result.exit_code == 2
    assert "--version and --exclude-versions cannot be used together" in result.output


def test_download_exclude_versions_filters_api_versions(monkeypatch, tmp_path):
    captured = _setup_download_mocks(monkeypatch, version_names=["v1", "v2", "v3"])
    runner = CliRunner()
    result = runner.invoke(
        download,
        [
            "--token",
            "token",
            "--config",
            "config.yml",
            "--exclude-versions",
            "v2, v3",
            "--base-path",
            str(tmp_path),
        ],
    )

    assert result.exit_code == 0
    assert captured["version_list"] == ["v1"]


def test_download_delete_requires_crop_roi():
    """Test that --delete is rejected unless --crop-roi is set."""
    runner = CliRunner()
    result = runner.invoke(
        download,
        [
            "--token",
            "token",
            "--config",
            "config.yml",
            "--delete",
        ],
    )

    assert result.exit_code == 2
    assert "--delete/--clean requires --crop-roi" in result.output


def test_download_clean_requires_crop_roi():
    """Test that --clean is rejected unless --crop-roi is set."""
    runner = CliRunner()
    result = runner.invoke(
        download,
        [
            "--token",
            "token",
            "--config",
            "config.yml",
            "--clean",
        ],
    )

    assert result.exit_code == 2
    assert "--delete/--clean requires --crop-roi" in result.output


def test_download_crop_roi_keeps_full_frames_by_default(monkeypatch, tmp_path):
    """Test that --crop-roi keeps full-frame media unless --delete or --clean is set."""
    captured = _setup_download_mocks(monkeypatch, version_names=["v1"])
    runner = CliRunner()
    result = runner.invoke(
        download,
        [
            "--token",
            "token",
            "--config",
            "config.yml",
            "--version",
            "v1",
            "--crop-roi",
            "--base-path",
            str(tmp_path),
        ],
    )

    assert result.exit_code == 0
    assert captured["crop_roi"] is True
    assert captured["delete_full_frames"] is False


def test_download_delete_requests_full_frame_removal(monkeypatch, tmp_path):
    """Test that --delete with --crop-roi asks the generator to remove full frames."""
    captured = _setup_download_mocks(monkeypatch, version_names=["v1"])
    runner = CliRunner()
    result = runner.invoke(
        download,
        [
            "--token",
            "token",
            "--config",
            "config.yml",
            "--version",
            "v1",
            "--crop-roi",
            "--delete",
            "--base-path",
            str(tmp_path),
        ],
    )

    assert result.exit_code == 0
    assert captured["delete_full_frames"] is True


def test_download_clean_requests_full_frame_removal(monkeypatch, tmp_path):
    """Test that --clean with --crop-roi asks the generator to remove full frames."""
    captured = _setup_download_mocks(monkeypatch, version_names=["v1"])
    runner = CliRunner()
    result = runner.invoke(
        download,
        [
            "--token",
            "token",
            "--config",
            "config.yml",
            "--version",
            "v1",
            "--crop-roi",
            "--clean",
            "--base-path",
            str(tmp_path),
        ],
    )

    assert result.exit_code == 0
    assert captured["delete_full_frames"] is True
