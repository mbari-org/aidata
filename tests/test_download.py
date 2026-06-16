# mbari_aidata, Apache-2.0 license
# Filename: tests/test_download.py
# Description: Tests for dataset download CLI version filters

from types import SimpleNamespace
import sys

from click.testing import CliRunner

from mbari_aidata.commands.download import download


def _setup_download_mocks(monkeypatch, version_names):
    captured = {}

    def fake_download(*args, **kwargs):
        captured["version_list"] = kwargs["version_list"]
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
