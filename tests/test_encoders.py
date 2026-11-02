import numpy as np

from rag.encoders import mean_pool


def test_mean_pool_ignores_padding_and_normalises():
    hidden = np.array([[[1.0, 0.0], [3.0, 0.0], [100.0, 100.0]]])  # last token is padding
    mask = np.array([[1, 1, 0]])
    out = mean_pool(hidden, mask)
    np.testing.assert_allclose(out, [[1.0, 0.0]])


def test_sentencepiece_ids_match_reference_tokenizer():
    """The light SentencePiece path must give the same ids as the 245 MB tokenizer.json."""
    import json
    from pathlib import Path

    import pytest

    tokenizers = pytest.importorskip("tokenizers")
    from huggingface_hub import hf_hub_download

    from rag.encoders import XlmrTokenizer

    name = "intfloat/multilingual-e5-small"
    reference = tokenizers.Tokenizer.from_file(hf_hub_download(name, "onnx/tokenizer.json"))
    reference.enable_truncation(512)
    light = XlmrTokenizer(hf_hub_download(name, "onnx/sentencepiece.bpe.model"), max_length=512)
    root = Path(__file__).resolve().parent.parent
    texts = [json.loads(l)["text"] for l in open(root / "data" / "chunks.jsonl", encoding="utf-8")]
    texts += ["query: " + json.loads(l)["question"] for l in open(root / "eval" / "questions.jsonl", encoding="utf-8")]
    for text in texts:
        assert light.ids("passage: " + text) == reference.encode("passage: " + text).ids
