# Matching Algorithm v1

This version implements a lightweight, rule-based approach used by
`/v1/match/opportunities`.

## Scoring Factors

1. **Skill Overlap** – ratio of volunteer skills that satisfy the required
   skills for an opportunity.
2. **Location** – perfect score when remote is allowed or city and country
   match. Half score when only the country matches.
3. **Availability** – perfect score when volunteer availability equals the
   opportunity's commitment type. A smaller boost is applied when either side is
   flexible.

The final score is the average of the three factors and is returned as a value
between `0` and `100`.

This simple strategy provides deterministic results and executes in under
100&nbsp;ms for 1000 opportunities on typical hardware.
