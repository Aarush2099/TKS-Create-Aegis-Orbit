# CW state ordering from cw_relative_dynamics.py is [x, y, z, vx, vy, vz].
# At t = 0, nt = n*t = 0. The CW state-transition velocity block is the
# identity, and the position-to-velocity block is zero.
# Given n = 1.1e-3 rad/s, r = [0, 0, 0] m, and v = [0.5, 0, 0] m/s:
#   Delta-v = [0, 0, 0] - [0.5, 0, 0] = [-0.5, 0, 0] m/s.
#   |Delta-v| = sqrt((-0.5)^2 + 0^2 + 0^2) = 0.5 m/s.
#   |v| = sqrt(0.5^2 + 0^2 + 0^2) = 0.5 m/s, so |Delta-v| = |v|.
#   v_after = [0.5, 0, 0] + [-0.5, 0, 0] = [0, 0, 0] m/s.

import numpy as np

from aegis_orbit.envs.cw_relative_dynamics import propagate_relative
from planning.greedy import leg_delta_v


# For n = 1.1e-3 rad/s and t = 600 s:
#   nt = n*t = (1.1e-3)(600) = 0.66 rad.
#   sin(nt) = sin(0.66) = 0.6131168519734338.
#   cos(nt) = cos(0.66) = 0.7899922314973651.
# The CW radial-position row is
#   x(t) = (4 - 3*cos(nt))*x0 + (sin(nt)/n)*vx0
#          + (2*(1 - cos(nt))/n)*vy0.
# For r0 = [10, 0, 0] m and v0 = [0, 0, 0] m/s:
#   x(600) = (4 - 3*0.7899922314973651)*10
#            + (0.6131168519734338/1.1e-3)*0
#            + (2*(1 - 0.7899922314973651)/1.1e-3)*0
#          = (4 - 2.3699766944920953)*10
#          = 1.6300233055079047*10
#          = 16.300233055079047 m.
# The t=0 impulse sets relative velocity to zero by construction, so its
# delta-v is 0 m/s; this nonzero radial position is the CW coast result.
def test_cw_radial_position_matches_hand_derived_value_after_coast():
    initial_state = [10.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    expected_radial_position_m = 16.300233055079047

    propagated_state = propagate_relative(initial_state, 1.1e-3, 600.0)

    assert abs(propagated_state[0] - expected_radial_position_m) <= 1e-9


def test_leg_delta_v_nulls_initial_radial_relative_velocity():
    initial_state = np.array([0.0, 0.0, 0.0, 0.5, 0.0, 0.0])

    assert abs(leg_delta_v(initial_state) - 0.5) <= 1e-12
