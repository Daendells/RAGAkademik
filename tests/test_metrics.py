from rag.metrics import hit_at_k, reciprocal_rank, summarize


def test_hit_at_k_boundary():
    assert hit_at_k([5, 7, 9], {9}, k=3)
    assert not hit_at_k([5, 7, 9], {9}, k=2)


def test_duplicate_pasal_counts_once():
    # Three chunks of Pasal 5 must not push Pasal 9 out of the top 2.
    assert hit_at_k([5, 5, 5, 9], {9}, k=2)
    assert reciprocal_rank([5, 5, 9], {9}) == 0.5


def test_reciprocal_rank():
    assert reciprocal_rank([1, 2, 3], {3}) == 1 / 3
    assert reciprocal_rank([1, 2, 3], {4}) == 0.0


def test_summarize():
    rows = [{"ranked": [3, 1], "gold": [1]}, {"ranked": [2], "gold": [9]}]
    s = summarize(rows)
    assert s == {"n": 2, "hit@1": 0.0, "hit@3": 0.5, "hit@5": 0.5, "mrr": 0.25}
