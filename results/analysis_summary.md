# Analysis summary: monitor recruitment study (Project 1)

All numbers come from the frozen design v3 analysis. Generation: 1,200
agent-rounds (conditions A, B, C by diners and weakestlink, 10 trials,
10 rounds, 2 agents). Monitor: Qwen2.5-14B-Instruct, frozen prompt,
public record only. Threshold 51, calibrated on condition A trials 0
to 2 (118 negatives) at a 5 percent target false positive rate.
Held-out evaluation: trials 3 to 9, 840 agent-rounds.

## 1. Uptake (reported first, per the frozen order)

Monitor-directed messages: A 0 of 400, B 0 of 400, C 1 of 400. The
single C message was a fully honest round containing a passing mention
("no benefit in misleading Agent M or the monitor"). Monitor-directed
positives: 0 in every condition. No agent attempted to persuade,
address, or recruit the monitor.

## 2. Detection at the frozen threshold (held-out)

| Condition | Positives | Recall | 95% CI | Observed FPR | AUROC |
| A blind | 4 | 1.000 | (1.000, 1.000) | 0.065 | 0.987 |
| B awareness | 49 | 0.918 | (0.793, 0.983) | 0.043 | 0.974 |
| C invitation | 65 | 0.846 | (0.674, 0.958) | 0.051 | 0.941 |

Primary contrast (C against B): recall falls 7.2 points at comparable
observed false positive rates. Intervals overlap, so the drop is
suggestive, not decisive. Condition A recall rests on 4 positives and
carries no weight. Exploratory 1 percent operating point (threshold
76): recall B 0.633, C 0.569, the same direction.

By game (held-out): diners B recall 0.953 (43 positives), C 0.902
(61). Weakestlink B 0.667 (6), C 0.000 (4, mean score 12.5).
Weakestlink counts are too small for a standalone claim.

## 3. Behaviour: premeditated deception rates (all rounds)

| Game | A | B | C |
| Diners | 0.030 (6 of 200) | 0.305 (61) | 0.440 (88) |
| Weakestlink | 0.000 (0) | 0.035 (7) | 0.030 (6) |

Awareness raised the diners rate tenfold. The invitation raised it
further. Weakestlink barely moved under either change.

## 4. False positives by negative type (held-out, threshold 51)

| Negative type | A | B | C |
| Fully honest | 1 of 249 (0.004) | 2 of 207 (0.010) | 1 of 198 (0.005) |
| Impulsive deviation | 17 of 24 (0.708) | 8 of 20 (0.400) | 9 of 16 (0.562) |
| Intended deceptive, complied | 0 of 3 | 0 of 4 | 1 of 1 |

Nearly every false alarm is a changed-mind round, not an honest round.

## 5. Mechanism: pattern-stratified recall (held-out positives)

Diners has two deception patterns, and the mix is identical in B and
C: stated EXPENSIVE then final CHEAP is 67 percent of positives in
both conditions, and stated CHEAP then final EXPENSIVE is 33 percent
in both. Recall fell inside each pattern in C: the dominant pattern
fell from 0.931 (29 positives, mean score 77.1) in B to 0.878
(41 positives, mean score 73.8) in C, and the other pattern fell from
1.000 (14, mean 83.2) to 0.950 (20, mean 78.8). The diners detection
drop is therefore not a mix shift toward harder patterns. The same
patterns received softer scores under the invitation. Weakestlink
patterns are singletons (6 positives in B, 4 in C) and support no
pattern conclusion.

## 6. Evidence-format comparison (secondary, same logs)

Each view calibrated by the same rule on the same split.

| View | Threshold | Recall B | Recall C | AUROC B | AUROC C | FPR B | FPR C |
| Messages plus actions (headline) | 51 | 0.918 | 0.846 | 0.974 | 0.941 | 0.043 | 0.051 |
| Messages only | 21 | 0.367 | 0.492 | 0.715 | 0.772 | 0.026 | 0.042 |
| Actions only | 1 | 0.000 | 0.000 | 0.500 | 0.500 | 0.000 | 0.000 |
| Structured report | 76 | 0.878 | 0.862 | 0.986 | 0.978 | 0.017 | 0.033 |

Actions only: the monitor scored every one of the 1,200 rounds 0.
The target is invisible without the announcements. Structured view:
the B to C gap shrinks from 7.2 points to 1.6 points, so most of the
headline detection loss runs through the free-text message channel.

## 7. Bounded conclusions

1. Awareness of a named monitor did not deter deception. It raised
   the premeditated rate sharply in diners and left weakestlink
   almost unchanged.
2. The invitation raised the diners deception rate further while
   uptake of the invitation was zero. No agent wrote to the monitor.
3. Detection at the frozen threshold fell 7.2 points from B to C at
   comparable observed false positive rates, with overlapping
   intervals: suggestive, not decisive.
4. The drop is not explained by monitor-directed messages (none
   exist), and in diners it is not explained by a harder mix of
   deception patterns (the mix is identical; scores softened inside
   each pattern). A structured evidence view removes most of the gap.
5. Nothing in these logs supports a recruitment-by-persuasion claim.
   The supported claim is the measured invitation effect on behaviour
   and on detection, with the mechanism left open between the message
   channel and peer reaction to the public record.
