# Run stages in parallel

1. Open the policy and click **New draft version** (or **Edit** an existing draft).
2. Add or open the stages that should run together.
3. On each of those stages, set **Parallel group** to the same number (e.g. `1`).
4. Leave **Parallel group** blank on stages that should remain sequential.
5. Click **Save** and **Activate** the new version.

Stages sharing a parallel-group number all activate at once. The next group
only starts after every stage in the current group is approved. Any single
stage rejecting terminates the request.
