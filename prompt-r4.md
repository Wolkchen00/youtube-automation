Fourth round. Re-read RF-PLAN-REELYZE.md, RF-ISSUES-REELYZE.md and
RF-SAME-PAGE-LOG-REELYZE.md.

I accepted your scope recommendation. Six rocks became four:
- Rock 1: master_lufs for the two ACTIVE narration series only (event-horizon,
  flashpoints). next-stop dropped: series.json says status paused, I verified.
- Rock 2: AImagine-Fear audio mastering in the correct order.
- Rock 3: core/medya_sozlesmesi.py (the validator).
- Rock 4: bind it at the publication boundary (_try at series_runner.py:329).

Deferred with reasons in RF-ISSUES: the 1080p canary (I-1), route duration and
quarantine (I-8), next-stop (I-9).

I verified your round-3 claims before accepting. All four I checked were correct:
- aimagine/next-stop/series.json status is "paused".
- run_next's own docstring says it produces, publishes AND advances state.
- _try is at series_runner.py:329, exactly.
- kie_uret.py:112-113 defaults are sora-2-pro-storyboard and 25 seconds, so my
  canary spec would have spent credits on the wrong model at the wrong duration.
  That is now written into I-1 as an explicit requirement.

I also fixed I-1 and I-2, which still contained the retracted "1080p is impossible"
claim you flagged.

Independently of you I found that the quarantine problem is worse than you stated:
sirdaki() at gunluk.py:76-86 reads `gecmis` from the publish log, so a route that is
rejected pre-spend never enters it, stays "unused", and is returned again the next
day, permanently. Not "after it becomes oldest" but immediately. That is recorded in
I-8 as the reason duration work cannot ship without quarantine.

Be skeptical of this revision. Specifically:
1. Rock 1's isolated render harness: is there an existing supported way to render a
   fixed episode without touching series state and the publish log, or does the plan
   require building one? If it must be built, is that scoped honestly?
2. Rock 1 asserts event-horizon and flashpoints share one audio path. Verify that.
3. Rock 4 says activation is gated until Rocks 1 and 2 produce compliant output. Is
   that sequencing actually expressible, or does binding the gate immediately break
   live publishing on the first run?
4. Rock 4 lists callers to migrate atomically. Is that list complete?
5. Any proof that would still pass while the feature is broken.
6. Is four rocks now deliverable in one cycle, or is there still one that should be
   deferred?

Flag issues in the same shape:
- [KILL|DEFER|FIX|CLARIFY] <root cause in one sentence> -> <one-line fix or question>

Do NOT modify any files. End your reply with EXACTLY one line:
VERDICT: SAME PAGE
or
VERDICT: NOT YET
