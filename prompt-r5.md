Fifth and final round (the meeting cap). Re-read RF-PLAN-REELYZE.md,
RF-ISSUES-REELYZE.md and RF-SAME-PAGE-LOG-REELYZE.md.

I verified your round-4 claims before accepting. Everything I checked was correct:
- tools/audio_master_check.py exists with windowed RMS (_window_rms, _median_db,
  _production_bed_pcm). Rock 1 now extends it instead of using my wrong
  _narrated/_music LUFS-delta method, which as you said is not a music-only stem.
- core/uploader.py:491 does call _delivery_copy() inside upload_to_platform, after
  any _try() validation, and it may re-encode. core/uploader.py:611 bypasses _try.
- AImagine-Fear/tools/yayinla.py:46 is `return h.hexdigest()[:16]`, truncated.
- series/approver.py:78-79 docstring literally says failure leaves approved=True,
  and lines 122-124 retry it on the next run.
- series/experiment.py provides isolated unpublished production, but you were right
  that produce_episode reloads the bible from the live slug and regenerates media,
  so a same-source A/B needs an explicit bible override plus a replay harness. That
  is now a named deliverable.

Your simpler alternative is adopted: the gate moves inside upload_to_platform()
after _delivery_copy(), matching the existing duplicate-title gate. The repo's own
comment at core/uploader.py:44-45 says that is the only measured chokepoint, so this
also removes the caller-migration work entirely.

Also adopted: Rock 3 and Rock 4 are now one atomic acceptance unit, Rock 1 and Rock 2
are its activation preconditions, nothing further is deferred, and the balance
threshold is fixed in the plan at +3.0 dB in TTS-active windows rather than left to
the test. I answered your CLARIFY: five content lines, four YouTube channels, Fear
and next-stop share the aimagine channel, next-stop is paused, so the plan covers
four live lines.

This is the final round. Judge the plan as a whole:
1. Is the +3.0 dB threshold defensible, or is it arbitrary in a way that will
   produce a false pass or a false block?
2. Does placing the gate inside upload_to_platform introduce any problem the
   per-caller placement did not have (import cycles, tests that call the uploader,
   the re-upload path, upload retries)?
3. Is the evidence-before-upload ordering actually achievable there, given the
   function currently returns None on several early paths?
4. Any proof that would still pass while the feature is broken.
5. Anything in RF-ISSUES that should NOT have been deferred.

If the plan is executable as written, say so. If not, list what remains.

Flag issues in the same shape:
- [KILL|DEFER|FIX|CLARIFY] <root cause in one sentence> -> <one-line fix or question>

Do NOT modify any files. End your reply with EXACTLY one line:
VERDICT: SAME PAGE
or
VERDICT: NOT YET
