import numpy as np

from tradingbots.strategies import intraday_momentum as im


def test_check_offsets_default_is_every_half_hour_10_to_1530():
    assert im.check_offsets(im.Params()) == list(range(30, 361, 30))


def test_check_offsets_other_intervals():
    assert im.check_offsets(im.Params(check_interval_min=60)) == [60, 120, 180, 240, 300, 360]
    assert im.check_offsets(im.Params(check_interval_min=15))[0] == 30


def test_typical_move_uses_prior_days_only():
    rng = np.random.default_rng(0)
    moves = rng.random((20, 5))
    sigma = im.typical_move(moves, 14)
    assert np.isnan(sigma[:14]).all()
    np.testing.assert_allclose(sigma[14], moves[0:14].mean(axis=0))
    np.testing.assert_allclose(sigma[19], moves[5:19].mean(axis=0))
    changed = moves.copy()
    changed[19] += 100.0          # today's data must not move today's boundary
    np.testing.assert_allclose(im.typical_move(changed, 14)[19], sigma[19])


def test_boundaries_widen_on_gaps():
    sigma = np.array([0.01])
    up, lo = im.boundaries(100.0, 105.0, sigma, 1.0)     # gap down: upper anchors to prior close
    assert up[0] == 105.0 * 1.01 and lo[0] == 100.0 * 0.99
    up, lo = im.boundaries(105.0, 100.0, sigma, 1.0)     # gap up: lower anchors to prior close
    assert up[0] == 105.0 * 1.01 and lo[0] == 100.0 * 0.99


def test_target_position_rules():
    assert im.target_position(0, 101, 100, 90, 95) == 1
    assert im.target_position(0, 89, 100, 90, 95) == -1
    assert im.target_position(0, 95, 100, 90, 95) == 0
    # Long stays only while above the higher of the upper boundary and VWAP.
    assert im.target_position(1, 103, 100, 90, 102) == 1
    assert im.target_position(1, 101, 100, 90, 102) == 0
    # Short stays only while below the lower of the lower boundary and VWAP.
    assert im.target_position(-1, 87, 100, 90, 88) == -1
    assert im.target_position(-1, 89, 100, 90, 88) == 0


def test_stop_distance_on_tick_grid_with_floor():
    assert im.stop_distance(0.00030769, 5003.08, 0.25) == 1.5
    assert im.stop_distance(0.0, 5000.0, 0.25) == 0.25


def test_vwap_constant_price():
    x = np.full(10, 50.0)
    np.testing.assert_allclose(im.session_vwap(x, x, x, np.arange(1, 11)), 50.0)
