# Rigor Levels

Use depth level to decide how hard to review. Depth is independent from artifact type.

Levels are cumulative: each level includes the expectations below it. When a lower-level or higher-level check does not apply to the artifact, mark it N/A with a reason.

| Level | Name | Required Behavior |
|---|---|---|
| 1 | Quick Scan | Identify obvious blockers only. Keep the report short. |
| 2 | Basic Review | Add governing-spec fit, obvious omissions, and obvious accuracy issues. |
| 3 | Standard POTATO | Apply applicable POTATO variants with evidence for each finding. Default for ordinary "review" requests. |
| 4 | Submission Check | Add deliverable readiness, required sections, formatting, deadlines, file naming, and packaging checks when relevant. |
| 5 | Harsh Critic | Findings first; no praise before blockers; material risks separated from minor polish. |
| 6 | Academic / Professional Rigor | Add source quality, argument quality, limitations, audience fit, and methodology fit when relevant. |
| 7 | Source Integrity | Add source authority, recency, DOI/URL/stable locator, source-to-claim trace, citation/reference symmetry, and source bias checks. |
| 8 | Doctoral / Expert Review | Add Toulmin-style argument checks and discipline-specific standards for claims, methods, limitations, and rebuttals. |
| 9 | Verification Pass | Add render/layout checks, metadata checks, table/figure cross-references, and source/reference dual pass when tools and files permit. |
| 10 | Defense Mode | Add adversarial objections, source triangulation, dual-pass verification, methodology/risk-of-bias review, and final readiness verdict. |

## Default Inference

If the user names a level, use it. If user language maps to several levels, choose the higher level unless the user asks for speed or brevity.

| User language | Level |
|---|---|
| "quick", "skim", "sanity check" | 1-2 |
| "review", "POTATO review" | 3 |
| "submission ready", "check formatting", "deliverable" | 4 |
| "harsh", "critical", "adversarial" | 5 |
| "academic", "scholarly", "graduate" | 6 |
| "source audit", "citations", "references" | 7 |
| "PhD", "doctoral", "publication quality" | 8 |
| "verify everything", "metadata", "render", "dual pass" | 9 |
| "defense mode", "maximum rigor", "incredible PhD rigor" | 10 |

## Tooling Limits

Levels 9 and 10 are best-effort when local tools are unavailable. Do not claim metadata, render, DOI, URL, or source verification unless it was actually performed. State verification limits in the report.
