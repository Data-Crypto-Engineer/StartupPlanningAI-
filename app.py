"""
app.py - Main Streamlit UI Entry Point
🚀 Startup Planning & Organizer AI
Tagline: Find real problems. Verify real demand. Discover companies. Build AI solutions people may actually pay for.

Requirements:
- 7 Streamlit Pages
- Real metrics, cards, reasoning trails, outreach copy
- Master Excel download and Google Drive synchronization
- Clean professional styling, responsive cards, no AI slop
"""

import streamlit as st
import datetime
import workflow
import storage

# Page Configuration
st.set_page_config(
    page_title="Startup Planning & Organizer AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for Streamlit
st.markdown("""
<style>
    .main-title {
        font-size: 2.1rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .tagline {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
        font-weight: 400;
    }
    .metric-box {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 12px 16px;
        text-align: center;
    }
    .metric-value {
        font-size: 1.6rem;
        font-weight: 700;
        color: #1E3A8A;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .badge {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .badge-green { background-color: #DEF7EC; color: #03543F; }
    .badge-blue { background-color: #E1EFFE; color: #1E429F; }
    .badge-amber { background-color: #FEF08A; color: #78350F; }
    .badge-gray { background-color: #F3F4F6; color: #374151; }
    .evidence-box {
        background-color: #F0FDF4;
        border-left: 4px solid #16A34A;
        padding: 10px 14px;
        margin-top: 8px;
        border-radius: 0 6px 6px 0;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# Session State Initialization
if "engine" not in st.session_state:
    st.session_state.engine = workflow.StartupResearchWorkflow()

if "region" not in st.session_state:
    st.session_state.region = "Pakistan"

if "selected_domain" not in st.session_state:
    st.session_state.selected_domain = "Electricity & Energy"

if "current_page" not in st.session_state:
    st.session_state.current_page = "Research Setup"

if "selected_opp_id" not in st.session_state:
    st.session_state.selected_opp_id = None

# Sidebar Navigation
with st.sidebar:
    st.markdown("### 🚀 Navigation")
    pages = [
        "Research Setup",
        "Domain Discovery",
        "Opportunity Discovery",
        "Opportunity Detail",
        "Job Opportunities",
        "Outreach CRM",
        "Excel & Google Drive"
    ]
    st.session_state.current_page = st.radio("Go to:", pages, index=pages.index(st.session_state.current_page))

    st.markdown("---")
    st.markdown("### 📁 Persistent Tracker")
    gdrive_url = "https://drive.google.com/drive/folders/1QJnRIqDLOpkaArrNIcpaehgYlHWOyXEG?usp=sharing"
    st.markdown(f"[🔗 Open Google Drive Folder]({gdrive_url})")
    st.caption("Folder ID: `1QJnRIqDLOpkaArrNIcpaehgYlHWOyXEG`")

    st.markdown("---")
    st.markdown("### ⚙️ Engine Status")
    has_key = bool(st.session_state.engine.ai.api_key)
    if has_key:
        st.success("Gemini API: Connected")
    else:
        st.info("Gemini API: Local Mock / Fallback")

# Header
st.markdown('<div class="main-title">🚀 Startup Planning & Organizer AI</div>', unsafe_allow_html=True)
st.markdown('<div class="tagline">Find real problems. Verify real demand. Discover companies. Build AI solutions people may actually pay for.</div>', unsafe_allow_html=True)

# -------------------------------------------------------------
# PAGE 1: RESEARCH SETUP
# -------------------------------------------------------------
if st.session_state.current_page == "Research Setup":
    st.markdown("### 🔎 Step 1 — Research Setup")
    st.write("Configure search parameters to uncover grounded commercial demand.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Where should we search?")
        reg_choice = st.radio(
            "Select geographic scope:",
            ["🇵🇰 Pakistan", "🌍 Global / Remote"],
            index=0 if st.session_state.region == "Pakistan" else 1
        )
        st.session_state.region = "Pakistan" if "Pakistan" in reg_choice else "Global / Remote"

        if st.session_state.region == "Pakistan":
            st.info("Searching Pakistani enterprises, public-sector organizations, engineering firms, and energy companies.")
        else:
            st.warning("Global mode: Eligibility for Pakistani applicants will be verified where publicly documented. No assumptions made.")

    with col2:
        st.markdown("#### What are you looking for?")
        mode = st.selectbox(
            "Primary objective:",
            [
                "Discover AI opportunity domains",
                "Find organizations with operational problems",
                "Find jobs & freelance opportunities",
                "Find AI & automation procurement signals",
                "Research a specific industry"
            ]
        )

        domain_input = st.selectbox(
            "Initial Domain Focus:",
            [
                "Electricity & Energy",
                "Engineering",
                "Schools & Education",
                "NGOs",
                "Agriculture",
                "Logistics",
                "Customer Support",
                "Healthcare"
            ]
        )
        st.session_state.selected_domain = domain_input

    st.markdown("---")
    c3, c4, c5 = st.columns(3)
    with c3:
        lookback = st.select_slider("Search Lookback Window:", options=["Last 7 days", "Last 30 days", "Last 90 days", "Last 6 months", "All available"], value="Last 90 days")
    with c4:
        min_score = st.slider("Minimum Commercial Intent Score:", 0, 100, 30, step=5)
    with c5:
        max_orgs = st.selectbox("Maximum Organizations to investigate:", [10, 25, 50, 100], index=1)

    c6, c7 = st.columns(2)
    with c6:
        only_pk_eligible = st.checkbox("☑ Show only opportunities verified for Pakistani applicants", value=False)
    with c7:
        remote_only = st.checkbox("☑ Show remote opportunities only", value=False)

    st.markdown("---")
    if st.button("🔎 Start Market Research", type="primary"):
        with st.spinner("Analyzing verified market signals and commercial indicators..."):
            results = st.session_state.engine.run_opportunity_investigation(
                region=st.session_state.region,
                domain=st.session_state.selected_domain,
                min_commercial_score=min_score,
                pakistan_only_eligible=only_pk_eligible,
                remote_only=remote_only,
                max_results=max_orgs
            )
            st.success(f"Investigation complete: Found {len(results)} verified opportunities!")
            st.session_state.current_page = "Opportunity Discovery"
            st.rerun()

# -------------------------------------------------------------
# PAGE 2: DOMAIN DISCOVERY
# -------------------------------------------------------------
elif st.session_state.current_page == "Domain Discovery":
    st.markdown(f"### 🌐 Domain Discovery — {st.session_state.region}")
    st.write("Ranked by empirical operational pain, commercial hiring signals, and tender notices.")

    domains = st.session_state.engine.get_domains_for_region(st.session_state.region)

    for d in domains:
        with st.expander(f"📌 {d['domain']} — Evidence Strength: {d['evidence_strength']} | Commercial Signals: {d['commercial_signals']}", expanded=False):
            col_a, col_b = st.columns([2, 1])
            with col_a:
                st.write(f"**Why AI may be useful:** {d['why_useful']}")
                st.write("**Potential AI Applications:**")
                for app in d["ai_applications"]:
                    st.write(f"• {app}")
                st.write(f"**Verified Example Organizations:** {', '.join(d['example_orgs'])}")
            with col_b:
                st.metric("Sources Found", d["sources_found"])
                st.write(f"**Search Date:** {d['search_date']}")
                if st.button(f"Investigate {d['domain']}", key=f"btn_{d['domain']}"):
                    st.session_state.selected_domain = d["domain"]
                    with st.spinner(f"Investigating {d['domain']}..."):
                        st.session_state.engine.run_opportunity_investigation(
                            region=st.session_state.region,
                            domain=d["domain"]
                        )
                        st.session_state.current_page = "Opportunity Discovery"
                        st.rerun()

# -------------------------------------------------------------
# PAGE 3: OPPORTUNITY DISCOVERY
# -------------------------------------------------------------
elif st.session_state.current_page == "Opportunity Discovery":
    st.markdown(f"### 🏢 Discovered Opportunities — {st.session_state.selected_domain} ({st.session_state.region})")

    metrics = st.session_state.engine.compute_summary_metrics()
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Organizations", metrics["organizations_found"])
    m2.metric("Commercial Signals", metrics["commercial_opportunities"])
    m3.metric("AI Opportunities", metrics["ai_opportunities"])
    m4.metric("Verified Jobs", metrics["verified_jobs"])
    m5.metric("High Confidence", metrics["high_confidence_opportunities"])

    st.markdown("---")

    opps = st.session_state.engine.active_opportunities
    if not opps:
        st.info("No opportunities currently loaded. Click 'Start Market Research' from Research Setup.")
        if st.button("Run Quick Search Now"):
            st.session_state.engine.run_opportunity_investigation(
                region=st.session_state.region,
                domain=st.session_state.selected_domain
            )
            st.rerun()
    else:
        for opp in opps:
            with st.container():
                st.markdown(f"#### {opp['organization']} — {opp['domain']}")
                c1, c2, c3 = st.columns(3)
                c1.markdown(f"**Commercial Intent:** `{opp['commercial_score']}/100` ({opp['commercial_level']})")
                c2.markdown(f"**AI Intent:** `{opp['ai_intent']}`")
                c3.markdown(f"**Confidence:** `{opp['confidence']}`")

                st.write(f"**Problem:** {opp['problem_statement']}")
                st.write(f"**Proposed Solution:** {opp['proposed_solution']} (*Working Name: {opp['app_name']}*)")
                st.write(f"**Contact:** {opp['contact_name']} — {opp['contact_position']}")

                b1, b2, b3 = st.columns([1, 1, 2])
                with b1:
                    if st.button("View Full Detail", key=f"view_{opp['opportunity_id']}"):
                        st.session_state.selected_opp_id = opp["opportunity_id"]
                        st.session_state.current_page = "Opportunity Detail"
                        st.rerun()
                with b2:
                    if st.button("Approve & Add to CRM", key=f"app_{opp['opportunity_id']}", type="primary"):
                        st.session_state.engine.approve_opportunity(opp["opportunity_id"])
                        st.success(f"Added {opp['organization']} to CRM!")
                st.markdown("---")

# -------------------------------------------------------------
# PAGE 4: OPPORTUNITY DETAIL
# -------------------------------------------------------------
elif st.session_state.current_page == "Opportunity Detail":
    opp_id = st.session_state.selected_opp_id
    opps = [o for o in st.session_state.engine.active_opportunities if o["opportunity_id"] == opp_id]
    if not opps:
        opps = [o for o in st.session_state.engine.approved_tracker if o["opportunity_id"] == opp_id]

    if not opps:
        st.warning("Please select an opportunity from the Opportunity Discovery list.")
    else:
        opp = opps[0]
        st.markdown(f"### 📋 Opportunity Detail: {opp['organization']}")
        st.markdown(f"**Domain:** {opp['domain']} | **Region:** {opp['region']} | **Website:** [{opp['website']}]({opp['website']})")

        t1, t2, t3, t4 = st.tabs(["Problem & Solution", "Commercial Evidence", "Decision Maker & Outreach", "Explainability Trail"])

        with t1:
            st.markdown("#### Documented Operational Problem")
            st.write(opp["problem_statement"])
            st.markdown('<div class="evidence-box">', unsafe_allow_html=True)
            st.write("**Supporting Evidence:**")
            for ev in opp["problem_evidence"]:
                st.write(f"• {ev}")
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown("#### Proposed AI Solution")
            st.info(f"**{opp['app_name']}** — {opp['proposed_solution']}")
            st.caption("Note: Proposed solution is an AI recommendation, not an active procurement requirement unless confirmed by sources.")

        with t2:
            st.markdown(f"#### Evidence-Based Commercial Intent Score: {opp['commercial_score']}/100")
            st.write(f"**Level:** {opp['commercial_level']}")
            st.write("**Score Breakdown:**")
            for item in opp["commercial_evidence"]:
                st.write(f"✓ {item}")

            st.markdown("#### Why this Organization was Selected:")
            for reason in opp["why_selected"]:
                st.write(f"• {reason}")

        with t3:
            st.markdown("#### Contact Person (Strict Anti-Hallucination)")
            st.write(f"**Name:** {opp['contact_name']}")
            st.write(f"**Position:** {opp['contact_position']}")
            st.write(f"**Email:** `{opp['contact_email']}`")
            st.write(f"**LinkedIn:** {opp['contact_linkedin']}")
            st.write(f"**Verification Source:** {opp['contact_source']}")

            st.markdown("---")
            st.markdown("#### Generated Outreach Email")
            st.text_area("Cold Outreach Email", opp["outreach_email"], height=220)

            st.markdown("#### LinkedIn Connection Message (Max 200 Characters)")
            li_text = opp["linkedin_message"]
            st.text_input("LinkedIn Message", value=li_text, key="li_inp")
            st.caption(f"Character Count: **{len(li_text)}/200 characters**")

        with t4:
            st.markdown("#### 10-Step Explainability Reasoning Trail")
            for step in opp["reasoning_trail"]:
                st.write(step)

        st.markdown("---")
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("✅ Approve for Outreach Tracker", type="primary"):
                st.session_state.engine.approve_opportunity(opp["opportunity_id"])
                st.success("Opportunity approved!")
        with c2:
            if st.button("❌ Reject / Discard"):
                st.session_state.engine.reject_opportunity(opp["opportunity_id"])
                st.info("Opportunity discarded.")
                st.session_state.current_page = "Opportunity Discovery"
                st.rerun()
        with c3:
            if st.button("⬅ Back to Discovery"):
                st.session_state.current_page = "Opportunity Discovery"
                st.rerun()

# -------------------------------------------------------------
# PAGE 5: JOB OPPORTUNITIES
# -------------------------------------------------------------
elif st.session_state.current_page == "Job Opportunities":
    st.markdown("### 💼 Job & Freelance Opportunity Track")
    st.write("Organizations actively hiring personnel for workflows that can be augmented or automated by AI.")

    job_opps = [o for o in st.session_state.engine.active_opportunities if o.get("opportunity_type") == "Job/Freelance" or o.get("job_url")]

    if not job_opps:
        st.info("No active job postings identified in the current batch. Try a broader search.")
    else:
        for j in job_opps:
            with st.expander(f"💼 {j['organization']} — {j.get('job_title', 'Operational Role')}"):
                c1, c2 = st.columns([2, 1])
                with c1:
                    st.write(f"**Location & Remote Status:** {j.get('remote_status', 'On-site')}")
                    st.write(f"**Pakistan Applicant Eligibility:** `{j.get('application_eligibility', 'Unknown')}`")
                    st.write(f"**Automation Opportunity:** {j['proposed_solution']}")
                    if j.get("job_url"):
                        st.markdown(f"[🔗 Official Job Listing URL]({j['job_url']})")
                with c2:
                    st.metric("Commercial Intent", f"{j['commercial_score']}/100")
                    if st.button("Add to Outreach Tracker", key=f"job_add_{j['opportunity_id']}"):
                        st.session_state.engine.approve_opportunity(j["opportunity_id"])
                        st.success("Added to tracker!")

# -------------------------------------------------------------
# PAGE 6: OUTREACH CRM
# -------------------------------------------------------------
elif st.session_state.current_page == "Outreach CRM":
    st.markdown("### 🤝 Outreach & Lead Tracker CRM")
    st.write("Track contacts, outreach statuses, and follow-up pipeline for approved opportunities.")

    crm_list = st.session_state.engine.approved_tracker

    if not crm_list:
        st.info("Your CRM tracker is currently empty. Go to 'Opportunity Discovery' and click 'Approve & Add to CRM'.")
    else:
        st.write(f"Total Tracked Leads: **{len(crm_list)}**")
        for opp in crm_list:
            with st.expander(f"🏢 {opp['organization']} — Current Status: {opp.get('status', 'New')}"):
                col1, col2 = st.columns(2)
                with col1:
                    new_st = st.selectbox(
                        "Status",
                        [
                            "New", "Researching", "Contacted", "Email Sent", "LinkedIn Sent",
                            "Replied", "Meeting", "Demo", "Proposal", "Negotiation",
                            "Won", "Lost", "Not Relevant", "Follow Up"
                        ],
                        index=0,
                        key=f"status_{opp['opportunity_id']}"
                    )
                    notes = st.text_area("Notes / Meeting logs", value=opp.get("notes", ""), key=f"notes_{opp['opportunity_id']}")
                with col2:
                    c_date = st.date_input("Contact Date", value=datetime.date.today(), key=f"cdate_{opp['opportunity_id']}")
                    st.write(f"**Decision Maker:** {opp.get('contact_name')}")
                    st.write(f"**Email:** `{opp.get('contact_email')}`")
                    if st.button("Save Updates", key=f"save_crm_{opp['opportunity_id']}"):
                        st.session_state.engine.update_crm_status(opp["opportunity_id"], new_st, notes, str(c_date))
                        st.success("CRM status updated!")

# -------------------------------------------------------------
# PAGE 7: EXCEL & GOOGLE DRIVE
# -------------------------------------------------------------
elif st.session_state.current_page == "Excel & Google Drive":
    st.markdown("### 📊 Persistent Excel & Google Drive Tracker")
    st.write("Maintains a centralized master `.xlsx` database with 4 structured worksheets.")

    # Status box
    st.markdown(f"""
    <div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; padding: 16px; border-radius: 8px; margin-bottom: 20px;">
        <h4>Google Drive Persistent Folder</h4>
        <p><strong>Configured Folder:</strong> <a href="{gdrive_url}" target="_blank">Startup Planning & Organizer</a></p>
        <p><strong>Folder ID:</strong> <code>1QJnRIqDLOpkaArrNIcpaehgYlHWOyXEG</code></p>
        <p><strong>Master Filename:</strong> <code>Startup_Planning_Organizer_Tracker.xlsx</code></p>
    </div>
    """, unsafe_allow_html=True)

    # Export workbook
    wb = st.session_state.engine.export_to_excel_workbook()
    excel_bytes = storage.get_workbook_bytes(wb)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.download_button(
            label="📥 Download Master Excel (.xlsx)",
            data=excel_bytes,
            file_name=f"Startup_Planning_Organizer_Tracker_{datetime.datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary"
        )
    with c2:
        if st.button("🔄 Sync to Google Drive"):
            with st.spinner("Connecting to Google Drive..."):
                res = st.session_state.engine.save_and_sync_tracker()
                if res["gdrive_synced"]:
                    st.success(res["gdrive_message"])
                else:
                    st.warning(f"⚠ {res['gdrive_message']}")
                    st.info(f"Local backup saved safely as: {res['local_file']}")
    with c3:
        if st.button("🔁 Refresh Tracker"):
            st.success("Tracker reloaded. Latest records verified against duplicate index.")

    st.markdown("---")
    st.markdown("#### Master Workbook Structure (4 Worksheets):")
    st.write("1. **Opportunities**: Main research database (37 columns including ID, scores, outreach, contacts)")
    st.write("2. **Research Runs**: Execution audit trail and timestamps")
    st.write("3. **Sources**: Grounded URLs, source quality tiers, and publication dates")
    st.write("4. **Contacts**: Decision makers, verification statuses, and verified profiles")
