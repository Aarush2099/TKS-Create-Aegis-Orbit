# Leg definition: coast for T = 600 s under the CW state transition with no
# thrust, then instantaneously cancel the full post-coast relative velocity.
# Leg delta-v is the magnitude of that velocity.
#
# Case: n = 1.1e-3 rad/s, r0 = [10, 0, 0] m, v0 = [0, 0, 0] m/s.
#   nT = (1.1e-3 rad/s)(600 s) = 0.66 rad.
# The standard sine and cosine values used here are from their Taylor series
# about zero:
#   sin(x) = x - x^3/3! + x^5/5! - x^7/7! + x^9/9! - ...,
#   sin(0.66) = 0.6131168519734338.
#   cos(x) = 1 - x^2/2! + x^4/4! - x^6/6! + x^8/8! - ...,
#   cos(0.66) = 0.7899922314973651.
#
# From the CW velocity-block row for x-velocity:
#   vx(T) = 3n*sin(nT)*x0
#         = 3(1.1e-3)(0.6131168519734338)(10)
#         = (0.0033)(0.6131168519734338)(10)
#         = (0.00202328561151233154)(10)
#         = 0.0202328561151233154 m/s.
#
# From the CW velocity-block row for y-velocity (vx0 = vy0 = 0):
#   vy(T) = 6n(cos(nT) - 1)*x0
#         = 6(1.1e-3)(0.7899922314973651 - 1)(10)
#         = 6(1.1e-3)(-0.2100077685026349)(10)
#         = (0.0066)(-0.2100077685026349)(10)
#         = (-0.00138605127211739034)(10)
#         = -0.0138605127211739034 m/s.
#   vz(T) = 0 m/s because z-motion is not excited by this case.
#
# Full cancellation magnitude:
#   |v(T)| = sqrt(vx(T)^2 + vy(T)^2 + vz(T)^2)
#          = sqrt(0.0202328561151233154^2
#                 + (-0.0138605127211739034)^2 + 0^2)
#          = sqrt(0.00040936846657528294
#                 + 0.00019211381289382360)
#          = sqrt(0.00060148227946910654)
#          = 0.02452513566668096... m/s.
# The expected value comes from this derivation, not from the simulator.
# The earlier value 0.020232855 was a rounding error and is superseded.

from planning.multileg import coast_then_cancel_delta_v


def test_coast_then_cancel_delta_v_matches_hand_derived_full_velocity():
    expected_delta_v_mps = 0.0245251356666

    actual_delta_v_mps = coast_then_cancel_delta_v(
        [10.0, 0.0, 0.0],
        [0.0, 0.0, 0.0],
        1.1e-3,
        600.0,
    )

    assert abs(actual_delta_v_mps - expected_delta_v_mps) <= 1e-9
