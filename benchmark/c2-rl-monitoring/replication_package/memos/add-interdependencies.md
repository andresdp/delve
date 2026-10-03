ADD 2 (Production Monitoring Signal Selection) feeds directly into ADD 3 (Automated Response Mechanism), as detection signals (e.g. metric divergence, feature drift) trigger responses like circuit breakers or rollbacks—memos cross-link these explicitly (e.g. Source 2's safety activation to ADD 3).

ADD 2 (Production Monitoring Signal Selection) constrains ADD 4 (Reward Degradation Test Statistic Selection), as the signal repertoire determines which statistical tests are applicable — the covariance-weighted test and BFAR both require episodic reward signals, meaning that signal choices in ADD 2 that lack episodic structure rule out these methods in ADD 4 (Source 2, Greenberg & Mannor).


ADD 4 (Reward Degradation Test Statistic Selection) constrains ADD 5 (False Alarm Rate Control Method), as the selected test determines which calibration methods are applicable — BFAR relies on the assumption that episodes are i.i.d. even when time-steps are not, meaning it presupposes an episodic test statistic has been selected in ADD 4 (Source 2, Greenberg & Mannor).


ADD 4 (Reward Degradation Test Statistic) complements but is limited by ADD 6 (Reward Hacking Detection Strategy), since reward signals detect downward drift but miss upward gaming/inflation; memos note their combination covers both directions (e.g. Source 6).

ADD 6 (Reward Hacking Detection Strategy) and ADD 7 (Reward Hacking Mitigation) interact tensely: mitigations like RLHF can induce context-dependent hiding, degrading CoT analysis in ADD 6 (Memos 13, 27), requiring architectural separation of detection/mitigation.