import numpy as np

from aegis_orbit.shields import ControlBarrierShield
from aegis_orbit.shields.cbf_shield import _ttc_constraint


# Hand derivation (d_safe = 40.0 m is an experimental parameter under test,
# not a derived physical constant; gamma = 0.1 1/s):
#   r . v = (-36000.0)(10.0) + (20.0)(0.0) + (0.0)(0.0)
#         = -360000.0 + 0.0 + 0.0 = -360000.0 m^2/s
#   |v|^2 = (10.0)^2 + (0.0)^2 + (0.0)^2
#         = 100.0 + 0.0 + 0.0 = 100.0 m^2/s^2
#   t_ttc = -(r . v) / |v|^2
#         = -(-360000.0 m^2/s) / (100.0 m^2/s^2)
#         = 360000.0 / 100.0 s = 3600.0 s
#   v*t_ttc = [10.0, 0.0, 0.0] m/s * 3600.0 s
#           = [36000.0, 0.0, 0.0] m
#   r_TCA = r + v*t_ttc
#         = [-36000.0, 20.0, 0.0] + [36000.0, 0.0, 0.0]
#         = [0.0, 20.0, 0.0] m
#   h_TTC = 0^2 + 20^2 + 0^2 - 40^2 = 400 - 1600 = -1200 m^2
#   Since r_TCA . v = 0, differentiating h_TTC = |r + v*t_ttc|^2 -
#   d_safe^2 with respect to v gives 2*t_ttc*r_TCA at the closest approach:
#       grad_v(h_TTC) = [0, 2(3600)(20), 0] = [0, 144000, 0] m*s
#   The existing shield convention is a . u <= b. From
#   grad_v(h_TTC) . u + gamma*h_TTC >= 0:
#       a = -grad_v(h_TTC) = [0, -144000, 0] m*s
#       b = gamma*h_TTC = (0.1)(-1200) = -120 m^2/s
#   For u_max = 1e-4 m/s^2 per axis, the box support is
#   ||a||_1*u_max = 144000*1e-4 = 14.4 m^2/s. Thus the minimum
#   attainable a . u is -14.4 m^2/s. Feasibility under a . u <= b
#   requires this minimum to be <= -120 m^2/s; -14.4 <= -120 is false.
#   Therefore the constraint is infeasible in this box. The support
#   comparison in magnitudes is 14.4 < |b| = 120 m^2/s.
_R = np.array([-36000.0, 20.0, 0.0])
_V = np.array([10.0, 0.0, 0.0])
_D_SAFE_EXPERIMENTAL_M = 40.0
_GAMMA = 0.1
_U_MAX = 1e-4


def _state(r, v):
    state = np.zeros(12, dtype=np.float64)
    state[:3] = r
    state[3:6] = v
    return state


def test_ttc_constraint_matches_hand_derivation():
    t_ttc, r_tca, h_ttc, a, b = _ttc_constraint(
        _R, _V, _D_SAFE_EXPERIMENTAL_M, _GAMMA
    )

    assert np.isclose(t_ttc, 3600.0, rtol=0.0, atol=1e-9)
    assert np.allclose(r_tca, [0.0, 20.0, 0.0], rtol=0.0, atol=1e-9)
    assert np.isclose(h_ttc, -1200.0, rtol=0.0, atol=1e-9)
    assert np.allclose(a, [0.0, -144000.0, 0.0], rtol=0.0, atol=1e-9)
    assert np.isclose(b, -120.0, rtol=0.0, atol=1e-9)


def test_ttc_box_support_matches_hand_feasibility():
    shield = ControlBarrierShield(
        d_safe=_D_SAFE_EXPERIMENTAL_M,
        u_max=_U_MAX,
        barrier_type="ttc",
        gamma=_GAMMA,
        allow_unvalidated_d_safe=True,
    )
    _, _, _, a, b = _ttc_constraint(_R, _V, shield.d_safe, shield.gamma)
    box_support = np.sum(np.abs(a)) * shield.u_max

    _, _, feasible = shield.filter_action(_state(_R, _V), np.zeros(3))

    assert np.isclose(box_support, 14.4, rtol=0.0, atol=1e-9)
    assert box_support < abs(b)
    assert not (-box_support <= b)
    assert feasible is False


def test_ttc_selection_does_not_change_spatial_default():
    default_shield = ControlBarrierShield(
        d_safe=_D_SAFE_EXPERIMENTAL_M,
        u_max=_U_MAX,
        allow_unvalidated_d_safe=True,
    )
    spatial_shield = ControlBarrierShield(
        d_safe=_D_SAFE_EXPERIMENTAL_M,
        u_max=_U_MAX,
        barrier_type="spatial",
        gamma=_GAMMA,
        allow_unvalidated_d_safe=True,
    )
    state = _state(_R, _V)
    u_nom = np.array([0.0, 5e-5, 0.0])

    default_result = default_shield.filter_action(state, u_nom)
    explicit_spatial_result = spatial_shield.filter_action(state, u_nom)

    assert default_shield.barrier_type == "spatial"
    assert np.array_equal(default_result[0], explicit_spatial_result[0])
    assert default_result[1:] == explicit_spatial_result[1:]
