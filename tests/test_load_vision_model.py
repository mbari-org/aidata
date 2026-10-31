# mbari_aidata, Apache-2.0 license
# Filename: tests/test_load_vision_model.py
# Description: Tests BackboneClassifier fine-tune loading for exemplar embeddings
import json
from pathlib import Path

import pytest
import torch

from mbari_aidata.predictors.process_vits import (
    _align_module_prefixes,
    _is_backbone_classifier,
    _load_backbone_classifier,
    _read_state_dict,
    load_vision_model,
)


class _Config:
    def __init__(self):
        self._name_or_path = ""


class _Model:
    def __init__(self, missing=None, unexpected=None):
        self.config = _Config()
        self.state = None
        self.missing = missing or []
        self.unexpected = unexpected or []

    def state_dict(self):
        return {}

    def load_state_dict(self, state, strict=False):
        self.state = state
        return self.missing, self.unexpected


def _write_config(model_dir: Path, config: dict) -> None:
    (model_dir / "config.json").write_text(json.dumps(config), encoding="utf-8")


def _write_bin(model_dir: Path, state: dict) -> None:
    torch.save(state, model_dir / "pytorch_model.bin")


def _patch_automodel(monkeypatch, model: _Model, captured: dict):
    def for_model(model_type, **kwargs):
        captured["model_type"] = model_type
        captured["kwargs"] = kwargs
        return {"built": model_type}

    def from_config(config):
        captured["config"] = config
        return model

    def from_pretrained(name):
        captured["pretrained"] = name
        return model

    auto_config = type("AutoConfig", (), {"for_model": staticmethod(for_model)})
    auto_model = type(
        "AutoModel",
        (),
        {"from_config": staticmethod(from_config), "from_pretrained": staticmethod(from_pretrained)},
    )
    monkeypatch.setattr("mbari_aidata.predictors.process_vits.AutoConfig", auto_config)
    monkeypatch.setattr("mbari_aidata.predictors.process_vits.AutoModel", auto_model)


def test_is_backbone_classifier_matches_model_type_or_architecture():
    """Test that wrapper saves are recognized by model_type or architectures."""
    assert _is_backbone_classifier({"model_type": "backbone_classifier"})
    assert _is_backbone_classifier({"architectures": ["BackboneClassifier"]})
    assert not _is_backbone_classifier({"model_type": "dinov2", "architectures": ["Dinov2Model"]})
    assert not _is_backbone_classifier({})


def test_load_vision_model_rebuilds_backbone_and_drops_the_head(tmp_path: Path, monkeypatch):
    """Test that a BackboneClassifier save loads backbone weights and ignores the classification head."""
    _write_config(
        tmp_path,
        {
            "model_type": "backbone_classifier",
            "backbone_config": {"model_type": "dinov2", "hidden_size": 8, "num_hidden_layers": 1},
        },
    )
    weight = torch.ones(2, 2)
    _write_bin(
        tmp_path,
        {
            "backbone.encoder.layer.0.weight": weight,
            "classifier.weight": torch.zeros(4, 2),
            "classifier.bias": torch.zeros(4),
            "dropout.weight": torch.zeros(1),
        },
    )
    model = _Model()
    captured = {}
    _patch_automodel(monkeypatch, model, captured)

    loaded = load_vision_model(str(tmp_path))

    assert loaded is model
    assert captured["model_type"] == "dinov2"
    assert captured["kwargs"] == {"hidden_size": 8, "num_hidden_layers": 1}
    assert set(model.state) == {"encoder.layer.0.weight"}
    assert torch.equal(model.state["encoder.layer.0.weight"], weight)
    assert loaded.config._name_or_path == str(tmp_path)
    assert "pretrained" not in captured


def test_load_vision_model_recognizes_architecture_name(tmp_path: Path, monkeypatch):
    """Test that architectures containing BackboneClassifier takes the same load path."""
    _write_config(
        tmp_path,
        {
            "architectures": ["BackboneClassifier"],
            "base_model": "facebook/dinov2-small",
        },
    )
    _write_bin(tmp_path, {"backbone.embeddings.cls_token": torch.ones(1, 1, 4)})
    model = _Model()
    captured = {}
    _patch_automodel(monkeypatch, model, captured)

    loaded = load_vision_model(str(tmp_path))

    assert loaded is model
    assert captured["pretrained"] == "facebook/dinov2-small"
    assert set(model.state) == {"embeddings.cls_token"}


def test_load_vision_model_reads_safetensors(tmp_path: Path, monkeypatch):
    """Test that model.safetensors is preferred over pytorch_model.bin."""
    pytest.importorskip("safetensors.torch")
    from safetensors.torch import save_file

    _write_config(tmp_path, {"model_type": "backbone_classifier", "base_model": "org/backbone"})
    save_file({"backbone.w": torch.ones(2)}, str(tmp_path / "model.safetensors"))
    _write_bin(tmp_path, {"backbone.w": torch.zeros(2)})
    model = _Model()
    captured = {}
    _patch_automodel(monkeypatch, model, captured)

    load_vision_model(str(tmp_path))

    assert torch.equal(model.state["w"], torch.ones(2))


def test_load_vision_model_delegates_plain_checkpoints(tmp_path: Path, monkeypatch):
    """Test that a normal config and a hub id still use AutoModel.from_pretrained."""
    _write_config(tmp_path, {"model_type": "vit", "architectures": ["ViTModel"]})
    model = _Model()
    captured = {}
    _patch_automodel(monkeypatch, model, captured)

    assert load_vision_model(str(tmp_path)) is model
    assert captured["pretrained"] == str(tmp_path)

    captured.clear()
    assert load_vision_model("google/vit-base-patch16-224") is model
    assert captured["pretrained"] == "google/vit-base-patch16-224"


def test_backbone_classifier_rejects_incomplete_saves(tmp_path: Path, monkeypatch):
    """Test that a BackboneClassifier save without a reconstructable backbone is rejected."""
    model = _Model()
    _patch_automodel(monkeypatch, model, {})

    _write_config(tmp_path, {"model_type": "backbone_classifier"})
    with pytest.raises(ValueError, match="neither backbone_config nor base_model"):
        _load_backbone_classifier(str(tmp_path), json.loads((tmp_path / "config.json").read_text()))

    _write_config(tmp_path, {"model_type": "backbone_classifier", "backbone_config": {"hidden_size": 4}})
    with pytest.raises(ValueError, match="no model_type"):
        _load_backbone_classifier(str(tmp_path), json.loads((tmp_path / "config.json").read_text()))

    _write_config(tmp_path, {"model_type": "backbone_classifier", "base_model": "org/backbone"})
    with pytest.raises(ValueError, match="No model.safetensors or pytorch_model.bin"):
        _load_backbone_classifier(str(tmp_path), json.loads((tmp_path / "config.json").read_text()))

    _write_bin(tmp_path, {"classifier.weight": torch.ones(2)})
    with pytest.raises(ValueError, match="No backbone weights"):
        _load_backbone_classifier(str(tmp_path), json.loads((tmp_path / "config.json").read_text()))

    _write_bin(tmp_path, {"backbone.w": torch.ones(2), "other.w": torch.ones(2)})
    with pytest.raises(ValueError, match="Unexpected weight keys"):
        _load_backbone_classifier(str(tmp_path), json.loads((tmp_path / "config.json").read_text()))

    _write_bin(tmp_path, {"backbone.w": torch.ones(2)})
    mismatched = _Model(missing=["w"])
    _patch_automodel(monkeypatch, mismatched, {})
    with pytest.raises(ValueError, match="do not match the architecture"):
        _load_backbone_classifier(str(tmp_path), json.loads((tmp_path / "config.json").read_text()))


def test_align_module_prefixes_adds_and_strips_nesting():
    """Test that keys differing only by a leading module path are renamed in both directions."""
    weight = torch.ones(1)
    added = _align_module_prefixes(
        {"embeddings.cls_token": weight, "layer.0.norm1.weight": weight},
        {"embeddings.cls_token", "model.layer.0.norm1.weight"},
    )
    assert set(added) == {"embeddings.cls_token", "model.layer.0.norm1.weight"}

    stripped = _align_module_prefixes(
        {"model.layer.0.norm1.weight": weight},
        {"layer.0.norm1.weight"},
    )
    assert set(stripped) == {"layer.0.norm1.weight"}


def test_align_module_prefixes_skips_ambiguous_matches():
    """Test that a key matching more than one expected key is left alone."""
    state = {"norm.weight": torch.ones(1)}
    aligned = _align_module_prefixes(state, {"a.norm.weight", "b.norm.weight"})
    assert set(aligned) == {"norm.weight"}


@pytest.mark.parametrize("saved_prefix", ["model.", ""])
def test_load_vision_model_loads_dinov3_across_transformers_layouts(tmp_path: Path, saved_prefix: str):
    """Test that a DINOv3 BackboneClassifier loads whether layers were saved as layer.N or model.layer.N."""
    transformers = pytest.importorskip("transformers")
    from transformers import AutoConfig, AutoModel

    backbone_config = {
        "model_type": "dinov3_vit",
        "hidden_size": 32,
        "num_hidden_layers": 2,
        "num_attention_heads": 2,
        "intermediate_size": 64,
    }
    try:
        reference = AutoModel.from_config(
            AutoConfig.for_model("dinov3_vit", **{k: v for k, v in backbone_config.items() if k != "model_type"})
        )
    except (KeyError, ValueError):
        pytest.skip(f"transformers {transformers.__version__} has no dinov3_vit")

    saved = {}
    for key, value in reference.state_dict().items():
        bare = key[len("model.") :] if key.startswith("model.layer.") else key
        if bare.startswith("layer."):
            bare = saved_prefix + bare
        saved["backbone." + bare] = value.clone()
    saved["classifier.weight"] = torch.zeros(3, 32)
    _write_bin(tmp_path, saved)
    _write_config(tmp_path, {"model_type": "backbone_classifier", "backbone_config": backbone_config})

    loaded = load_vision_model(str(tmp_path))

    for key, value in reference.state_dict().items():
        assert torch.equal(loaded.state_dict()[key], value)


def test_read_state_dict_loads_pytorch_bin(tmp_path: Path):
    """Test that a pytorch_model.bin state dict round-trips."""
    expected = {"backbone.w": torch.arange(4)}
    _write_bin(tmp_path, expected)

    loaded = _read_state_dict(str(tmp_path))

    assert torch.equal(loaded["backbone.w"], expected["backbone.w"])
