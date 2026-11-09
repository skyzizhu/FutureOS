export interface paths {
    "/api/v1/health/live": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Live */
        get: operations["live_api_v1_health_live_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/health/ready": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Ready */
        get: operations["ready_api_v1_health_ready_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/me": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Me */
        get: operations["me_api_v1_me_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/demo/research": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Demo Research */
        post: operations["demo_research_api_v1_demo_research_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/jobs/{job_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Get Job */
        get: operations["get_job_api_v1_jobs__job_id__get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/admin/overview": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Overview */
        get: operations["overview_api_v1_admin_overview_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/admin/sources/ingest": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Ingest */
        post: operations["ingest_api_v1_admin_sources_ingest_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/admin/sources": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Sources */
        get: operations["sources_api_v1_admin_sources_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/admin/sources/{source_version_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Source */
        get: operations["source_api_v1_admin_sources__source_version_id__get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/admin/evidence": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Claims */
        get: operations["claims_api_v1_admin_evidence_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/admin/indicators": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Indicators */
        get: operations["indicators_api_v1_admin_indicators_get"];
        put?: never;
        /** Indicator */
        post: operations["indicator_api_v1_admin_indicators_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/admin/indicators/{indicator_id}/observations": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Observation */
        post: operations["observation_api_v1_admin_indicators__indicator_id__observations_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/admin/indicators/{indicator_id}/series": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Series */
        get: operations["series_api_v1_admin_indicators__indicator_id__series_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/admin/signals": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Signals */
        get: operations["signals_api_v1_admin_signals_get"];
        put?: never;
        /** Signal */
        post: operations["signal_api_v1_admin_signals_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/admin/historical-cases": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Historical Cases */
        get: operations["historical_cases_api_v1_admin_historical_cases_get"];
        put?: never;
        /** Historical Case */
        post: operations["historical_case_api_v1_admin_historical_cases_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/admin/historical-cases/{case_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Historical View */
        get: operations["historical_view_api_v1_admin_historical_cases__case_id__get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/admin/web-access": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Web Access */
        get: operations["web_access_api_v1_admin_web_access_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/admin/sources/search": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Web Search */
        post: operations["web_search_api_v1_admin_sources_search_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/admin/sources/fetch": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Web Fetch */
        post: operations["web_fetch_api_v1_admin_sources_fetch_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/admin/research/config": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Settings */
        get: operations["settings_api_v1_admin_research_config_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/admin/research/demo-inputs": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Demo */
        post: operations["demo_api_v1_admin_research_demo_inputs_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/admin/research/submit": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Submit */
        post: operations["submit_api_v1_admin_research_submit_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/admin/research/runs": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Runs */
        get: operations["runs_api_v1_admin_research_runs_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/admin/research/runs/{run_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Run */
        get: operations["run_api_v1_admin_research_runs__run_id__get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/admin/research/runs/{run_id}/inputs": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Inputs */
        get: operations["inputs_api_v1_admin_research_runs__run_id__inputs_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/admin/research/runs/{run_id}/replay": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Replay */
        post: operations["replay_api_v1_admin_research_runs__run_id__replay_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/admin/research/model-calls": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Model Calls */
        get: operations["model_calls_api_v1_admin_research_model_calls_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/admin/review/drafts": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Drafts */
        get: operations["drafts_api_v1_admin_review_drafts_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/admin/review/drafts/{draft_id}/check": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Check */
        post: operations["check_api_v1_admin_review_drafts__draft_id__check_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/admin/review/runs": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Runs */
        get: operations["runs_api_v1_admin_review_runs_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/admin/review/runs/{review_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Run */
        get: operations["run_api_v1_admin_review_runs__review_id__get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/admin/review/drafts/{draft_id}/revise": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Revise */
        post: operations["revise_api_v1_admin_review_drafts__draft_id__revise_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/admin/review/drafts/{draft_id}/revision": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Revision */
        get: operations["revision_api_v1_admin_review_drafts__draft_id__revision_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/admin/review/drafts/{draft_id}/publish": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Publish */
        post: operations["publish_api_v1_admin_review_drafts__draft_id__publish_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/admin/review/versions": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Versions */
        get: operations["versions_api_v1_admin_review_versions_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/admin/review/versions/{version_id}/register": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Register */
        post: operations["register_api_v1_admin_review_versions__version_id__register_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/admin/review/protocols/{protocol_id}/resolve": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Resolution */
        post: operations["resolution_api_v1_admin_review_protocols__protocol_id__resolve_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/admin/review/scoreboard": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Scoreboard */
        get: operations["scoreboard_api_v1_admin_review_scoreboard_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/auth/config": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Auth Config */
        get: operations["auth_config_api_v1_auth_config_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/auth/email-code": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Email Code */
        post: operations["email_code_api_v1_auth_email_code_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/auth/password-reset": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Reset Password */
        post: operations["reset_password_api_v1_auth_password_reset_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/me/sessions": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Sessions */
        get: operations["sessions_api_v1_me_sessions_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/me/sessions/{identifier}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post?: never;
        /** Revoke */
        delete: operations["revoke_api_v1_me_sessions__identifier__delete"];
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/me/sessions/revoke-all": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Revoke All */
        post: operations["revoke_all_api_v1_me_sessions_revoke_all_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/admin-auth/bootstrap": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Bootstrap */
        post: operations["bootstrap_api_v1_admin_auth_bootstrap_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/admin-auth/login": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Admin Login */
        post: operations["admin_login_api_v1_admin_auth_login_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/admin-auth/enroll": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Enroll */
        post: operations["enroll_api_v1_admin_auth_enroll_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/admin-auth/verify": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Verify */
        post: operations["verify_api_v1_admin_auth_verify_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/admin-auth/step-up": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Step Up */
        post: operations["step_up_api_v1_admin_auth_step_up_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/admin-auth/recovery-codes": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Rotate */
        post: operations["rotate_api_v1_admin_auth_recovery_codes_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/admin-auth/logout": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Admin Logout */
        post: operations["admin_logout_api_v1_admin_auth_logout_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/admin/security/admins": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Admins */
        get: operations["admins_api_v1_admin_security_admins_get"];
        put?: never;
        /** Create Admin */
        post: operations["create_admin_api_v1_admin_security_admins_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/admin/security/admins/{target}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        /** Change Admin */
        put: operations["change_admin_api_v1_admin_security_admins__target__put"];
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/admin/security/admins/{target}/reset-mfa": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Reset Mfa */
        post: operations["reset_mfa_api_v1_admin_security_admins__target__reset_mfa_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/admin/security/audit": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Audits */
        get: operations["audits_api_v1_admin_security_audit_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/auth/register": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Register */
        post: operations["register_api_v1_auth_register_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/auth/login": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Login */
        post: operations["login_api_v1_auth_login_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/auth/logout": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Logout */
        post: operations["logout_api_v1_auth_logout_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/auth/identity": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Who */
        get: operations["who_api_v1_auth_identity_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/taxonomies/industries": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Taxonomy */
        get: operations["taxonomy_api_v1_taxonomies_industries_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/taxonomies/countries": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Countries */
        get: operations["countries_api_v1_taxonomies_countries_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/me/profile": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Profile */
        get: operations["profile_api_v1_me_profile_get"];
        /** Save */
        put: operations["save_api_v1_me_profile_put"];
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/me/profile/snapshots": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Snapshot */
        post: operations["snapshot_api_v1_me_profile_snapshots_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/me/profile/snapshots/{snapshot_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Snapshot View */
        get: operations["snapshot_view_api_v1_me_profile_snapshots__snapshot_id__get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/me/entitlements": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Entitlement */
        get: operations["entitlement_api_v1_me_entitlements_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/me/export": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Export */
        get: operations["export_api_v1_me_export_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/me/data": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post?: never;
        /** Erase */
        delete: operations["erase_api_v1_me_data_delete"];
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/research/intake": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Intake */
        post: operations["intake_api_v1_research_intake_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/research/requests": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Requests */
        get: operations["requests_api_v1_research_requests_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/research/first-report": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** First */
        post: operations["first_api_v1_research_first_report_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/research/jobs/{job_id}/cancel": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Cancel */
        post: operations["cancel_api_v1_research_jobs__job_id__cancel_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/reports": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Reports */
        get: operations["reports_api_v1_reports_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/reports/{report_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Report */
        get: operations["report_api_v1_reports__report_id__get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/reports/{report_id}/versions": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Versions */
        get: operations["versions_api_v1_reports__report_id__versions_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/reports/{report_id}/versions/{version_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Report Version */
        get: operations["report_version_api_v1_reports__report_id__versions__version_id__get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/recommendations": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Recommendations */
        get: operations["recommendations_api_v1_recommendations_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/recommendations/{recommendation_id}/feedback": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Feedback */
        post: operations["feedback_api_v1_recommendations__recommendation_id__feedback_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/reports/{report_id}/email-preview": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Preview */
        get: operations["preview_api_v1_reports__report_id__email_preview_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/reports/{report_id}/email": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Email */
        post: operations["email_api_v1_reports__report_id__email_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/forecasts": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Forecasts */
        get: operations["forecasts_api_v1_forecasts_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/forecasts/versions/{version_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Forecast */
        get: operations["forecast_api_v1_forecasts_versions__version_id__get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/forecasts/{forecast_id}/versions": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Forecast Versions */
        get: operations["forecast_versions_api_v1_forecasts__forecast_id__versions_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/forecasts/{forecast_id}/versions/{version_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Exact Forecast */
        get: operations["exact_forecast_api_v1_forecasts__forecast_id__versions__version_id__get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/community/industries": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Industries */
        get: operations["industries_api_v1_community_industries_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/community/industries/{identifier}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Industry */
        get: operations["industry_api_v1_community_industries__identifier__get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/community/reports": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Reports */
        get: operations["reports_api_v1_community_reports_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/community/reports/{identifier}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Public Report */
        get: operations["public_report_api_v1_community_reports__identifier__get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/community/reports/{identifier}/read": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Record Read */
        post: operations["record_read_api_v1_community_reports__identifier__read_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/me/preferences": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Preference */
        get: operations["preference_api_v1_me_preferences_get"];
        /** Save Preference */
        put: operations["save_preference_api_v1_me_preferences_put"];
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/me/community/industries/{identifier}/add": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        /** Copy Industry */
        put: operations["copy_industry_api_v1_me_community_industries__identifier__add_put"];
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/me/community/industries/{identifier}/tracking": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Tracking */
        get: operations["tracking_api_v1_me_community_industries__identifier__tracking_get"];
        /** Save Tracking */
        put: operations["save_tracking_api_v1_me_community_industries__identifier__tracking_put"];
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/me/community/reports/{identifier}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Personal Report */
        get: operations["personal_report_api_v1_me_community_reports__identifier__get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/me/community/reports/{identifier}/like": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        /** Like */
        put: operations["like_api_v1_me_community_reports__identifier__like_put"];
        post?: never;
        /** Unlike */
        delete: operations["unlike_api_v1_me_community_reports__identifier__like_delete"];
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/me/community/reports/{identifier}/download": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Download */
        get: operations["download_api_v1_me_community_reports__identifier__download_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/me/community/notifications": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Activities */
        get: operations["activities_api_v1_me_community_notifications_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/me/community/notifications/{identifier}/read": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Read Activity */
        post: operations["read_activity_api_v1_me_community_notifications__identifier__read_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/me/community/industries": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Mine */
        get: operations["mine_api_v1_me_community_industries_get"];
        put?: never;
        /** Create */
        post: operations["create_api_v1_me_community_industries_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/me/community/industries/{identifier}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Mine Detail */
        get: operations["mine_detail_api_v1_me_community_industries__identifier__get"];
        /** Edit */
        put: operations["edit_api_v1_me_community_industries__identifier__put"];
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/me/community/industries/{identifier}/visibility": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        /** Visibility */
        put: operations["visibility_api_v1_me_community_industries__identifier__visibility_put"];
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/me/community/industries/{identifier}/membership": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        /** Add */
        put: operations["add_api_v1_me_community_industries__identifier__membership_put"];
        post?: never;
        /** Remove */
        delete: operations["remove_api_v1_me_community_industries__identifier__membership_delete"];
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/me/community/feed": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Feed */
        get: operations["feed_api_v1_me_community_feed_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/me/community/publications": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Publications */
        get: operations["publications_api_v1_me_community_publications_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/me/community/bookmarks": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Bookmarks */
        get: operations["bookmarks_api_v1_me_community_bookmarks_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/me/community/reports/{identifier}/bookmark": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        /** Save */
        put: operations["save_api_v1_me_community_reports__identifier__bookmark_put"];
        post?: never;
        /** Unsave */
        delete: operations["unsave_api_v1_me_community_reports__identifier__bookmark_delete"];
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/me/community/reports/{identifier}/preview": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Preview */
        post: operations["preview_api_v1_me_community_reports__identifier__preview_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/me/community/reports/{identifier}/publish": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Publish */
        post: operations["publish_api_v1_me_community_reports__identifier__publish_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/me/community/publications/{identifier}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post?: never;
        /** Withdraw */
        delete: operations["withdraw_api_v1_me_community_publications__identifier__delete"];
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/me/community/private-reports": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Private Links */
        get: operations["private_links_api_v1_me_community_private_reports_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/me/community/private-reports/{identifier}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        /** File Private */
        put: operations["file_private_api_v1_me_community_private_reports__identifier__put"];
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/me/conversations": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Conversations */
        get: operations["conversations_api_v1_me_conversations_get"];
        put?: never;
        /** Conversation */
        post: operations["conversation_api_v1_me_conversations_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/me/chat-capabilities": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Chat Capabilities */
        get: operations["chat_capabilities_api_v1_me_chat_capabilities_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/me/conversations/{identifier}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Read Conversation */
        get: operations["read_conversation_api_v1_me_conversations__identifier__get"];
        put?: never;
        post?: never;
        /** Delete Conversation */
        delete: operations["delete_conversation_api_v1_me_conversations__identifier__delete"];
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/me/conversations/{identifier}/messages": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Message */
        post: operations["message_api_v1_me_conversations__identifier__messages_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/me/conversations/{identifier}/start": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Start */
        post: operations["start_api_v1_me_conversations__identifier__start_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/me/conversations/{identifier}/industries/{proposal_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Confirm Industry */
        post: operations["confirm_industry_api_v1_me_conversations__identifier__industries__proposal_id__post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/me/conversations/{identifier}/industry-research": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** List Industry Research */
        get: operations["list_industry_research_api_v1_me_conversations__identifier__industry_research_get"];
        put?: never;
        /** Start Industry Research */
        post: operations["start_industry_research_api_v1_me_conversations__identifier__industry_research_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/me/conversations/{identifier}/industry-research/{job_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Read Industry Research */
        get: operations["read_industry_research_api_v1_me_conversations__identifier__industry_research__job_id__get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/me/conversations/{identifier}/industry-research/{job_id}/cancel": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Cancel Industry Research */
        post: operations["cancel_industry_research_api_v1_me_conversations__identifier__industry_research__job_id__cancel_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/admin/monitor/forecasts": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Forecasts */
        get: operations["forecasts_api_v1_admin_monitor_forecasts_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/admin/monitor/forecasts/{forecast_id}/policy": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        /** Policy */
        put: operations["policy_api_v1_admin_monitor_forecasts__forecast_id__policy_put"];
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/admin/monitor/forecasts/{forecast_id}/check": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Check */
        post: operations["check_api_v1_admin_monitor_forecasts__forecast_id__check_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/admin/monitor/runs": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Runs */
        get: operations["runs_api_v1_admin_monitor_runs_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/admin/monitor/forecasts/{forecast_id}/demo-change": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Demo */
        post: operations["demo_api_v1_admin_monitor_forecasts__forecast_id__demo_change_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/me/notification-preferences": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Prefs */
        get: operations["prefs_api_v1_me_notification_preferences_get"];
        /** Save */
        put: operations["save_api_v1_me_notification_preferences_put"];
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/notifications": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Notifications */
        get: operations["notifications_api_v1_notifications_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/notifications/{notification_id}/read": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Read */
        post: operations["read_api_v1_notifications__notification_id__read_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/reports/{report_id}/refresh": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Refresh */
        post: operations["refresh_api_v1_reports__report_id__refresh_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/reports/{report_id}/deliver": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Deliver */
        post: operations["deliver_api_v1_reports__report_id__deliver_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/me/mail-deliveries": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Deliveries */
        get: operations["deliveries_api_v1_me_mail_deliveries_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/me/mail-deliveries/{delivery_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Local Mail */
        get: operations["local_mail_api_v1_me_mail_deliveries__delivery_id__get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/mail/unsubscribe": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Optout */
        post: operations["optout_api_v1_mail_unsubscribe_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/mail/bounce": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Bounce */
        post: operations["bounce_api_v1_mail_bounce_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/billing/status": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Status */
        get: operations["status_api_v1_billing_status_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/billing/plans": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Catalog */
        get: operations["catalog_api_v1_billing_plans_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/billing/balance": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Balance */
        get: operations["balance_api_v1_billing_balance_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/billing/checkout": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Checkout */
        post: operations["checkout_api_v1_billing_checkout_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/billing/checkouts/{checkout_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** View */
        get: operations["view_api_v1_billing_checkouts__checkout_id__get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/billing/checkouts/{checkout_id}/confirm": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Confirm */
        post: operations["confirm_api_v1_billing_checkouts__checkout_id__confirm_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/billing/checkouts/{checkout_id}/refund": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Refund */
        post: operations["refund_api_v1_billing_checkouts__checkout_id__refund_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/billing/webhook": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Webhook */
        post: operations["webhook_api_v1_billing_webhook_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/billing/history": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** History */
        get: operations["history_api_v1_billing_history_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/billing/subscriptions/{subscription_id}/cancel": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Cancel Subscription */
        post: operations["cancel_subscription_api_v1_billing_subscriptions__subscription_id__cancel_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/research/quote": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Quote */
        post: operations["quote_api_v1_research_quote_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/research/submit": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Submit */
        post: operations["submit_api_v1_research_submit_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/research/paid-jobs/{job_id}/cancel": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Cancel Job */
        post: operations["cancel_job_api_v1_research_paid_jobs__job_id__cancel_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/research/topics": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Topics */
        get: operations["topics_api_v1_research_topics_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/research/topics/{topic_id}/schedule": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Schedule */
        post: operations["schedule_api_v1_research_topics__topic_id__schedule_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/research/topics/{topic_id}/pause": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Pause */
        post: operations["pause_api_v1_research_topics__topic_id__pause_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/admin/costs": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Costs */
        get: operations["costs_api_v1_admin_costs_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/admin/readiness": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Snapshot */
        get: operations["snapshot_api_v1_admin_readiness_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
}
export type webhooks = Record<string, never>;
export interface components {
    schemas: {
        /** AccountIdentityV1 */
        AccountIdentityV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * User Id
             * Format: uuid
             */
            user_id: string;
            /**
             * Role
             * @enum {string}
             */
            role: "user" | "admin";
            /** Email Masked */
            email_masked: string;
            /**
             * Email Verified
             * @default false
             */
            email_verified: boolean;
        };
        /** AccountSessionV1 */
        AccountSessionV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /** Access Token */
            access_token: string;
            /**
             * Expires At
             * Format: date-time
             */
            expires_at: string;
            identity: components["schemas"]["AccountIdentityV1"];
        };
        /** AdminAccessChangeV1 */
        AdminAccessChangeV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Permission Group
             * @enum {string}
             */
            permission_group: "owner" | "reviewer" | "operator" | "viewer";
            /**
             * Enabled
             * @default true
             */
            enabled: boolean;
        };
        /** AdminBootstrapV1 */
        AdminBootstrapV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /** Email */
            email: string;
            /** Password */
            password: string;
            /** Bootstrap Token */
            bootstrap_token: string;
        };
        /** AdminChallengeV1 */
        AdminChallengeV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /** Challenge Token */
            challenge_token: string;
            /**
             * Stage
             * @enum {string}
             */
            stage: "enroll" | "verify";
            /**
             * Expires In
             * @default 300
             */
            expires_in: number;
            /** Secret */
            secret?: string | null;
            /** Provisioning Uri */
            provisioning_uri?: string | null;
        };
        /** AdminCreateV1 */
        AdminCreateV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /** Email */
            email: string;
            /** Password */
            password: string;
            /**
             * Permission Group
             * @enum {string}
             */
            permission_group: "owner" | "reviewer" | "operator" | "viewer";
        };
        /** AdminSecondFactorV1 */
        AdminSecondFactorV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /** Challenge Token */
            challenge_token: string;
            /** Code */
            code: string;
        };
        /** AdminSessionV1 */
        AdminSessionV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /** Access Token */
            access_token: string;
            /**
             * Expires At
             * Format: date-time
             */
            expires_at: string;
            identity: components["schemas"]["AccountIdentityV1"];
            /**
             * Recovery Codes
             * @default []
             */
            recovery_codes: string[];
        };
        /** AdminStepUpV1 */
        AdminStepUpV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /** Code */
            code: string;
        };
        /** AnalogyAssessmentV1 */
        AnalogyAssessmentV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Case Id
             * Format: uuid
             */
            case_id: string;
            /** Mechanism Overlap */
            mechanism_overlap: string[];
            /** Similarities */
            similarities: string[];
            /** Key Differences */
            key_differences: string[];
            /** Non Transferable */
            non_transferable: string[];
            /** Known Outcomes */
            known_outcomes: components["schemas"]["HistoricalEventImportV1"][];
            /** Limitations */
            limitations: string[];
        };
        /** AuthConfigurationV1 */
        AuthConfigurationV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Email Code Length
             * @default 4
             * @constant
             */
            email_code_length: 4;
            /**
             * Email Transport
             * @enum {string}
             */
            email_transport: "local_preview" | "smtp" | "disabled";
            /** Turnstile Enabled */
            turnstile_enabled: boolean;
            /** Turnstile Site Key */
            turnstile_site_key: string;
            /** Demo Admin Enabled */
            demo_admin_enabled: boolean;
        };
        /** BaselineV1 */
        BaselineV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Method
             * @enum {string}
             */
            method: "last_value" | "not_applicable";
            /** Sample Count */
            sample_count: number;
            /** Observation Ids */
            observation_ids: string[];
            /** Last Observed Value */
            last_observed_value?: number | null;
            /** Projected Value */
            projected_value?: number | null;
            /** Unit */
            unit?: string | null;
            /** Limitations */
            limitations: string[];
        };
        /** ChangeAssertionV1 */
        ChangeAssertionV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Kind
             * @enum {string}
             */
            kind: "critical_assumption_broken" | "resolution_source_revised" | "new_bottleneck_removed" | "material_new_counterevidence";
            /** Claim Ids */
            claim_ids: string[];
            /** Prior Claim Id */
            prior_claim_id?: string | null;
            /** Verification Note */
            verification_note: string;
        };
        /** ChatResearchStageViewV1 */
        ChatResearchStageViewV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Stage
             * @enum {string}
             */
            stage: "search" | "analysis" | "report";
            /**
             * Started At
             * Format: date-time
             */
            started_at: string;
        };
        /** ChatResearchStartV1 */
        ChatResearchStartV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Client Id
             * Format: uuid
             */
            client_id: string;
            /**
             * Industry Id
             * Format: uuid
             */
            industry_id: string;
            /**
             * Horizon Days
             * @default 180
             */
            horizon_days: number;
            /**
             * Confirm Demo
             * @constant
             */
            confirm_demo: true;
        };
        /** ChatResearchViewV1 */
        ChatResearchViewV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Id
             * Format: uuid
             */
            id: string;
            /** Industry */
            industry: string;
            /** Horizon Days */
            horizon_days: number;
            status: components["schemas"]["JobStatus"];
            /** Stages */
            stages: components["schemas"]["ChatResearchStageViewV1"][];
            /** Error Code */
            error_code: string | null;
            /**
             * Created At
             * Format: date-time
             */
            created_at: string;
            result?: components["schemas"]["IndustryResearchRunV1"] | null;
        };
        /** CheckoutRequestV1 */
        CheckoutRequestV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /** Plan Code */
            plan_code: string;
            /**
             * Explicit Sandbox Consent
             * @constant
             */
            explicit_sandbox_consent: true;
        };
        /** ClaimImportV1 */
        ClaimImportV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /** Claim Text */
            claim_text: string;
            /** Quote */
            quote: string;
            /** Source Locator */
            source_locator: string;
            /**
             * Relation
             * @enum {string}
             */
            relation: "supports" | "contradicts" | "context";
            /**
             * Claim Kind
             * @enum {string}
             */
            claim_kind: "fact" | "opinion" | "hypothesis";
            /**
             * Verification Status
             * @default unverified
             * @enum {string}
             */
            verification_status: "unverified" | "verified";
            /**
             * Verification Note
             * @default
             */
            verification_note: string;
            /** Scope */
            scope: string;
            /**
             * Caveat
             * @default
             */
            caveat: string;
        };
        /** CommunityActivityV1 */
        CommunityActivityV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Id
             * Format: uuid
             */
            id: string;
            /**
             * Publication Id
             * Format: uuid
             */
            publication_id: string;
            /**
             * Kind
             * @enum {string}
             */
            kind: "like" | "bookmark";
            /** Title */
            title: string;
            /** Summary */
            summary: string;
            /**
             * Created At
             * Format: date-time
             */
            created_at: string;
            /** Read */
            read: boolean;
        };
        /** CommunityIndustryInputV1 */
        CommunityIndustryInputV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /** Name */
            name: string;
            /** Description */
            description: string;
            /**
             * Domain
             * @enum {string}
             */
            domain: "technology" | "energy" | "healthcare" | "manufacturing" | "education" | "finance" | "services" | "society";
        };
        /** CommunityIndustryViewV1 */
        CommunityIndustryViewV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Id
             * Format: uuid
             */
            id: string;
            /** Name */
            name: string;
            /** Description */
            description: string;
            /** Domain */
            domain: string;
            /** Public */
            public: boolean;
            /**
             * Owned
             * @default false
             */
            owned: boolean;
            /**
             * Added
             * @default false
             */
            added: boolean;
            /** Personal Industry Id */
            personal_industry_id?: string | null;
            /** Source Industry Id */
            source_industry_id?: string | null;
        };
        /** CommunityPublishV1 */
        CommunityPublishV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /** Industry Id */
            industry_id: string | null;
            /**
             * Report Version Id
             * Format: uuid
             */
            report_version_id: string;
            /**
             * Confirm Public
             * @constant
             */
            confirm_public: true;
        };
        /** CommunityReadInputV1 */
        CommunityReadInputV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Visitor Id
             * Format: uuid
             */
            visitor_id: string;
        };
        /** CommunityReportViewV1 */
        CommunityReportViewV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Id
             * Format: uuid
             */
            id: string;
            /** Industry Id */
            industry_id: string | null;
            /** Industry Name */
            industry_name: string;
            /** Title */
            title: string;
            /** Summary */
            summary: string;
            /**
             * Label
             * @enum {string}
             */
            label: "DEMO" | "REAL";
            /** Sample */
            sample: boolean;
            /** Image */
            image: string;
            /** Sections */
            sections: components["schemas"]["CommunitySectionV1"][];
            /**
             * Created At
             * Format: date-time
             */
            created_at: string;
            /** Author */
            author: string;
            /**
             * Reason
             * @default
             */
            reason: string;
            /**
             * Views Count
             * @default 0
             */
            views_count: number;
            /**
             * Likes Count
             * @default 0
             */
            likes_count: number;
            /**
             * Bookmarks Count
             * @default 0
             */
            bookmarks_count: number;
            /**
             * Liked
             * @default false
             */
            liked: boolean;
            /**
             * Saved
             * @default false
             */
            saved: boolean;
            /** Saved Industry Id */
            saved_industry_id?: string | null;
            /**
             * Owned
             * @default false
             */
            owned: boolean;
            /**
             * Public
             * @default true
             */
            public: boolean;
        };
        /** CommunitySaveReportV1 */
        CommunitySaveReportV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Industry Id
             * Format: uuid
             */
            industry_id: string;
        };
        /** CommunitySectionV1 */
        CommunitySectionV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /** Heading */
            heading: string;
            /** Text */
            text: string;
        };
        /** CommunityVisibilityV1 */
        CommunityVisibilityV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /** Public */
            public: boolean;
        };
        /** ConsumerPreferenceV1 */
        ConsumerPreferenceV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Theme
             * @default system
             * @enum {string}
             */
            theme: "system" | "light" | "dark";
        };
        /** ConversationCapabilitiesV1 */
        ConversationCapabilitiesV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /** Model Available */
            model_available: boolean;
        };
        /** ConversationCreateV1 */
        ConversationCreateV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /** Industry Id */
            industry_id?: string | null;
            /** Question */
            question: string;
            /**
             * Client Id
             * Format: uuid
             */
            client_id: string;
            /**
             * Use Model
             * @default false
             */
            use_model: boolean;
            /**
             * Include Memory
             * @default false
             */
            include_memory: boolean;
        };
        /** ConversationIndustryProposalV1 */
        ConversationIndustryProposalV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Id
             * Format: uuid
             */
            id: string;
            /** Name */
            name: string;
            /**
             * Status
             * @enum {string}
             */
            status: "pending" | "added" | "already_exists";
            /** Industry Id */
            industry_id?: string | null;
        };
        /** ConversationMessageV1 */
        ConversationMessageV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /** Text */
            text: string;
            /**
             * Client Id
             * Format: uuid
             */
            client_id: string;
            /**
             * Use Model
             * @default false
             */
            use_model: boolean;
            /**
             * Include Memory
             * @default false
             */
            include_memory: boolean;
        };
        /** ConversationMessageViewV1 */
        ConversationMessageViewV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Role
             * @enum {string}
             */
            role: "user" | "assistant";
            /** Text */
            text: string;
            /** Client Id */
            client_id?: string | null;
            /** Source */
            source?: ("local" | "llm") | null;
            proposal?: components["schemas"]["ConversationIndustryProposalV1"] | null;
        };
        /** ConversationStartV1 */
        ConversationStartV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Confirm Demo Reuse
             * @constant
             */
            confirm_demo_reuse: true;
        };
        /** ConversationViewV1 */
        ConversationViewV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Id
             * Format: uuid
             */
            id: string;
            /** Industry Id */
            industry_id: string | null;
            /** Title */
            title: string;
            /**
             * Created At
             * Format: date-time
             */
            created_at: string;
            /** Messages */
            messages: components["schemas"]["ConversationMessageViewV1"][];
            /** Job Id */
            job_id: string | null;
            job_status: components["schemas"]["JobStatus"] | null;
            /** Error Code */
            error_code: string | null;
            /** Report Id */
            report_id: string | null;
            /**
             * Mode
             * @default demo_reuse
             * @constant
             */
            mode: "demo_reuse";
            /**
             * New Forecast Rules Pending
             * @default true
             * @constant
             */
            new_forecast_rules_pending: true;
        };
        /** CountryCatalogV1 */
        CountryCatalogV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /** Entries */
            entries: components["schemas"]["CountryOptionV1"][];
            /**
             * Source
             * @default Unicode CLDR
             * @constant
             */
            source: "Unicode CLDR";
        };
        /** CountryOptionV1 */
        CountryOptionV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /** Code */
            code: string;
            /** Label */
            label: string;
        };
        /** CriticReportV1 */
        CriticReportV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Critic Run Id
             * Format: uuid
             */
            critic_run_id: string;
            /**
             * Draft Id
             * Format: uuid
             */
            draft_id: string;
            /** Draft Hash */
            draft_hash: string;
            /** Independent Input Hash */
            independent_input_hash: string;
            /** Findings */
            findings: components["schemas"]["ReviewFindingV1"][];
            /** Checkers Completed */
            checkers_completed: string[];
            /**
             * Rules Version
             * @default m3-critic-v1
             * @constant
             */
            rules_version: "m3-critic-v1";
            /** Duration Ms */
            duration_ms: number;
            /**
             * Model Calls
             * @default 0
             * @constant
             */
            model_calls: 0;
            /** Limitations */
            limitations: string[];
        };
        /** CurrentPasswordV1 */
        CurrentPasswordV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /** Password */
            password: string;
        };
        /** DecisionValueV1 */
        DecisionValueV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Impact Id
             * Format: uuid
             */
            impact_id: string;
            /**
             * Relevance
             * @enum {string}
             */
            relevance: "low" | "medium" | "high";
            /** Impact Window */
            impact_window: string;
            /** Actionability */
            actionability: string;
            /**
             * Reversibility
             * @enum {string}
             */
            reversibility: "low" | "medium" | "high";
            /** Cost Note */
            cost_note: string;
            /**
             * Decision Priority
             * @enum {string}
             */
            decision_priority: "prepare" | "observe" | "no_action";
            /** Reasons */
            reasons: string[];
            /** Unknowns */
            unknowns: string[];
            /** Reevaluate If */
            reevaluate_if: string[];
        };
        /** DemoResearchInputV1 */
        DemoResearchInputV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /** Question */
            question: string;
        };
        /** DemoResearchResultV1 */
        DemoResearchResultV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Label
             * @default DEMO
             * @constant
             */
            label: "DEMO";
            /**
             * Kind
             * @default hypothesis
             * @constant
             */
            kind: "hypothesis";
            /** Statement */
            statement: string;
            /**
             * Research As Of
             * Format: date-time
             */
            research_as_of: string;
            /** Source Ids */
            source_ids: string[];
            /** Limitations */
            limitations: string[];
            /**
             * Model Id
             * @default mock-llm-v1
             * @constant
             */
            model_id: "mock-llm-v1";
            /** Prompt Hash */
            prompt_hash: string;
            /**
             * Cost Units
             * @default 0
             * @constant
             */
            cost_units: 0;
        };
        /**
         * DomainTag
         * @enum {string}
         */
        DomainTag: "macro_finance" | "technology" | "industry" | "workforce" | "policy" | "consumption" | "housing" | "education" | "health" | "energy" | "supply_chain" | "society";
        /** EmailAuthorizationV1 */
        EmailAuthorizationV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Explicit Consent
             * @constant
             */
            explicit_consent: true;
            /** Recipient */
            recipient: string;
        };
        /** EmailCodeRequestV1 */
        EmailCodeRequestV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /** Email */
            email: string;
            /**
             * Purpose
             * @enum {string}
             */
            purpose: "register" | "password_reset";
            /**
             * Human Token
             * @default
             */
            human_token: string;
        };
        /** EmailCodeSentV1 */
        EmailCodeSentV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Challenge Id
             * Format: uuid
             */
            challenge_id: string;
            /**
             * Expires In
             * @default 300
             */
            expires_in: number;
            /**
             * Resend After
             * @default 60
             */
            resend_after: number;
            /**
             * Delivery Mode
             * @enum {string}
             */
            delivery_mode: "local_preview" | "smtp" | "disabled";
        };
        /** EmailPreviewV1 */
        EmailPreviewV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Report Version Id
             * Format: uuid
             */
            report_version_id: string;
            /** Recipient Masked */
            recipient_masked: string;
            /** Subject */
            subject: string;
            /** Summary */
            summary: string;
            /** Private Link */
            private_link: string;
            /**
             * Transport
             * @default mock_local
             * @constant
             */
            transport: "mock_local";
            /**
             * External Delivery
             * @default false
             * @constant
             */
            external_delivery: false;
        };
        /** EmailQueueRequestV1 */
        EmailQueueRequestV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Purpose
             * @default first_report
             * @enum {string}
             */
            purpose: "first_report" | "alert" | "digest";
            /**
             * Explicit Consent
             * @constant
             */
            explicit_consent: true;
        };
        /** ErrorV1 */
        ErrorV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /** Code */
            code: string;
            /** Message */
            message: string;
            /** Request Id */
            request_id: string;
            /** Details */
            details?: {
                [key: string]: boolean | string | number;
            };
        };
        /** EvaluationProtocolV1 */
        EvaluationProtocolV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Protocol Id
             * Format: uuid
             */
            protocol_id: string;
            /**
             * Version Id
             * Format: uuid
             */
            version_id: string;
            /**
             * Mode
             * @enum {string}
             */
            mode: "synthetic" | "temporal_backtest" | "forward";
            /**
             * Label
             * @enum {string}
             */
            label: "DEMO" | "REAL";
            /**
             * Registered At
             * Format: date-time
             */
            registered_at: string;
            /**
             * As Of
             * Format: date-time
             */
            as_of: string;
            /**
             * Due At
             * Format: date-time
             */
            due_at: string;
            /** Metric Definition */
            metric_definition: string;
            /** Geography */
            geography: string;
            /** Unit */
            unit: string;
            /** Resolution Source */
            resolution_source: string;
            /**
             * Operator
             * @enum {string}
             */
            operator: "gte" | "lte" | "eq";
            /** Threshold */
            threshold: number;
            /** Point Prediction A */
            point_prediction_a?: number | null;
            /** Point Prediction B */
            point_prediction_b?: number | null;
            /** Baseline Value */
            baseline_value?: number | null;
            /** Source Snapshot Hash */
            source_snapshot_hash: string;
            /** Model Id */
            model_id: string;
            /** Prompt Hash */
            prompt_hash: string;
            /** Testset Version */
            testset_version: string;
            /**
             * Protocol Version
             * @default m3-resolution-v1
             * @constant
             */
            protocol_version: "m3-resolution-v1";
            /** Limitations */
            limitations: string[];
        };
        /** EvaluationRegisterV1 */
        EvaluationRegisterV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Mode
             * @enum {string}
             */
            mode: "synthetic" | "temporal_backtest" | "forward";
            /**
             * Operator
             * @enum {string}
             */
            operator: "gte" | "lte" | "eq";
            /** Threshold */
            threshold: number;
            /** Unit */
            unit: string;
            /**
             * Testset Version
             * @default manual-v1
             */
            testset_version: string;
        };
        /** EvidenceClaimV1 */
        EvidenceClaimV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Claim Id
             * Format: uuid
             */
            claim_id: string;
            /**
             * Source Version Id
             * Format: uuid
             */
            source_version_id: string;
            /**
             * Source Group Id
             * Format: uuid
             */
            source_group_id: string;
            /** Claim Text */
            claim_text: string;
            /** Quote */
            quote: string;
            /** Source Locator */
            source_locator: string;
            /**
             * Relation
             * @enum {string}
             */
            relation: "supports" | "contradicts" | "context";
            /**
             * Claim Kind
             * @enum {string}
             */
            claim_kind: "fact" | "opinion" | "hypothesis";
            /** Known At */
            known_at: string | null;
            /**
             * Verification Status
             * @enum {string}
             */
            verification_status: "unverified" | "verified";
            /** Verification Note */
            verification_note: string;
            /** Scope */
            scope: string;
            /** Caveat */
            caveat: string;
            /**
             * Label
             * @enum {string}
             */
            label: "DEMO" | "REAL";
        };
        /** FirstReportRequestV1 */
        FirstReportRequestV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Label
             * @default DEMO
             * @enum {string}
             */
            label: "DEMO" | "REAL";
            /**
             * Forecast Version Ids
             * @default []
             */
            forecast_version_ids: string[];
        };
        /** ForecastResolutionV1 */
        ForecastResolutionV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Resolution Id
             * Format: uuid
             */
            resolution_id: string;
            /**
             * Protocol Id
             * Format: uuid
             */
            protocol_id: string;
            /**
             * Status
             * @enum {string}
             */
            status: "not_due" | "confirmed" | "disconfirmed" | "inconclusive" | "unresolved_due_to_data";
            /**
             * Checked At
             * Format: date-time
             */
            checked_at: string;
            /** Observation Id */
            observation_id?: string | null;
            /** Observed Value */
            observed_value?: number | null;
            /** Forecast Absolute Error A */
            forecast_absolute_error_a?: number | null;
            /** Forecast Absolute Error B */
            forecast_absolute_error_b?: number | null;
            /** Baseline Absolute Error */
            baseline_absolute_error?: number | null;
            /** Reason */
            reason: string;
        };
        /** ForecastTargetV1 */
        ForecastTargetV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Target Type
             * @enum {string}
             */
            target_type: "binary" | "numeric" | "ordinal" | "milestone";
            /** Population Scope */
            population_scope: string;
            /** Geography */
            geography: string;
            /** Metric Definition */
            metric_definition: string;
            /** Direction Or Threshold */
            direction_or_threshold: string;
            /** Baseline */
            baseline: string;
            /**
             * Target Start At
             * Format: date-time
             */
            target_start_at: string;
            /**
             * Target End At
             * Format: date-time
             */
            target_end_at: string;
            /** Resolution Source */
            resolution_source: string;
            /** Resolution Rule */
            resolution_rule: string;
        };
        /** FreeReportEntitlementV1 */
        FreeReportEntitlementV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Total
             * @default 1
             * @constant
             */
            total: 1;
            /** Available */
            available: number;
            /** Reserved */
            reserved: number;
            /** Consumed */
            consumed: number;
            /**
             * Paid Research Enabled
             * @default false
             * @constant
             */
            paid_research_enabled: false;
        };
        /** HTTPValidationError */
        HTTPValidationError: {
            /** Detail */
            detail?: components["schemas"]["ValidationError"][];
        };
        /** HistoricalCaseImportV1 */
        HistoricalCaseImportV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /** Title */
            title: string;
            /**
             * Cutoff At
             * Format: date-time
             */
            cutoff_at: string;
            /** Domain Tags */
            domain_tags: components["schemas"]["DomainTag"][];
            /** Mechanism Tags */
            mechanism_tags: string[];
            /** Initial Conditions */
            initial_conditions: string;
            /** Limitations */
            limitations: string[];
            /** Events */
            events: components["schemas"]["HistoricalEventImportV1"][];
            /**
             * Label
             * @enum {string}
             */
            label: "DEMO" | "REAL";
        };
        /** HistoricalCaseViewV1 */
        HistoricalCaseViewV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Case Id
             * Format: uuid
             */
            case_id: string;
            /** Title */
            title: string;
            /**
             * Cutoff At
             * Format: date-time
             */
            cutoff_at: string;
            /**
             * As Of
             * Format: date-time
             */
            as_of: string;
            /** Domain Tags */
            domain_tags: components["schemas"]["DomainTag"][];
            /** Mechanism Tags */
            mechanism_tags: string[];
            /** Initial Conditions */
            initial_conditions: string;
            /** Limitations */
            limitations: string[];
            /** Contemporaneous */
            contemporaneous: components["schemas"]["HistoricalEventImportV1"][];
            /** Outcomes */
            outcomes: components["schemas"]["HistoricalEventImportV1"][];
            /**
             * Label
             * @enum {string}
             */
            label: "DEMO" | "REAL";
        };
        /** HistoricalEventImportV1 */
        HistoricalEventImportV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /** Text */
            text: string;
            /**
             * Known At
             * Format: date-time
             */
            known_at: string;
            /**
             * Source Version Id
             * Format: uuid
             */
            source_version_id: string;
            /**
             * Data Role
             * @enum {string}
             */
            data_role: "contemporaneous" | "outcome";
            /** Outcome Category */
            outcome_category?: ("success" | "failure" | "inconclusive") | null;
        };
        /** IndicatorDefinitionV1 */
        IndicatorDefinitionV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /** Code */
            code: string;
            /** Name */
            name: string;
            /** Provider */
            provider: string;
            /** Geo Scope */
            geo_scope: string;
            /** Unit */
            unit: string;
            /**
             * Frequency
             * @enum {string}
             */
            frequency: "day" | "week" | "month" | "quarter" | "year" | "irregular";
            /** Definition Version */
            definition_version: string;
            /**
             * Label
             * @enum {string}
             */
            label: "DEMO" | "REAL";
            /**
             * Indicator Id
             * Format: uuid
             */
            indicator_id: string;
        };
        /** IndicatorImportV1 */
        IndicatorImportV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /** Code */
            code: string;
            /** Name */
            name: string;
            /** Provider */
            provider: string;
            /** Geo Scope */
            geo_scope: string;
            /** Unit */
            unit: string;
            /**
             * Frequency
             * @enum {string}
             */
            frequency: "day" | "week" | "month" | "quarter" | "year" | "irregular";
            /** Definition Version */
            definition_version: string;
            /**
             * Label
             * @enum {string}
             */
            label: "DEMO" | "REAL";
        };
        /** IndustryActionDraftV1 */
        IndustryActionDraftV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Forecast Index
             * @description Zero-based forecast position
             */
            forecast_index: number;
            /**
             * Domain
             * @enum {string}
             */
            domain: "career" | "work" | "learning" | "spending" | "finance" | "life" | "health";
            /** Action */
            action: string;
            /** Trigger */
            trigger: string;
            /** Check After Days */
            check_after_days: number;
            /** Time Minutes */
            time_minutes: number;
            /** Success Check */
            success_check: string;
            /** Stop Condition */
            stop_condition: string;
        };
        /** IndustryAnalogyChainV1 */
        IndustryAnalogyChainV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /** Case Id */
            case_id: string;
            /** Industry */
            industry: string;
            /** Context */
            context: string;
            /** Milestones */
            milestones: components["schemas"]["IndustryAnalogyMilestoneV1"][];
            /** Mechanism */
            mechanism: string;
            /** Comparable Conditions */
            comparable_conditions: string;
            /** Key Difference */
            key_difference: string;
        };
        /** IndustryAnalogyMilestoneV1 */
        IndustryAnalogyMilestoneV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /** Period */
            period: string;
            /** Observed Change */
            observed_change: string;
            /**
             * Source Id
             * Format: uuid
             */
            source_id: string;
            /** Quote */
            quote: string;
        };
        /** IndustryEvidenceV1 */
        IndustryEvidenceV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Source Id
             * Format: uuid
             */
            source_id: string;
            /**
             * Kind
             * @enum {string}
             */
            kind: "direct" | "indicator" | "counter" | "analogy";
            /** Quote */
            quote: string;
            /** Interpretation */
            interpretation: string;
            /** Comparable Conditions */
            comparable_conditions?: string | null;
            /** Key Difference */
            key_difference?: string | null;
            /** Indicator Name */
            indicator_name?: string | null;
            /** Indicator Period */
            indicator_period?: string | null;
            /** Indicator Value */
            indicator_value?: string | null;
        };
        /** IndustryForecastDraftV1 */
        IndustryForecastDraftV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /** Statement */
            statement: string;
            /** Mechanism */
            mechanism: string;
            /** Expected Signal */
            expected_signal: string;
            /** Falsifier */
            falsifier: string;
            /** Uncertainty */
            uncertainty: string;
            /** Alternatives */
            alternatives: string[];
            /** Supporting Source Ids */
            supporting_source_ids: string[];
            /**
             * Counter Source Ids
             * @default []
             */
            counter_source_ids: string[];
            /**
             * Basis
             * @default direct
             * @enum {string}
             */
            basis: "direct" | "analogy";
            /**
             * Analogy Case Ids
             * @default []
             */
            analogy_case_ids: string[];
        };
        /** IndustryReportDraftV1 */
        IndustryReportDraftV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /** Forecasts */
            forecasts: components["schemas"]["IndustryForecastDraftV1"][];
            /** Actions */
            actions: components["schemas"]["IndustryActionDraftV1"][];
        };
        /** IndustryResearchRunV1 */
        IndustryResearchRunV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            scope: components["schemas"]["IndustryResearchScopeV1"];
            /**
             * As Of
             * Format: date-time
             */
            as_of: string;
            /**
             * Status
             * @enum {string}
             */
            status: "draft" | "evidence_limited";
            /** Searched */
            searched: components["schemas"]["IndustrySearchQueryV1"][];
            /** Sources */
            sources: components["schemas"]["IndustrySourceExcerptV1"][];
            /** Evidence */
            evidence: components["schemas"]["IndustryEvidenceV1"][];
            /**
             * Analogy Chains
             * @default []
             */
            analogy_chains: components["schemas"]["IndustryAnalogyChainV1"][];
            /** Gaps */
            gaps: string[];
            report?: components["schemas"]["IndustryReportDraftV1"] | null;
            /** Personal Actions */
            personal_actions?: components["schemas"]["IndustryActionDraftV1"][] | null;
            /** Fetch Calls */
            fetch_calls: number;
            /** Model Calls */
            model_calls: number;
            /** Provider Failures */
            provider_failures: number;
        };
        /** IndustryResearchScopeV1 */
        IndustryResearchScopeV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /** Industry */
            industry: string;
            /**
             * Region
             * @default global
             */
            region: string;
            /**
             * Horizon Days
             * @default 180
             */
            horizon_days: number;
            /**
             * Label
             * @default DEMO
             * @enum {string}
             */
            label: "DEMO" | "REAL";
        };
        /** IndustrySearchQueryV1 */
        IndustrySearchQueryV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Lane
             * @enum {string}
             */
            lane: "industry" | "market" | "policy" | "indicators" | "counter" | "analogy";
            /** Query */
            query: string;
        };
        /** IndustrySourceExcerptV1 */
        IndustrySourceExcerptV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Source Id
             * Format: uuid
             */
            source_id: string;
            /** Url */
            url: string;
            /** Title */
            title: string;
            /** Published At */
            published_at: string | null;
            /**
             * Retrieved At
             * Format: date-time
             */
            retrieved_at: string;
            /** Content Hash */
            content_hash: string;
            /** Excerpt */
            excerpt: string;
        };
        /** IndustryTrackingV1 */
        IndustryTrackingV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Monitor Enabled
             * @default true
             */
            monitor_enabled: boolean;
            /**
             * Prediction Enabled
             * @default true
             */
            prediction_enabled: boolean;
            /**
             * Email Enabled
             * @default false
             */
            email_enabled: boolean;
        };
        /** IndustryTrackingViewV1 */
        IndustryTrackingViewV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Monitor Enabled
             * @default true
             */
            monitor_enabled: boolean;
            /**
             * Prediction Enabled
             * @default true
             */
            prediction_enabled: boolean;
            /**
             * Email Enabled
             * @default false
             */
            email_enabled: boolean;
            /**
             * Industry Id
             * Format: uuid
             */
            industry_id: string;
            /**
             * Status
             * @enum {string}
             */
            status: "waiting_rules" | "paused";
        };
        /** JobAcceptedV1 */
        JobAcceptedV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Job Id
             * Format: uuid
             */
            job_id: string;
            /**
             * Request Id
             * Format: uuid
             */
            request_id: string;
        };
        /**
         * JobStatus
         * @enum {string}
         */
        JobStatus: "queued" | "running" | "succeeded" | "failed_retryable" | "failed_terminal" | "cancelled";
        /** JobV1 */
        JobV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Job Id
             * Format: uuid
             */
            job_id: string;
            /**
             * Request Id
             * Format: uuid
             */
            request_id: string;
            /**
             * Trace Id
             * Format: uuid
             */
            trace_id: string;
            status: components["schemas"]["JobStatus"];
            /** Attempts */
            attempts: number;
            /**
             * Label
             * @default DEMO
             * @enum {string}
             */
            label: "DEMO" | "REAL";
            /** Result */
            result?: components["schemas"]["DemoResearchResultV1"] | components["schemas"]["M2ResearchResultV1"] | components["schemas"]["UserReportResultV1"] | components["schemas"]["MonitorResultV1"] | components["schemas"]["MailDeliveryResultV1"] | null;
            /** Error Code */
            error_code?: string | null;
        };
        /**
         * LifecycleStage
         * @enum {string}
         */
        LifecycleStage: "emergence" | "growth" | "maturity" | "inflection" | "decline" | "unknown";
        /** LocalDeliveryV1 */
        LocalDeliveryV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Delivery Id
             * Format: uuid
             */
            delivery_id: string;
            /**
             * Report Version Id
             * Format: uuid
             */
            report_version_id: string;
            /**
             * Status
             * @default saved_locally_not_sent
             * @constant
             */
            status: "saved_locally_not_sent";
            /**
             * External Delivery
             * @default false
             * @constant
             */
            external_delivery: false;
            /**
             * Consented At
             * Format: date-time
             */
            consented_at: string;
        };
        /** LoginSessionViewV1 */
        LoginSessionViewV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Session Id
             * Format: uuid
             */
            session_id: string;
            /**
             * Kind
             * @enum {string}
             */
            kind: "user" | "admin";
            /** Device Label */
            device_label: string;
            /**
             * Created At
             * Format: date-time
             */
            created_at: string;
            /**
             * Expires At
             * Format: date-time
             */
            expires_at: string;
            /** Current */
            current: boolean;
        };
        /** M2DraftV1 */
        M2DraftV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /** Parent Version Id */
            parent_version_id?: string | null;
            /**
             * Draft Id
             * Format: uuid
             */
            draft_id: string;
            /**
             * Run Id
             * Format: uuid
             */
            run_id: string;
            /**
             * Draft Sequence
             * @default A
             * @enum {string}
             */
            draft_sequence: "A" | "B1" | "B2";
            /**
             * Status
             * @default internal_unreviewed
             * @constant
             */
            status: "internal_unreviewed";
            /**
             * Publication Allowed
             * @default false
             * @constant
             */
            publication_allowed: false;
            /**
             * Label
             * @enum {string}
             */
            label: "DEMO" | "REAL";
            /**
             * Kind
             * @enum {string}
             */
            kind: "hypothesis" | "draft_forecast";
            /** Statement */
            statement: string;
            /**
             * Research As Of
             * Format: date-time
             */
            research_as_of: string;
            lifecycle_stage: components["schemas"]["LifecycleStage"];
            target: components["schemas"]["ForecastTargetV1"] | null;
            /** Evidence Claim Ids */
            evidence_claim_ids: string[];
            /** Contradiction Claim Ids */
            contradiction_claim_ids: string[];
            /** Fusions */
            fusions: components["schemas"]["SignalFusionV1"][];
            /** Mechanism Chain */
            mechanism_chain: components["schemas"]["MechanismEdgeV1"][];
            /** Analogies */
            analogies: components["schemas"]["AnalogyAssessmentV1"][];
            /** Scenarios */
            scenarios: components["schemas"]["ScenarioV1"][];
            baseline: components["schemas"]["BaselineV1"];
            raw_narrative: components["schemas"]["ResearchNarrativeV1"];
            /** Assumptions */
            assumptions: string[];
            /** Falsification Conditions */
            falsification_conditions: string[];
            /**
             * Uncertainty State
             * @default uncalibrated
             * @constant
             */
            uncertainty_state: "uncalibrated";
            /**
             * Next Review At
             * Format: date-time
             */
            next_review_at: string;
            /** Limitations */
            limitations: string[];
            /** Downgrade Reasons */
            downgrade_reasons: string[];
            /** Input Hash */
            input_hash: string;
            /** Prompt Hash */
            prompt_hash: string;
            /** Model Id */
            model_id: string;
            /**
             * Rules Version
             * @default m2-rules-v1
             * @constant
             */
            rules_version: "m2-rules-v1";
        };
        /** M2ResearchResultV1 */
        M2ResearchResultV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Run Id
             * Format: uuid
             */
            run_id: string;
            /**
             * Draft Id
             * Format: uuid
             */
            draft_id: string;
            /**
             * Status
             * @default internal_draft_ready
             * @constant
             */
            status: "internal_draft_ready";
            /**
             * Label
             * @enum {string}
             */
            label: "DEMO" | "REAL";
            /**
             * Kind
             * @enum {string}
             */
            kind: "hypothesis" | "draft_forecast";
            /**
             * Publication Allowed
             * @default false
             * @constant
             */
            publication_allowed: false;
            /** Input Hash */
            input_hash: string;
            /** Draft Hash */
            draft_hash: string;
        };
        /** MailDeliveryResultV1 */
        MailDeliveryResultV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Delivery Id
             * Format: uuid
             */
            delivery_id: string;
            /**
             * Status
             * @enum {string}
             */
            status: "delivered_local" | "suppressed";
            /**
             * External Delivery
             * @default false
             * @constant
             */
            external_delivery: false;
        };
        /** MechanismEdgeV1 */
        MechanismEdgeV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /** From Node */
            from_node: string;
            /** To Node */
            to_node: string;
            /**
             * Relationship
             * @enum {string}
             */
            relationship: "enables" | "constrains" | "counteracts";
            /**
             * Sign
             * @enum {string}
             */
            sign: "positive" | "negative";
            /** Lag Range */
            lag_range: string;
            /** Conditions */
            conditions: string[];
            /** Evidence Claim Ids */
            evidence_claim_ids: string[];
            /** Uncertainty */
            uncertainty: string;
        };
        /** MonitorCheckRequestV1 */
        MonitorCheckRequestV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Assertions
             * @default []
             */
            assertions: components["schemas"]["ChangeAssertionV1"][];
        };
        /** MonitorPolicyV1 */
        MonitorPolicyV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Enabled
             * @default true
             */
            enabled: boolean;
            /**
             * Interval Seconds
             * @default 300
             */
            interval_seconds: number;
            /**
             * Cooldown Seconds
             * @default 21600
             */
            cooldown_seconds: number;
            /**
             * Max Daily Jobs
             * @default 12
             */
            max_daily_jobs: number;
            /**
             * Independent Groups Required
             * @default 2
             */
            independent_groups_required: number;
            /** Indicator Absolute Delta */
            indicator_absolute_delta?: number | null;
            /**
             * Consecutive Periods
             * @default 2
             */
            consecutive_periods: number;
        };
        /** MonitorResultV1 */
        MonitorResultV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Monitor Run Id
             * Format: uuid
             */
            monitor_run_id: string;
            /**
             * Forecast Id
             * Format: uuid
             */
            forecast_id: string;
            /**
             * Old Version Id
             * Format: uuid
             */
            old_version_id: string;
            /** New Version Id */
            new_version_id?: string | null;
            /**
             * Level
             * @enum {string}
             */
            level: "T0" | "T1" | "T2" | "T3";
            /**
             * Outcome
             * @enum {string}
             */
            outcome: "archived" | "observed" | "retained" | "published" | "review_blocked";
            /** Reason */
            reason: string;
            /** Changed Fields */
            changed_fields: string[];
            /** Refreshed Reports */
            refreshed_reports: number;
            /**
             * External Model Calls
             * @default 0
             * @constant
             */
            external_model_calls: 0;
        };
        /** NotificationPreferencesV1 */
        NotificationPreferencesV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * First Report Opt In
             * @default false
             */
            first_report_opt_in: boolean;
            /**
             * Alert Opt In
             * @default false
             */
            alert_opt_in: boolean;
            /**
             * Digest Opt In
             * @default false
             */
            digest_opt_in: boolean;
            /**
             * Frequency
             * @default weekly
             * @enum {string}
             */
            frequency: "daily" | "weekly";
            /**
             * Explicit Consent
             * @default false
             */
            explicit_consent: boolean;
        };
        /** ObservationImportV1 */
        ObservationImportV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Source Version Id
             * Format: uuid
             */
            source_version_id: string;
            /**
             * Period Start
             * Format: date-time
             */
            period_start: string;
            /**
             * Period End
             * Format: date-time
             */
            period_end: string;
            /** Value */
            value: number;
            /**
             * Published At
             * Format: date-time
             */
            published_at: string;
            /**
             * Available At
             * Format: date-time
             */
            available_at: string;
            /** Revision Number */
            revision_number: number;
            /**
             * Quality Flag
             * @enum {string}
             */
            quality_flag: "DEMO_DATA" | "UNVERIFIED" | "VERIFIED";
            /** Definition Note */
            definition_note: string;
        };
        /** ObservationV1 */
        ObservationV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Source Version Id
             * Format: uuid
             */
            source_version_id: string;
            /**
             * Period Start
             * Format: date-time
             */
            period_start: string;
            /**
             * Period End
             * Format: date-time
             */
            period_end: string;
            /** Value */
            value: number;
            /**
             * Published At
             * Format: date-time
             */
            published_at: string;
            /**
             * Available At
             * Format: date-time
             */
            available_at: string;
            /** Revision Number */
            revision_number: number;
            /**
             * Quality Flag
             * @enum {string}
             */
            quality_flag: "DEMO_DATA" | "UNVERIFIED" | "VERIFIED";
            /** Definition Note */
            definition_note: string;
            /**
             * Observation Id
             * Format: uuid
             */
            observation_id: string;
            /**
             * Indicator Id
             * Format: uuid
             */
            indicator_id: string;
            /**
             * Label
             * @enum {string}
             */
            label: "DEMO" | "REAL";
        };
        /** PaidResearchAcceptedV1 */
        PaidResearchAcceptedV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Action
             * @enum {string}
             */
            action: "queued" | "existing_report";
            /** Job Id */
            job_id?: string | null;
            /** Report Id */
            report_id?: string | null;
            /** User Topic Id */
            user_topic_id?: string | null;
            /** Reserved Units */
            reserved_units: number;
            /**
             * Deduplicated
             * @default false
             */
            deduplicated: boolean;
        };
        /** PaidResearchSubmitV1 */
        PaidResearchSubmitV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Quote Id
             * Format: uuid
             */
            quote_id: string;
            /**
             * Accept Usage Rules
             * @constant
             */
            accept_usage_rules: true;
        };
        /** PasswordResetV1 */
        PasswordResetV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /** Email */
            email: string;
            /** Password */
            password: string;
            /**
             * Verification Id
             * Format: uuid
             */
            verification_id: string;
            /** Code */
            code: string;
        };
        /** PeriodicResearchRequestV1 */
        PeriodicResearchRequestV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Subscription Id
             * Format: uuid
             */
            subscription_id: string;
            /**
             * Explicit Periodic Consent
             * @constant
             */
            explicit_periodic_consent: true;
        };
        /** PersonalAssessmentV1 */
        PersonalAssessmentV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Impact Id
             * Format: uuid
             */
            impact_id: string;
            /**
             * User Id
             * Format: uuid
             */
            user_id: string;
            /**
             * Profile Snapshot Id
             * Format: uuid
             */
            profile_snapshot_id: string;
            /**
             * Forecast Version Id
             * Format: uuid
             */
            forecast_version_id: string;
            /**
             * Relevance
             * @enum {string}
             */
            relevance: "low" | "medium" | "high";
            /** Mechanism Path */
            mechanism_path: string[];
            /** Relevance Reason */
            relevance_reason: string;
            /** Positive Impacts */
            positive_impacts: string[];
            /** Negative Impacts */
            negative_impacts: string[];
            /** Applicable Conditions */
            applicable_conditions: string[];
            /** Uncertainty */
            uncertainty: string;
            /** Matched Domains */
            matched_domains: string[];
            decision: components["schemas"]["DecisionValueV1"];
        };
        /** PersonalDataEraseV1 */
        PersonalDataEraseV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /** Password */
            password: string;
            /**
             * Confirmation
             * @constant
             */
            confirmation: "DELETE MY DATA";
        };
        /** PersonalDataErasedV1 */
        PersonalDataErasedV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Erasure Id
             * Format: uuid
             */
            erasure_id: string;
            /**
             * Erased At
             * Format: date-time
             */
            erased_at: string;
            /** Cleared Records */
            cleared_records: {
                [key: string]: number;
            };
            /** Retained */
            retained: string[];
            /** Backup Notice */
            backup_notice: string;
        };
        /** PrivateReportV1 */
        PrivateReportV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Report Id
             * Format: uuid
             */
            report_id: string;
            /**
             * Report Version Id
             * Format: uuid
             */
            report_version_id: string;
            /**
             * User Id
             * Format: uuid
             */
            user_id: string;
            /** Version Num */
            version_num: number;
            /**
             * Profile Snapshot Id
             * Format: uuid
             */
            profile_snapshot_id: string;
            /** Profile Revision */
            profile_revision: number;
            /**
             * Label
             * @enum {string}
             */
            label: "DEMO" | "REAL";
            /** Title */
            title: string;
            /**
             * Created At
             * Format: date-time
             */
            created_at: string;
            /** Forecast Version Ids */
            forecast_version_ids: string[];
            /** Primary Impacts */
            primary_impacts: components["schemas"]["PersonalAssessmentV1"][];
            /** Observation Only */
            observation_only: components["schemas"]["PersonalAssessmentV1"][];
            /** Recommendations */
            recommendations: components["schemas"]["RecommendationV1"][];
            /** Evidence Gaps */
            evidence_gaps: string[];
            /** Limitations */
            limitations: string[];
            /**
             * Algorithm Version
             * @default m4-personal-v1
             * @constant
             */
            algorithm_version: "m4-personal-v1";
            /** Previous Report Version Id */
            previous_report_version_id?: string | null;
            /**
             * Change Summary
             * @default []
             */
            change_summary: string[];
        };
        /** ProfileInputV1 */
        ProfileInputV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /** Industry L1 Code */
            industry_l1_code: string;
            /** Industry L2 Code */
            industry_l2_code: string;
            /**
             * Industry Detail
             * @default
             */
            industry_detail: string;
            /**
             * Occupation Text
             * @default
             */
            occupation_text: string;
            /**
             * Country Code
             * @default
             */
            country_code: string;
            /**
             * Subdivision
             * @default
             */
            subdivision: string;
            /** Gender */
            gender?: ("female" | "male" | "other") | null;
            /** Age */
            age?: number | null;
            /**
             * Region
             * @default
             */
            region: string;
            /**
             * Goals
             * @default []
             */
            goals: string[];
            /**
             * Tasks
             * @default []
             */
            tasks: string[];
            /** Available Minutes Per Week */
            available_minutes_per_week?: number | null;
            /**
             * Allow Low Cost Experiments
             * @default false
             */
            allow_low_cost_experiments: boolean;
            /**
             * Use Optional Fields
             * @default false
             */
            use_optional_fields: boolean;
            /**
             * Locale
             * @default zh-CN
             * @enum {string}
             */
            locale: "zh-CN" | "en";
            /**
             * Timezone
             * @default Asia/Shanghai
             * @enum {string}
             */
            timezone: "Asia/Shanghai" | "UTC";
        };
        /** ProfileSnapshotV1 */
        ProfileSnapshotV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Snapshot Id
             * Format: uuid
             */
            snapshot_id: string;
            /**
             * User Id
             * Format: uuid
             */
            user_id: string;
            profile: components["schemas"]["ProfileInputV1"];
            /** Profile Revision */
            profile_revision: number;
            /**
             * Consent Scope
             * @enum {string}
             */
            consent_scope: "industry_only" | "optional_fields";
            /**
             * Created At
             * Format: date-time
             */
            created_at: string;
            /** Snapshot Hash */
            snapshot_hash: string;
        };
        /** ProfileViewV1 */
        ProfileViewV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * User Id
             * Format: uuid
             */
            user_id: string;
            profile: components["schemas"]["ProfileInputV1"];
            /** Revision */
            revision: number;
            /**
             * Updated At
             * Format: date-time
             */
            updated_at: string;
            /** Taxonomy Version */
            taxonomy_version: string;
        };
        /** ProtectedLoginV1 */
        ProtectedLoginV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /** Email */
            email: string;
            /** Password */
            password: string;
            /**
             * Human Token
             * @default
             */
            human_token: string;
        };
        /** PublishRequestV1 */
        PublishRequestV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Review Id
             * Format: uuid
             */
            review_id: string;
            /** Change Reason */
            change_reason: string;
        };
        /** PublishedForecastV1 */
        PublishedForecastV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Version Id
             * Format: uuid
             */
            version_id: string;
            /**
             * Forecast Id
             * Format: uuid
             */
            forecast_id: string;
            /** Version Num */
            version_num: number;
            /**
             * Draft Id
             * Format: uuid
             */
            draft_id: string;
            /**
             * Review Id
             * Format: uuid
             */
            review_id: string;
            /**
             * Label
             * @enum {string}
             */
            label: "DEMO" | "REAL";
            /**
             * Published At
             * Format: date-time
             */
            published_at: string;
            /** Version Hash */
            version_hash: string;
            /** Change Reason */
            change_reason: string;
            body: components["schemas"]["M2DraftV1"];
        };
        /** RecommendationFeedbackV1 */
        RecommendationFeedbackV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Status
             * @enum {string}
             */
            status: "helpful" | "not_applicable" | "taken" | "hide";
        };
        /** RecommendationV1 */
        RecommendationV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Recommendation Id
             * Format: uuid
             */
            recommendation_id: string;
            /**
             * Impact Id
             * Format: uuid
             */
            impact_id: string;
            /** Action */
            action: string;
            /** Rationale */
            rationale: string;
            /** Forecast Version Ids */
            forecast_version_ids: string[];
            /** Applicability */
            applicability: string;
            /**
             * Suggested Start
             * Format: date-time
             */
            suggested_start: string;
            /**
             * Review Date
             * Format: date-time
             */
            review_date: string;
            /** Estimated Effort And Cost */
            estimated_effort_and_cost: string;
            /** Tradeoffs */
            tradeoffs: string;
            /** Alternatives */
            alternatives: string[];
            /** Success Metrics */
            success_metrics: string[];
            /** Stop Or Revisit Condition */
            stop_or_revisit_condition: string;
            /**
             * Priority
             * @enum {string}
             */
            priority: "prepare" | "observe" | "no_action";
            /** Personalization Assumptions */
            personalization_assumptions: string[];
            /** Suppressed High Risk Actions */
            suppressed_high_risk_actions: string[];
        };
        /** ReplayResultV1 */
        ReplayResultV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Run Id
             * Format: uuid
             */
            run_id: string;
            /** Identical */
            identical: boolean;
            /** Input Hash */
            input_hash: string;
            /** Original Draft Hash */
            original_draft_hash: string;
            /** Replay Draft Hash */
            replay_draft_hash: string;
            /**
             * Network Calls
             * @default 0
             * @constant
             */
            network_calls: 0;
        };
        /** ReportSummaryV1 */
        ReportSummaryV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Report Id
             * Format: uuid
             */
            report_id: string;
            /**
             * Report Version Id
             * Format: uuid
             */
            report_version_id: string;
            /** Version Num */
            version_num: number;
            /** Title */
            title: string;
            /**
             * Label
             * @enum {string}
             */
            label: "DEMO" | "REAL";
            /**
             * Created At
             * Format: date-time
             */
            created_at: string;
        };
        /** ResearchAcceptedV1 */
        ResearchAcceptedV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Job Id
             * Format: uuid
             */
            job_id: string;
            /**
             * Request Id
             * Format: uuid
             */
            request_id: string;
            /**
             * Run Id
             * Format: uuid
             */
            run_id: string;
        };
        /** ResearchIntakeResultV1 */
        ResearchIntakeResultV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /** Scope */
            scope: string;
            /** Matched Version Ids */
            matched_version_ids: string[];
            /** Available Free Reports */
            available_free_reports: number;
            /** Additional Questions */
            additional_questions: string[];
            /** Limitations */
            limitations: string[];
        };
        /** ResearchIntakeV1 */
        ResearchIntakeV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Question
             * @default
             */
            question: string;
            /**
             * Label
             * @default DEMO
             * @enum {string}
             */
            label: "DEMO" | "REAL";
        };
        /** ResearchNarrativeV1 */
        ResearchNarrativeV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /** Hypothesis */
            hypothesis: string;
            /** Enabling Conditions */
            enabling_conditions: string[];
            /** Bottlenecks */
            bottlenecks: string[];
            /** Opposing Explanations */
            opposing_explanations: string[];
            /** Next Observable Signals */
            next_observable_signals: string[];
            /** Falsification Conditions */
            falsification_conditions: string[];
            /** Cited Claim Ids */
            cited_claim_ids: string[];
        };
        /** ResearchQuoteV1 */
        ResearchQuoteV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Quote Id
             * Format: uuid
             */
            quote_id: string;
            scope: components["schemas"]["ResearchScopeV1"];
            /** Scope Fingerprint */
            scope_fingerprint: string;
            /**
             * Kind
             * @enum {string}
             */
            kind: "new_topic" | "existing_topic";
            /** Units Required */
            units_required: number;
            /** Existing Report Id */
            existing_report_id: string | null;
            /**
             * Expires At
             * Format: date-time
             */
            expires_at: string;
            /** Rules */
            rules: string[];
        };
        /** ResearchRunViewV1 */
        ResearchRunViewV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Run Id
             * Format: uuid
             */
            run_id: string;
            /**
             * Topic Id
             * Format: uuid
             */
            topic_id: string;
            /**
             * Job Id
             * Format: uuid
             */
            job_id: string;
            /** Title */
            title: string;
            status: components["schemas"]["JobStatus"];
            /**
             * Research As Of
             * Format: date-time
             */
            research_as_of: string;
            /** Input Hash */
            input_hash: string;
            /** Engine Code Hash */
            engine_code_hash: string;
            /**
             * Provider
             * @enum {string}
             */
            provider: "mock" | "deepseek" | "incremental";
            /** Model Id */
            model_id: string;
            /**
             * Label
             * @enum {string}
             */
            label: "DEMO" | "REAL";
            draft: components["schemas"]["M2DraftV1"] | null;
            /** Draft Hash */
            draft_hash: string | null;
            /** Error Code */
            error_code: string | null;
        };
        /** ResearchScopeV1 */
        ResearchScopeV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Domain
             * @enum {string}
             */
            domain: "technology" | "manufacturing" | "healthcare" | "education" | "finance" | "services" | "logistics" | "energy" | "society";
            /**
             * Focus
             * @enum {string}
             */
            focus: "workflow_adoption" | "integration_constraints";
            /**
             * Population
             * @enum {string}
             */
            population: "small_teams" | "large_organizations";
            /**
             * Geography
             * @default global
             * @enum {string}
             */
            geography: "global" | "CN";
            /**
             * Label
             * @default DEMO
             * @enum {string}
             */
            label: "DEMO" | "REAL";
        };
        /** ResearchSnapshotV1 */
        ResearchSnapshotV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            request: components["schemas"]["ResearchSubmitV1"];
            /** Signals */
            signals: components["schemas"]["SignalV1"][];
            /** Claims */
            claims: components["schemas"]["EvidenceClaimV1"][];
            /** Sources */
            sources: components["schemas"]["SourceVersionV1"][];
            /** Cases */
            cases: components["schemas"]["HistoricalCaseViewV1"][];
            indicator?: components["schemas"]["IndicatorDefinitionV1"] | null;
            /**
             * Observations
             * @default []
             */
            observations: components["schemas"]["ObservationV1"][];
            /** Engine Code Hash */
            engine_code_hash: string;
            /**
             * Rules Version
             * @default m2-rules-v1
             * @constant
             */
            rules_version: "m2-rules-v1";
        };
        /** ResearchSubmitV1 */
        ResearchSubmitV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /** Title */
            title: string;
            /** Scope */
            scope: string;
            /** Domain Tags */
            domain_tags: components["schemas"]["DomainTag"][];
            /**
             * Research As Of
             * Format: date-time
             */
            research_as_of: string;
            /** Signal Ids */
            signal_ids: string[];
            /**
             * Historical Case Ids
             * @default []
             */
            historical_case_ids: string[];
            /** Indicator Id */
            indicator_id?: string | null;
            target?: components["schemas"]["ForecastTargetV1"] | null;
            /** @default unknown */
            lifecycle_stage: components["schemas"]["LifecycleStage"];
            /**
             * Recipe Id
             * @default verifiable_agent
             * @enum {string}
             */
            recipe_id: "verifiable_agent" | "technology_diffusion";
            /**
             * Provider
             * @default mock
             * @enum {string}
             */
            provider: "mock" | "deepseek";
            /**
             * Label
             * @enum {string}
             */
            label: "DEMO" | "REAL";
        };
        /** ResolveRequestV1 */
        ResolveRequestV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /** Observation Id */
            observation_id?: string | null;
            /** Unavailable Reason */
            unavailable_reason?: string | null;
        };
        /** ReviewDecisionV1 */
        ReviewDecisionV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Decision Id
             * Format: uuid
             */
            decision_id: string;
            /**
             * Critic Run Id
             * Format: uuid
             */
            critic_run_id: string;
            /**
             * Draft Id
             * Format: uuid
             */
            draft_id: string;
            /**
             * Decision
             * @enum {string}
             */
            decision: "accept" | "annotate" | "targeted_research" | "block" | "research_only";
            /** Publication Allowed */
            publication_allowed: boolean;
            /** Verified Finding Ids */
            verified_finding_ids: string[];
            /**
             * Rule Version
             * @default m3-adjudication-v1
             * @constant
             */
            rule_version: "m3-adjudication-v1";
            /** Rationale */
            rationale: string;
            /**
             * Decided At
             * Format: date-time
             */
            decided_at: string;
        };
        /** ReviewFindingV1 */
        ReviewFindingV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Finding Id
             * Format: uuid
             */
            finding_id: string;
            /**
             * Checker
             * @enum {string}
             */
            checker: "evidence" | "historical" | "causal" | "scenario" | "temporal_resolution";
            /** Code */
            code: string;
            /**
             * Severity
             * @enum {string}
             */
            severity: "L0" | "L1" | "L2" | "L3";
            /** Statement */
            statement: string;
            /**
             * Verification Status
             * @enum {string}
             */
            verification_status: "verified" | "pending" | "refuted";
            /**
             * Source Refs
             * @default []
             */
            source_refs: string[];
            /** Affected Fields */
            affected_fields: string[];
            /** Recommended Action */
            recommended_action: string;
        };
        /** ReviewViewV1 */
        ReviewViewV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            report: components["schemas"]["CriticReportV1"];
            decision: components["schemas"]["ReviewDecisionV1"];
        };
        /** RevisionRequestV1 */
        RevisionRequestV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Review Id
             * Format: uuid
             */
            review_id: string;
            /** Confirmed Finding Ids */
            confirmed_finding_ids: string[];
            /**
             * Additional Case Ids
             * @default []
             */
            additional_case_ids: string[];
        };
        /** RevisionViewV1 */
        RevisionViewV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Draft Id
             * Format: uuid
             */
            draft_id: string;
            /**
             * Parent Draft Id
             * Format: uuid
             */
            parent_draft_id: string;
            /**
             * Draft Sequence
             * @enum {string}
             */
            draft_sequence: "B1" | "B2";
            /** Input Hash */
            input_hash: string;
            /** Draft Hash */
            draft_hash: string;
            /** Changes */
            changes: {
                [key: string]: unknown;
            };
            body: components["schemas"]["M2DraftV1"];
        };
        /** SandboxConsentV1 */
        SandboxConsentV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Explicit Sandbox Consent
             * @constant
             */
            explicit_sandbox_consent: true;
        };
        /** ScenarioV1 */
        ScenarioV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Scenario Id
             * Format: uuid
             */
            scenario_id: string;
            /**
             * Kind
             * @default scenario
             * @constant
             */
            kind: "scenario";
            /**
             * Path
             * @enum {string}
             */
            path: "base" | "acceleration" | "friction";
            /** Statement */
            statement: string;
            /** Conditions */
            conditions: string[];
            /** Observable Signals */
            observable_signals: string[];
            /** Falsification Conditions */
            falsification_conditions: string[];
        };
        /**
         * SearchHitV1
         * @description Unverified provider output, separate from ingested/verified SourceV1 evidence.
         */
        SearchHitV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Hit Id
             * Format: uuid
             */
            hit_id: string;
            /**
             * Provider
             * @enum {string}
             */
            provider: "mock" | "deepseek";
            /** Url */
            url: string;
            /** Title */
            title: string;
            /** Snippet */
            snippet: string;
            /** Summary */
            summary: string;
            /** Content */
            content: string;
            /** Site Name */
            site_name?: string | null;
            /** Published At */
            published_at: string | null;
            /**
             * Retrieved At
             * Format: date-time
             */
            retrieved_at: string;
            /** Provider Rank Score */
            provider_rank_score?: number | null;
            /** Provider Authority */
            provider_authority?: number | null;
            /**
             * Evidence Status
             * @default unverified
             * @constant
             */
            evidence_status: "unverified";
            /**
             * Label
             * @enum {string}
             */
            label: "DEMO" | "REAL";
        };
        /** SignalFusionV1 */
        SignalFusionV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Fusion Id
             * Format: uuid
             */
            fusion_id: string;
            /** Signal Ids */
            signal_ids: string[];
            /** Independent Source Groups */
            independent_source_groups: number;
            /** Mechanism */
            mechanism: string;
            /** Remaining Bottlenecks */
            remaining_bottlenecks: string[];
            /** Emergent Hypotheses */
            emergent_hypotheses: string[];
            /** Opposing Explanations */
            opposing_explanations: string[];
            /** Next Observable Signals */
            next_observable_signals: string[];
            stage: components["schemas"]["LifecycleStage"];
            /**
             * Status
             * @default hypothesis
             * @constant
             */
            status: "hypothesis";
        };
        /** SignalImportV1 */
        SignalImportV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /** Headline */
            headline: string;
            /** Claim Ids */
            claim_ids: string[];
            /** @default unknown */
            lifecycle_stage: components["schemas"]["LifecycleStage"];
            /**
             * Mechanism Tags
             * @default []
             */
            mechanism_tags: string[];
            /** Domain Tags */
            domain_tags: components["schemas"]["DomainTag"][];
        };
        /** SignalV1 */
        SignalV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Signal Id
             * Format: uuid
             */
            signal_id: string;
            /**
             * Kind
             * @default signal
             * @constant
             */
            kind: "signal";
            /**
             * Status
             * @default candidate
             * @constant
             */
            status: "candidate";
            /** Headline */
            headline: string;
            lifecycle_stage: components["schemas"]["LifecycleStage"];
            /** Claim Ids */
            claim_ids: string[];
            /** Source Group Ids */
            source_group_ids: string[];
            /** Independent Source Count */
            independent_source_count: number;
            /** Mechanism Tags */
            mechanism_tags: string[];
            /** Domain Tags */
            domain_tags: components["schemas"]["DomainTag"][];
            /**
             * Detected At
             * Format: date-time
             */
            detected_at: string;
            /**
             * Label
             * @enum {string}
             */
            label: "DEMO" | "REAL";
        };
        /** SourceImportV1 */
        SourceImportV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /** Url */
            url: string;
            /** Title */
            title: string;
            /** Publisher */
            publisher: string;
            /**
             * Source Type
             * @enum {string}
             */
            source_type: "official" | "paper" | "licensed_data" | "news" | "community" | "manual";
            /**
             * Original Language
             * @default zh
             */
            original_language: string;
            /**
             * Region
             * @default unspecified
             */
            region: string;
            /** Published At */
            published_at?: string | null;
            /** Event At */
            event_at?: string | null;
            /** Available At */
            available_at?: string | null;
            /**
             * Availability Basis
             * @enum {string}
             */
            availability_basis: "observed_now" | "verified_archive" | "verified_release" | "unknown";
            /**
             * Availability Note
             * @default
             */
            availability_note: string;
            /** Revised At */
            revised_at?: string | null;
            /**
             * Content
             * @default
             */
            content: string;
            /**
             * Usage Permission
             * @enum {string}
             */
            usage_permission: "metadata_only" | "excerpt" | "authorized_full";
            /** License Note */
            license_note: string;
            /**
             * Access Method
             * @default manual
             * @enum {string}
             */
            access_method: "manual" | "deepseek" | "archive" | "licensed_api";
            /** Reliability Note */
            reliability_note: string;
            /** Original Source Url */
            original_source_url?: string | null;
            /** Domain Tags */
            domain_tags: components["schemas"]["DomainTag"][];
            /**
             * Claims
             * @default []
             */
            claims: components["schemas"]["ClaimImportV1"][];
            /**
             * Label
             * @enum {string}
             */
            label: "DEMO" | "REAL";
        };
        /** SourceIngestedV1 */
        SourceIngestedV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            version: components["schemas"]["SourceVersionV1"];
            /** Claim Ids */
            claim_ids: string[];
            /** Duplicate */
            duplicate: boolean;
        };
        /** SourceVersionV1 */
        SourceVersionV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Source Version Id
             * Format: uuid
             */
            source_version_id: string;
            /**
             * Source Id
             * Format: uuid
             */
            source_id: string;
            /**
             * Source Group Id
             * Format: uuid
             */
            source_group_id: string;
            /** Source Type */
            source_type: string;
            /** Original Language */
            original_language: string;
            /** Region */
            region: string;
            /** Dedup Method */
            dedup_method: string;
            /** Original Source Url */
            original_source_url?: string | null;
            /** Version Label */
            version_label: string;
            /** Url */
            url: string;
            /** Title */
            title: string;
            /** Publisher */
            publisher: string;
            /** Published At */
            published_at: string | null;
            /** Event At */
            event_at: string | null;
            /** Available At */
            available_at: string | null;
            /**
             * Ingested At
             * Format: date-time
             */
            ingested_at: string;
            /** Revised At */
            revised_at: string | null;
            /** Availability Basis */
            availability_basis: string;
            /** Availability Note */
            availability_note: string;
            /** Content Hash */
            content_hash: string;
            /** Content */
            content: string;
            /** Usage Permission */
            usage_permission: string;
            /** License Note */
            license_note: string;
            /** Access Method */
            access_method: string;
            /** Reliability Note */
            reliability_note: string;
            /** Domain Tags */
            domain_tags: components["schemas"]["DomainTag"][];
            /**
             * Label
             * @enum {string}
             */
            label: "DEMO" | "REAL";
        };
        /** UserReportResultV1 */
        UserReportResultV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /**
             * Report Id
             * Format: uuid
             */
            report_id: string;
            /**
             * Report Version Id
             * Format: uuid
             */
            report_version_id: string;
            /**
             * Label
             * @enum {string}
             */
            label: "DEMO" | "REAL";
            /**
             * Status
             * @default private_report_ready
             * @constant
             */
            status: "private_report_ready";
        };
        /** ValidationError */
        ValidationError: {
            /** Location */
            loc: (string | number)[];
            /** Message */
            msg: string;
            /** Error Type */
            type: string;
            /** Input */
            input?: unknown;
            /** Context */
            ctx?: Record<string, never>;
        };
        /** VerifiedRegistrationV1 */
        VerifiedRegistrationV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /** Email */
            email: string;
            /** Password */
            password: string;
            /**
             * Verification Id
             * Format: uuid
             */
            verification_id: string;
            /** Code */
            code: string;
        };
        /** WebFetchPreviewV1 */
        WebFetchPreviewV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /** Url */
            url: string;
            /** Title */
            title: string;
            /** Excerpt */
            excerpt: string;
            /** Full Content Hash */
            full_content_hash: string;
            /**
             * Retrieved At
             * Format: date-time
             */
            retrieved_at: string;
            /** Published At */
            published_at?: null;
            /**
             * Label
             * @default REAL
             * @constant
             */
            label: "REAL";
            /**
             * Evidence Status
             * @default unverified
             * @constant
             */
            evidence_status: "unverified";
            /** Retained Characters */
            retained_characters: number;
        };
        /** WebFetchRequestV1 */
        WebFetchRequestV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /** Url */
            url: string;
        };
        /** WebSearchRequestV1 */
        WebSearchRequestV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /** Query */
            query: string;
            /**
             * Count
             * @default 5
             */
            count: number;
        };
        /** WebSearchResponseV1 */
        WebSearchResponseV1: {
            /**
             * Schema Version
             * @default 1.0
             * @constant
             */
            schema_version: "1.0";
            /** Results */
            results: components["schemas"]["SearchHitV1"][];
        };
    };
    responses: never;
    parameters: never;
    requestBodies: never;
    headers: never;
    pathItems: never;
}
export type $defs = Record<string, never>;
export interface operations {
    live_api_v1_health_live_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": {
                        [key: string]: string;
                    };
                };
            };
        };
    };
    ready_api_v1_health_ready_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Service Unavailable */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
        };
    };
    me_api_v1_me_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": {
                        [key: string]: string;
                    };
                };
            };
            /** @description Unauthorized */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Forbidden */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Not Found */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Conflict */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Unprocessable Entity */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Internal Server Error */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Service Unavailable */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
        };
    };
    demo_research_api_v1_demo_research_post: {
        parameters: {
            query?: never;
            header: {
                "idempotency-key": string;
            };
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["DemoResearchInputV1"];
            };
        };
        responses: {
            /** @description Successful Response */
            202: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["JobAcceptedV1"];
                };
            };
            /** @description Unauthorized */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Forbidden */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Not Found */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Conflict */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Unprocessable Entity */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Internal Server Error */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Service Unavailable */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
        };
    };
    get_job_api_v1_jobs__job_id__get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                job_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["JobV1"];
                };
            };
            /** @description Unauthorized */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Forbidden */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Not Found */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Conflict */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Unprocessable Entity */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Internal Server Error */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Service Unavailable */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
        };
    };
    overview_api_v1_admin_overview_get: {
        parameters: {
            query?: never;
            header: {
                authorization: string;
            };
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": {
                        [key: string]: unknown;
                    };
                };
            };
            /** @description Unauthorized */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Forbidden */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Not Found */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Conflict */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Unprocessable Entity */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Internal Server Error */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Service Unavailable */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
        };
    };
    ingest_api_v1_admin_sources_ingest_post: {
        parameters: {
            query?: never;
            header: {
                authorization: string;
            };
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["SourceImportV1"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["SourceIngestedV1"];
                };
            };
            /** @description Unauthorized */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Forbidden */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Not Found */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Conflict */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Unprocessable Entity */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Too Many Requests */
            429: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Bad Gateway */
            502: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Service Unavailable */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
        };
    };
    sources_api_v1_admin_sources_get: {
        parameters: {
            query?: {
                as_of?: string | null;
                label?: ("DEMO" | "REAL") | null;
            };
            header: {
                authorization: string;
            };
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["SourceVersionV1"][];
                };
            };
            /** @description Unauthorized */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Forbidden */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Not Found */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Conflict */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Unprocessable Entity */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Too Many Requests */
            429: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Bad Gateway */
            502: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Service Unavailable */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
        };
    };
    source_api_v1_admin_sources__source_version_id__get: {
        parameters: {
            query?: never;
            header: {
                authorization: string;
            };
            path: {
                source_version_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["SourceVersionV1"];
                };
            };
            /** @description Unauthorized */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Forbidden */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Not Found */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Conflict */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Unprocessable Entity */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Too Many Requests */
            429: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Bad Gateway */
            502: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Service Unavailable */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
        };
    };
    claims_api_v1_admin_evidence_get: {
        parameters: {
            query: {
                as_of: string;
                label?: ("DEMO" | "REAL") | null;
            };
            header: {
                authorization: string;
            };
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["EvidenceClaimV1"][];
                };
            };
            /** @description Unauthorized */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Forbidden */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Not Found */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Conflict */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Unprocessable Entity */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Too Many Requests */
            429: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Bad Gateway */
            502: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Service Unavailable */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
        };
    };
    indicators_api_v1_admin_indicators_get: {
        parameters: {
            query?: never;
            header: {
                authorization: string;
            };
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["IndicatorDefinitionV1"][];
                };
            };
            /** @description Unauthorized */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Forbidden */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Not Found */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Conflict */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Unprocessable Entity */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Too Many Requests */
            429: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Bad Gateway */
            502: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Service Unavailable */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
        };
    };
    indicator_api_v1_admin_indicators_post: {
        parameters: {
            query?: never;
            header: {
                authorization: string;
            };
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["IndicatorImportV1"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["IndicatorDefinitionV1"];
                };
            };
            /** @description Unauthorized */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Forbidden */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Not Found */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Conflict */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Unprocessable Entity */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Too Many Requests */
            429: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Bad Gateway */
            502: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Service Unavailable */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
        };
    };
    observation_api_v1_admin_indicators__indicator_id__observations_post: {
        parameters: {
            query?: never;
            header: {
                authorization: string;
            };
            path: {
                indicator_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ObservationImportV1"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ObservationV1"];
                };
            };
            /** @description Unauthorized */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Forbidden */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Not Found */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Conflict */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Unprocessable Entity */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Too Many Requests */
            429: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Bad Gateway */
            502: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Service Unavailable */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
        };
    };
    series_api_v1_admin_indicators__indicator_id__series_get: {
        parameters: {
            query: {
                as_of: string;
                start?: string | null;
                end?: string | null;
            };
            header: {
                authorization: string;
            };
            path: {
                indicator_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ObservationV1"][];
                };
            };
            /** @description Unauthorized */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Forbidden */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Not Found */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Conflict */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Unprocessable Entity */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Too Many Requests */
            429: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Bad Gateway */
            502: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Service Unavailable */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
        };
    };
    signals_api_v1_admin_signals_get: {
        parameters: {
            query?: {
                as_of?: string | null;
                label?: ("DEMO" | "REAL") | null;
            };
            header: {
                authorization: string;
            };
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["SignalV1"][];
                };
            };
            /** @description Unauthorized */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Forbidden */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Not Found */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Conflict */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Unprocessable Entity */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Too Many Requests */
            429: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Bad Gateway */
            502: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Service Unavailable */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
        };
    };
    signal_api_v1_admin_signals_post: {
        parameters: {
            query?: never;
            header: {
                authorization: string;
            };
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["SignalImportV1"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["SignalV1"];
                };
            };
            /** @description Unauthorized */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Forbidden */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Not Found */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Conflict */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Unprocessable Entity */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Too Many Requests */
            429: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Bad Gateway */
            502: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Service Unavailable */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
        };
    };
    historical_cases_api_v1_admin_historical_cases_get: {
        parameters: {
            query?: never;
            header: {
                authorization: string;
            };
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Unauthorized */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Forbidden */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Not Found */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Conflict */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Unprocessable Entity */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Too Many Requests */
            429: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Bad Gateway */
            502: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Service Unavailable */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
        };
    };
    historical_case_api_v1_admin_historical_cases_post: {
        parameters: {
            query?: never;
            header: {
                authorization: string;
            };
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["HistoricalCaseImportV1"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": {
                        [key: string]: string;
                    };
                };
            };
            /** @description Unauthorized */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Forbidden */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Not Found */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Conflict */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Unprocessable Entity */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Too Many Requests */
            429: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Bad Gateway */
            502: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Service Unavailable */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
        };
    };
    historical_view_api_v1_admin_historical_cases__case_id__get: {
        parameters: {
            query: {
                as_of: string;
            };
            header: {
                authorization: string;
            };
            path: {
                case_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HistoricalCaseViewV1"];
                };
            };
            /** @description Unauthorized */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Forbidden */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Not Found */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Conflict */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Unprocessable Entity */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Too Many Requests */
            429: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Bad Gateway */
            502: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Service Unavailable */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
        };
    };
    web_access_api_v1_admin_web_access_get: {
        parameters: {
            query?: never;
            header: {
                authorization: string;
            };
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Unauthorized */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Forbidden */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Not Found */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Conflict */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Unprocessable Entity */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Too Many Requests */
            429: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Bad Gateway */
            502: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Service Unavailable */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
        };
    };
    web_search_api_v1_admin_sources_search_post: {
        parameters: {
            query?: never;
            header: {
                authorization: string;
            };
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["WebSearchRequestV1"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["WebSearchResponseV1"];
                };
            };
            /** @description Unauthorized */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Forbidden */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Not Found */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Conflict */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Unprocessable Entity */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Too Many Requests */
            429: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Bad Gateway */
            502: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Service Unavailable */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
        };
    };
    web_fetch_api_v1_admin_sources_fetch_post: {
        parameters: {
            query?: never;
            header: {
                authorization: string;
            };
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["WebFetchRequestV1"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["WebFetchPreviewV1"];
                };
            };
            /** @description Unauthorized */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Forbidden */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Not Found */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Conflict */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Unprocessable Entity */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Too Many Requests */
            429: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Bad Gateway */
            502: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Service Unavailable */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
        };
    };
    settings_api_v1_admin_research_config_get: {
        parameters: {
            query?: never;
            header: {
                authorization: string;
            };
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": {
                        [key: string]: unknown;
                    };
                };
            };
            /** @description Unauthorized */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Forbidden */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Not Found */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Conflict */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Unprocessable Entity */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Service Unavailable */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
        };
    };
    demo_api_v1_admin_research_demo_inputs_post: {
        parameters: {
            query?: never;
            header: {
                authorization: string;
            };
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ResearchSubmitV1"];
                };
            };
            /** @description Unauthorized */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Forbidden */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Not Found */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Conflict */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Unprocessable Entity */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Service Unavailable */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
        };
    };
    submit_api_v1_admin_research_submit_post: {
        parameters: {
            query?: never;
            header: {
                "idempotency-key": string;
                authorization: string;
            };
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ResearchSubmitV1"];
            };
        };
        responses: {
            /** @description Successful Response */
            202: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ResearchAcceptedV1"];
                };
            };
            /** @description Unauthorized */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Forbidden */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Not Found */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Conflict */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Unprocessable Entity */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Service Unavailable */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
        };
    };
    runs_api_v1_admin_research_runs_get: {
        parameters: {
            query?: never;
            header: {
                authorization: string;
            };
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ResearchRunViewV1"][];
                };
            };
            /** @description Unauthorized */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Forbidden */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Not Found */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Conflict */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Unprocessable Entity */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Service Unavailable */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
        };
    };
    run_api_v1_admin_research_runs__run_id__get: {
        parameters: {
            query?: never;
            header: {
                authorization: string;
            };
            path: {
                run_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ResearchRunViewV1"];
                };
            };
            /** @description Unauthorized */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Forbidden */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Not Found */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Conflict */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Unprocessable Entity */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Service Unavailable */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
        };
    };
    inputs_api_v1_admin_research_runs__run_id__inputs_get: {
        parameters: {
            query?: never;
            header: {
                authorization: string;
            };
            path: {
                run_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ResearchSnapshotV1"];
                };
            };
            /** @description Unauthorized */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Forbidden */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Not Found */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Conflict */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Unprocessable Entity */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Service Unavailable */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
        };
    };
    replay_api_v1_admin_research_runs__run_id__replay_post: {
        parameters: {
            query?: never;
            header: {
                authorization: string;
            };
            path: {
                run_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ReplayResultV1"];
                };
            };
            /** @description Unauthorized */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Forbidden */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Not Found */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Conflict */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Unprocessable Entity */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Service Unavailable */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
        };
    };
    model_calls_api_v1_admin_research_model_calls_get: {
        parameters: {
            query?: never;
            header: {
                authorization: string;
            };
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Unauthorized */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Forbidden */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Not Found */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Conflict */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Unprocessable Entity */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
            /** @description Service Unavailable */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorV1"];
                };
            };
        };
    };
    drafts_api_v1_admin_review_drafts_get: {
        parameters: {
            query?: never;
            header: {
                authorization: string;
            };
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    check_api_v1_admin_review_drafts__draft_id__check_post: {
        parameters: {
            query?: never;
            header: {
                authorization: string;
            };
            path: {
                draft_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ReviewViewV1"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    runs_api_v1_admin_review_runs_get: {
        parameters: {
            query?: never;
            header: {
                authorization: string;
            };
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    run_api_v1_admin_review_runs__review_id__get: {
        parameters: {
            query?: never;
            header: {
                authorization: string;
            };
            path: {
                review_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ReviewViewV1"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    revise_api_v1_admin_review_drafts__draft_id__revise_post: {
        parameters: {
            query?: never;
            header: {
                authorization: string;
            };
            path: {
                draft_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["RevisionRequestV1"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["RevisionViewV1"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    revision_api_v1_admin_review_drafts__draft_id__revision_get: {
        parameters: {
            query?: never;
            header: {
                authorization: string;
            };
            path: {
                draft_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["RevisionViewV1"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    publish_api_v1_admin_review_drafts__draft_id__publish_post: {
        parameters: {
            query?: never;
            header: {
                authorization: string;
            };
            path: {
                draft_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["PublishRequestV1"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["PublishedForecastV1"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    versions_api_v1_admin_review_versions_get: {
        parameters: {
            query?: never;
            header: {
                authorization: string;
            };
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["PublishedForecastV1"][];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    register_api_v1_admin_review_versions__version_id__register_post: {
        parameters: {
            query?: never;
            header: {
                authorization: string;
            };
            path: {
                version_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["EvaluationRegisterV1"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["EvaluationProtocolV1"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    resolution_api_v1_admin_review_protocols__protocol_id__resolve_post: {
        parameters: {
            query?: never;
            header: {
                authorization: string;
            };
            path: {
                protocol_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ResolveRequestV1"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ForecastResolutionV1"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    scoreboard_api_v1_admin_review_scoreboard_get: {
        parameters: {
            query?: never;
            header: {
                authorization: string;
            };
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    auth_config_api_v1_auth_config_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["AuthConfigurationV1"];
                };
            };
        };
    };
    email_code_api_v1_auth_email_code_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["EmailCodeRequestV1"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["EmailCodeSentV1"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    reset_password_api_v1_auth_password_reset_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["PasswordResetV1"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    sessions_api_v1_me_sessions_get: {
        parameters: {
            query?: never;
            header: {
                authorization: string;
            };
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["LoginSessionViewV1"][];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    revoke_api_v1_me_sessions__identifier__delete: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                identifier: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    revoke_all_api_v1_me_sessions_revoke_all_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["CurrentPasswordV1"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    bootstrap_api_v1_admin_auth_bootstrap_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["AdminBootstrapV1"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["AdminChallengeV1"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    admin_login_api_v1_admin_auth_login_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ProtectedLoginV1"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["AdminChallengeV1"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    enroll_api_v1_admin_auth_enroll_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["AdminSecondFactorV1"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["AdminSessionV1"] | components["schemas"]["AdminChallengeV1"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    verify_api_v1_admin_auth_verify_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["AdminSecondFactorV1"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["AdminSessionV1"] | components["schemas"]["AdminChallengeV1"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    step_up_api_v1_admin_auth_step_up_post: {
        parameters: {
            query?: never;
            header: {
                authorization: string;
            };
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["AdminStepUpV1"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    rotate_api_v1_admin_auth_recovery_codes_post: {
        parameters: {
            query?: never;
            header: {
                authorization: string;
            };
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["AdminStepUpV1"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    admin_logout_api_v1_admin_auth_logout_post: {
        parameters: {
            query?: never;
            header: {
                authorization: string;
            };
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    admins_api_v1_admin_security_admins_get: {
        parameters: {
            query?: never;
            header: {
                authorization: string;
            };
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    create_admin_api_v1_admin_security_admins_post: {
        parameters: {
            query?: never;
            header: {
                authorization: string;
            };
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["AdminCreateV1"];
            };
        };
        responses: {
            /** @description Successful Response */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    change_admin_api_v1_admin_security_admins__target__put: {
        parameters: {
            query?: never;
            header: {
                authorization: string;
            };
            path: {
                target: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["AdminAccessChangeV1"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    reset_mfa_api_v1_admin_security_admins__target__reset_mfa_post: {
        parameters: {
            query?: never;
            header: {
                authorization: string;
            };
            path: {
                target: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    audits_api_v1_admin_security_audit_get: {
        parameters: {
            query?: never;
            header: {
                authorization: string;
            };
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    register_api_v1_auth_register_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["VerifiedRegistrationV1"];
            };
        };
        responses: {
            /** @description Successful Response */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["AccountSessionV1"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    login_api_v1_auth_login_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ProtectedLoginV1"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["AccountSessionV1"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    logout_api_v1_auth_logout_post: {
        parameters: {
            query?: never;
            header: {
                authorization: string;
            };
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    who_api_v1_auth_identity_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["AccountIdentityV1"];
                };
            };
        };
    };
    taxonomy_api_v1_taxonomies_industries_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
        };
    };
    countries_api_v1_taxonomies_countries_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["CountryCatalogV1"];
                };
            };
        };
    };
    profile_api_v1_me_profile_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ProfileViewV1"];
                };
            };
        };
    };
    save_api_v1_me_profile_put: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ProfileInputV1"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ProfileViewV1"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    snapshot_api_v1_me_profile_snapshots_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ProfileSnapshotV1"];
                };
            };
        };
    };
    snapshot_view_api_v1_me_profile_snapshots__snapshot_id__get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                snapshot_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ProfileSnapshotV1"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    entitlement_api_v1_me_entitlements_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["FreeReportEntitlementV1"];
                };
            };
        };
    };
    export_api_v1_me_export_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
        };
    };
    erase_api_v1_me_data_delete: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["PersonalDataEraseV1"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["PersonalDataErasedV1"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    intake_api_v1_research_intake_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ResearchIntakeV1"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ResearchIntakeResultV1"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    requests_api_v1_research_requests_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
        };
    };
    first_api_v1_research_first_report_post: {
        parameters: {
            query?: never;
            header: {
                "idempotency-key": string;
            };
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["FirstReportRequestV1"];
            };
        };
        responses: {
            /** @description Successful Response */
            202: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["JobAcceptedV1"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    cancel_api_v1_research_jobs__job_id__cancel_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                job_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    reports_api_v1_reports_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ReportSummaryV1"][];
                };
            };
        };
    };
    report_api_v1_reports__report_id__get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                report_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["PrivateReportV1"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    versions_api_v1_reports__report_id__versions_get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                report_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    report_version_api_v1_reports__report_id__versions__version_id__get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                report_id: string;
                version_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["PrivateReportV1"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    recommendations_api_v1_recommendations_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
        };
    };
    feedback_api_v1_recommendations__recommendation_id__feedback_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                recommendation_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["RecommendationFeedbackV1"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    preview_api_v1_reports__report_id__email_preview_get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                report_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["EmailPreviewV1"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    email_api_v1_reports__report_id__email_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                report_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["EmailAuthorizationV1"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["LocalDeliveryV1"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    forecasts_api_v1_forecasts_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
        };
    };
    forecast_api_v1_forecasts_versions__version_id__get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                version_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    forecast_versions_api_v1_forecasts__forecast_id__versions_get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                forecast_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    exact_forecast_api_v1_forecasts__forecast_id__versions__version_id__get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                forecast_id: string;
                version_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    industries_api_v1_community_industries_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["CommunityIndustryViewV1"][];
                };
            };
        };
    };
    industry_api_v1_community_industries__identifier__get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                identifier: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["CommunityIndustryViewV1"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    reports_api_v1_community_reports_get: {
        parameters: {
            query?: {
                industry_id?: string | null;
                offset?: number;
                q?: string;
                sort?: "newest" | "oldest" | "recommended";
                standalone?: boolean;
                limit?: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["CommunityReportViewV1"][];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    public_report_api_v1_community_reports__identifier__get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                identifier: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["CommunityReportViewV1"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    record_read_api_v1_community_reports__identifier__read_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                identifier: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["CommunityReadInputV1"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["CommunityReportViewV1"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    preference_api_v1_me_preferences_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ConsumerPreferenceV1"];
                };
            };
        };
    };
    save_preference_api_v1_me_preferences_put: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ConsumerPreferenceV1"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ConsumerPreferenceV1"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    copy_industry_api_v1_me_community_industries__identifier__add_put: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                identifier: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["CommunityIndustryViewV1"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    tracking_api_v1_me_community_industries__identifier__tracking_get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                identifier: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["IndustryTrackingViewV1"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    save_tracking_api_v1_me_community_industries__identifier__tracking_put: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                identifier: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["IndustryTrackingV1"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["IndustryTrackingViewV1"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    personal_report_api_v1_me_community_reports__identifier__get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                identifier: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["CommunityReportViewV1"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    like_api_v1_me_community_reports__identifier__like_put: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                identifier: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    unlike_api_v1_me_community_reports__identifier__like_delete: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                identifier: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    download_api_v1_me_community_reports__identifier__download_get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                identifier: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    activities_api_v1_me_community_notifications_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["CommunityActivityV1"][];
                };
            };
        };
    };
    read_activity_api_v1_me_community_notifications__identifier__read_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                identifier: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    mine_api_v1_me_community_industries_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["CommunityIndustryViewV1"][];
                };
            };
        };
    };
    create_api_v1_me_community_industries_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["CommunityIndustryInputV1"];
            };
        };
        responses: {
            /** @description Successful Response */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["CommunityIndustryViewV1"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    mine_detail_api_v1_me_community_industries__identifier__get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                identifier: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["CommunityIndustryViewV1"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    edit_api_v1_me_community_industries__identifier__put: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                identifier: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["CommunityIndustryInputV1"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    visibility_api_v1_me_community_industries__identifier__visibility_put: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                identifier: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["CommunityVisibilityV1"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    add_api_v1_me_community_industries__identifier__membership_put: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                identifier: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    remove_api_v1_me_community_industries__identifier__membership_delete: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                identifier: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    feed_api_v1_me_community_feed_get: {
        parameters: {
            query?: {
                industry_id?: string | null;
                offset?: number;
                q?: string;
                sort?: "newest" | "oldest" | "recommended";
                standalone?: boolean;
                limit?: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["CommunityReportViewV1"][];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    publications_api_v1_me_community_publications_get: {
        parameters: {
            query?: {
                offset?: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["CommunityReportViewV1"][];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    bookmarks_api_v1_me_community_bookmarks_get: {
        parameters: {
            query?: {
                industry_id?: string | null;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["CommunityReportViewV1"][];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    save_api_v1_me_community_reports__identifier__bookmark_put: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                identifier: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["CommunitySaveReportV1"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    unsave_api_v1_me_community_reports__identifier__bookmark_delete: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                identifier: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    preview_api_v1_me_community_reports__identifier__preview_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                identifier: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["CommunityPublishV1"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    publish_api_v1_me_community_reports__identifier__publish_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                identifier: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["CommunityPublishV1"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["CommunityReportViewV1"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    withdraw_api_v1_me_community_publications__identifier__delete: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                identifier: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    private_links_api_v1_me_community_private_reports_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
        };
    };
    file_private_api_v1_me_community_private_reports__identifier__put: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                identifier: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["CommunitySaveReportV1"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    conversations_api_v1_me_conversations_get: {
        parameters: {
            query?: {
                industry_id?: string | null;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ConversationViewV1"][];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    conversation_api_v1_me_conversations_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ConversationCreateV1"];
            };
        };
        responses: {
            /** @description Successful Response */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ConversationViewV1"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    chat_capabilities_api_v1_me_chat_capabilities_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ConversationCapabilitiesV1"];
                };
            };
        };
    };
    read_conversation_api_v1_me_conversations__identifier__get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                identifier: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ConversationViewV1"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    delete_conversation_api_v1_me_conversations__identifier__delete: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                identifier: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    message_api_v1_me_conversations__identifier__messages_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                identifier: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ConversationMessageV1"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ConversationViewV1"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    start_api_v1_me_conversations__identifier__start_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                identifier: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ConversationStartV1"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ConversationViewV1"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    confirm_industry_api_v1_me_conversations__identifier__industries__proposal_id__post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                identifier: string;
                proposal_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ConversationViewV1"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    list_industry_research_api_v1_me_conversations__identifier__industry_research_get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                identifier: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ChatResearchViewV1"][];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    start_industry_research_api_v1_me_conversations__identifier__industry_research_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                identifier: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ChatResearchStartV1"];
            };
        };
        responses: {
            /** @description Successful Response */
            202: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ChatResearchViewV1"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    read_industry_research_api_v1_me_conversations__identifier__industry_research__job_id__get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                identifier: string;
                job_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ChatResearchViewV1"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    cancel_industry_research_api_v1_me_conversations__identifier__industry_research__job_id__cancel_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                identifier: string;
                job_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": {
                        [key: string]: boolean;
                    };
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    forecasts_api_v1_admin_monitor_forecasts_get: {
        parameters: {
            query?: never;
            header: {
                authorization: string;
            };
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    policy_api_v1_admin_monitor_forecasts__forecast_id__policy_put: {
        parameters: {
            query?: never;
            header: {
                authorization: string;
            };
            path: {
                forecast_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["MonitorPolicyV1"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    check_api_v1_admin_monitor_forecasts__forecast_id__check_post: {
        parameters: {
            query?: never;
            header: {
                authorization: string;
            };
            path: {
                forecast_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["MonitorCheckRequestV1"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    runs_api_v1_admin_monitor_runs_get: {
        parameters: {
            query?: never;
            header: {
                authorization: string;
            };
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    demo_api_v1_admin_monitor_forecasts__forecast_id__demo_change_post: {
        parameters: {
            query?: never;
            header: {
                authorization: string;
            };
            path: {
                forecast_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    prefs_api_v1_me_notification_preferences_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
        };
    };
    save_api_v1_me_notification_preferences_put: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["NotificationPreferencesV1"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    notifications_api_v1_notifications_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
        };
    };
    read_api_v1_notifications__notification_id__read_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                notification_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    refresh_api_v1_reports__report_id__refresh_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                report_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    deliver_api_v1_reports__report_id__deliver_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                report_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["EmailQueueRequestV1"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    deliveries_api_v1_me_mail_deliveries_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
        };
    };
    local_mail_api_v1_me_mail_deliveries__delivery_id__get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                delivery_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    optout_api_v1_mail_unsubscribe_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": {
                    [key: string]: string;
                };
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    bounce_api_v1_mail_bounce_post: {
        parameters: {
            query?: never;
            header?: {
                "X-Webhook-Signature"?: string;
            };
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    status_api_v1_billing_status_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
        };
    };
    catalog_api_v1_billing_plans_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
        };
    };
    balance_api_v1_billing_balance_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
        };
    };
    checkout_api_v1_billing_checkout_post: {
        parameters: {
            query?: never;
            header: {
                "Idempotency-Key": string;
            };
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["CheckoutRequestV1"];
            };
        };
        responses: {
            /** @description Successful Response */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    view_api_v1_billing_checkouts__checkout_id__get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                checkout_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    confirm_api_v1_billing_checkouts__checkout_id__confirm_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                checkout_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["SandboxConsentV1"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    refund_api_v1_billing_checkouts__checkout_id__refund_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                checkout_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["SandboxConsentV1"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    webhook_api_v1_billing_webhook_post: {
        parameters: {
            query?: never;
            header?: {
                "X-Payment-Signature"?: string;
            };
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    history_api_v1_billing_history_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
        };
    };
    cancel_subscription_api_v1_billing_subscriptions__subscription_id__cancel_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                subscription_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    quote_api_v1_research_quote_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ResearchScopeV1"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ResearchQuoteV1"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    submit_api_v1_research_submit_post: {
        parameters: {
            query?: never;
            header: {
                "Idempotency-Key": string;
            };
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["PaidResearchSubmitV1"];
            };
        };
        responses: {
            /** @description Successful Response */
            202: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["PaidResearchAcceptedV1"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    cancel_job_api_v1_research_paid_jobs__job_id__cancel_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                job_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    topics_api_v1_research_topics_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
        };
    };
    schedule_api_v1_research_topics__topic_id__schedule_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                topic_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["PeriodicResearchRequestV1"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    pause_api_v1_research_topics__topic_id__pause_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                topic_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    costs_api_v1_admin_costs_get: {
        parameters: {
            query?: never;
            header: {
                authorization: string;
            };
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    snapshot_api_v1_admin_readiness_get: {
        parameters: {
            query?: never;
            header: {
                authorization: string;
            };
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
}
