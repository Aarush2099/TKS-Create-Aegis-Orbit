# Sequencing rule: sort targets by ascending miss distance at t = 0 (|r0|);
# break ties by object_id ascending.
#
# For target A, r0_A = [30, 40, 0] m:
#   |r0_A| = sqrt(30^2 + 40^2) = sqrt(900 + 1600) = 50 m.
# For target B, r0_B = [10, 0, 0] m:
#   |r0_B| = sqrt(10^2 + 0^2 + 0^2) = 10 m.
# Thus the order is B, then A.
#
# Each leg's delta-v is the instantaneous cancellation of its own initial
# velocity, as in leg_delta_v:
#   |v0_A| = |[0.3, 0, 0]| = 0.3 m/s.
#   |v0_B| = |[0, 0.4, 0]| = 0.4 m/s.
#   Total delta-v = 0.3 + 0.4 = 0.7 m/s.
# Expected order: ["B", "A"]; expected total delta-v: 0.7 m/s.

from planning.greedy_sequencing import plan_order, total_delta_v


def test_greedy_sequencing_orders_two_targets_and_sums_hand_derived_delta_v():
    targets = [
        {
            "object_id": "A",
            "r0": [30.0, 40.0, 0.0],
            "v0": [0.3, 0.0, 0.0],
        },
        {
            "object_id": "B",
            "r0": [10.0, 0.0, 0.0],
            "v0": [0.0, 0.4, 0.0],
        },
    ]

    assert plan_order(targets) == ["B", "A"]
    assert abs(total_delta_v(targets) - 0.7) <= 1e-12
