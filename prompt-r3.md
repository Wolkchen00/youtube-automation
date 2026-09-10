Third round. Re-read RF-PLAN-REELYZE.md, RF-ISSUES-REELYZE.md and
RF-SAME-PAGE-LOG-REELYZE.md.

I verified your round-2 claims myself before accepting. All five I checked were correct:
- core/kie_api.py:483 does document `seedance-2-fast` while gunluk.py:30 calls
  `bytedance/seedance-2`. My "1080p is impossible" claim was wrong and is retracted.
  The plan no longer touches canon before a measured canary.
- produce.py:604/:656/:659 confirmed: master_lufs flips amix_normalize, music_volume
  0.28 -> 0.50, and limit_mix_peak. Rock 1 now requires a per-series narration/music
  balance check, not just LUFS and true peak.
- tests/test_rocka_audio_master.py:117 test_only_unnatural_lab_has_master_lufs exists
  and would break. The plan now requires migrating it, not deleting it.
- `concurrency: group: kie-uretim` exists in calibrate.yml, event-horizon.yml and
  fear-slide.yml. I killed the reservation rock.
- fear-slide-hazir.yml has only actions/setup-python@v5, no ffmpeg. Rock 6 installs it.

Structural changes: old Rock 2 merged into Rock 6 (one gate, one place). Seven rocks
became six. Every proof now names a specific test file, and files that do not exist
are listed as deliverables of their rock.

Be skeptical of this revision. Specifically:
1. Rock 1's "balance check": is comparing narration-only and music-only stem levels
   actually achievable from produce.py's pipeline, or does the mix happen in one
   ffmpeg pass with no separable stems? If not achievable, say so.
2. Rock 2 makes canon edits depend on a human decision after a canary. Does that
   leave the plan blocked or unfinishable, and is the canary itself well specified
   enough to be run by someone else?
3. Rock 3 says quarantine incompatible routes and skip them in `sirdaki()`. Look at
   the real rotation logic: does skipping break the ordering invariant, the state
   file, or the same-day lock?
4. Rock 6 validates inside `_try()` after platform source selection. Is `_try()`
   the right seam, does it exist with that name, and can it see the contract?
5. Any rock whose proof would still pass while the feature is broken.
6. Is six rocks now too much for one cycle? If so, which single rock delivers the
   most Core Focus per unit of risk, and what should be deferred?

Flag issues in the same shape:
- [KILL|DEFER|FIX|CLARIFY] <root cause in one sentence> -> <one-line fix or question>

Do NOT modify any files. End your reply with EXACTLY one line:
VERDICT: SAME PAGE
or
VERDICT: NOT YET
