# FutureOS

- Product specification: IMPLEMENTATION_PLAN.md v1.3. User instructions override it.
- Current scope: M7, explicitly authorized by the user after M6. Native local hardening and release-readiness; no real charging/email or public deployment without separate authorization.
- M2 implementation and local acceptance checks are complete; see docs/milestones/M2-report.md. User waived manual M2 acceptance and authorized M3.
- Deployment: native local PostgreSQL + Redis, no Docker requirement (user decision).
- Read docs/architecture.md and docs/decisions/ before changing module boundaries.
- Core must not import apps/infra/workers, HTTP, persistence, billing or UI.
- Contracts originate in Pydantic; regenerate via make contracts, never hand-edit generated files.
- All Mock output is DEMO hypothesis; no real forecast publication, email or payment in M0.
- .env/.local are private and ignored. Never print credentials or modify unrelated databases.
- make check; make build; make local-verify. Record actual commands/output in the active milestone report.

- M3 implementation and local automated acceptance are complete; see docs/milestones/M3-report.md. Independent human fixture review remains pending; first REAL forward sample is not_due. User has now explicitly authorized M4.

- M4 implementation and local acceptance are complete; see docs/milestones/M4-report.md. Preserve .local/private-profile.key with database backups. M5 is now explicitly authorized; external email still requires explicit recipient consent and configured transport. No payment or M6.

- M5 implementation and native local automated acceptance complete: 308 pytest + 6 browser flows; see docs/milestones/M5-report.md. SMTP remains disabled/local-only. Do not enter M6 without user authorization.

- User authorized M6 sandbox implementation. Real payment/SMTP remain off; native PostgreSQL/Redis only.

- M6 local sandbox implementation and native automated acceptance complete: 328 pytest + 7 browser flows. See docs/milestones/M6-report.md. Sandbox enabled locally; live payment/SMTP and real custom research remain disabled. Do not enter M7 without user authorization.

- User authorized M7 security, reliability, backup/restore and bounded real research validation. Existing DeepSeek key may be used for one bounded validation, never printed.

- M7 native engineering checks completed: 353 pytest + 8 browser flows, 108 schemas, encrypted isolated restore/deletion replay and one bounded real validation. See docs/milestones/M7-report.md. Production remains NO-GO; unresolved developer minimatch advisory, independent human quality/security/licensing and production providers are release blockers. Do not rerun the paid validation or publish its internal draft automatically.

- User authorized login protection after M7. Add atomic account/source/global throttling and bounded KDF admission; preserve local-only mode. Formal database-backed admin provisioning/RBAC/MFA is discussed, not implemented by this change. See ADR-019 and docs/milestones/login-protection-report.md.

- User authorized full account/admin security: controlled admin provisioning, granular permissions, TOTP/recovery, session management, email-code registration/password changes and anti-bot integration. Four-digit email code explicitly requested; real SMTP/Turnstile validation awaits credentials. Native local only, no public deployment.

- Account/admin security increment completed locally: 396 pytest + 11 browser flows, 123 schemas, migrations0013_security/0014_email. See docs/milestones/account-security-report.md. Normal demo admin token disabled; SMTP local preview and Turnstile off pending credentials. Real administrator initialization/MFA binding belongs to user; browser acceptance uses only isolated _test DB and .local/e2e key. No public deployment, real charging or email approval implied.

- User authorized registration/login UX fixes: visible password toggle, field errors/focus, proof gating, on-demand Turnstile and risk-triggered login verification. Completed:396pytest+18browser flows. See docs/milestones/auth-flow-review.md. Real SMTP/Turnstile remain configured; regression uses explicit dummy env credentials and local-preview transport, no real external calls.

- User selected latest consumer design option2 and authorized full user frontend reconstruction, public industry/report sharing, personal collections, conversational entry and light motion; admin UI deferred. Completed locally:415pytest+20browser flows,135schemas,95mypy source files; see docs/milestones/consumer-front-report.md, ADR-021 and design-qa.md. Conversation replies currently deterministic scoping, and generation reuses existing DEMO first-report workflow. User will provide forecast/research rules later; do not claim or enable unrestricted live conversational research/new forecast rules automatically. Normal SMTP/Turnstile configuration stays intact; acceptance uses isolated _test DB/local-preview and no external calls.

- User explicitly authorized optional age/gender, selectable country with manually entered province/state, expanded granular industries and clearer prediction-Agent positioning. Profile v2 complete:23 primary/259 secondary product-owned options,258 CLDR regions,137schemas,96mypy files,420pytest+21browser flows. See ADR-022 and docs/milestones/profile-v2-report.md. Keep demographics encrypted and out of research snapshots/prediction/recommendation until separately specified; preserve all v1 industry pairs and legacy region text. Homepage states realtime listening as a goal and labels current demo/live capability accurately; no live periodic provider calls were enabled.

- User authorized public-content terminology, owned public-industry copies and multi-industry settings, authenticated public report download, database-backed likes/bookmarks/author inbox, packaged consumer controls and system/light/dark themes. Completed locally: 427 pytest + 22 browser flows, 141 schemas, 97 mypy files; see ADR-023 and docs/milestones/consumer-social-report.md, migration0017_social. Tracking and email switches persist intentions only and show waiting_rules; user will supply real scraping/prediction/reminder rules later. Do not start new external providers or mail based on these intentions. Preserve normal SMTP/Turnstile configuration; regression remains isolated _test/local-preview without external calls.

- User requested technology display name “互联网与信息技术” and two child options “产品经理” / “UI设计师”. Product taxonomy v2.1 now has 23 parents / 261 children; migration0018_tech_roles appends both codes, retaining immutable historical lookup rows and old profile codes. Renamed unclear not_applicable display to “暂不按职业分类（学生／退休等）” with explanation. Completed 427 pytest + 22 browser flows and production build; see docs/milestones/taxonomy-roles-report.md and ADR-022 addendum.

- User requested prominent homepage chat entry. Moved homepage research composer directly after product positioning and before industry/report discovery, added lightweight AI marker/card/text CTA and mobile layout; industry-detail composer position unchanged. Completed 427 pytest + 22 browser flows and production build. See docs/milestones/home-chat-priority-report.md. No new research/provider/mail behavior.

- User requested public report reading/bookmark counts, floating capsule navigation and concise homepage copy. Completed 429 pytest + 22 browser flows, 142 schemas, 97 mypy files and production build; migration0019_reads. Public read POST is browser/report/Shanghai-day deduplicated; short-lived per-report/day UUID hashes plus durable aggregates, no account/IP link. GET/list/download do not count reads. See ADR-024 and docs/milestones/floating-nav-read-counts-report.md. Preserve local-only provider/mail boundaries and regression isolation.
