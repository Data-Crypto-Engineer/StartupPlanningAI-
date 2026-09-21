"""
workflow.py - End-to-End Orchestrator and Pipeline
Part of '🚀 Startup Planning & Organizer AI'

Dependencies (One-Way):
workflow.py -> research.py -> ai_engine.py -> storage.py
"""

import datetime
from typing import Dict, List, Any, Optional, Tuple

import research
import ai_engine
import storage


class StartupResearchWorkflow:
    """Coordinates market signal discovery, AI synthesis, validation, and storage."""

    def __init__(self, gemini_api_key: Optional[str] = None, gemini_model: Optional[str] = None):
        self.ai = ai_engine.GeminiEngine(api_key=gemini_api_key, model_name=gemini_model)
        self.active_opportunities: List[Dict[str, Any]] = []
        self.approved_tracker: List[Dict[str, Any]] = []
        self.research_runs: List[Dict[str, Any]] = []

    def get_domains_for_region(self, region: str) -> List[Dict[str, Any]]:
        """Stage 1: Broad market research and domain discovery."""
        return research.discover_opportunity_domains(region)

    def run_opportunity_investigation(
        self,
        region: str,
        domain: str,
        lookback_days: int = 90,
        min_commercial_score: int = 0,
        pakistan_only_eligible: bool = False,
        remote_only: bool = False,
        max_results: int = 25
    ) -> List[Dict[str, Any]]:
        """
        Stage 2 - 7: Search organizations, assess commercial intent, generate solutions and outreach.
        """
        raw_signals = research.search_market_opportunities(
            region=region,
            domain=domain,
            lookback_days=lookback_days,
            pakistan_only_eligible=pakistan_only_eligible,
            remote_only=remote_only
        )

        opportunities = []
        for signal in raw_signals[:max_results]:
            opp = self.ai.analyze_opportunity(signal)
            # Add unique opportunity key
            opp_id = storage.generate_opportunity_id(
                opp["organization"],
                opp["opportunity_type"],
                opp.get("job_title", opp.get("problem_statement", "")[:30]),
                opp.get("website", "")
            )
            opp["opportunity_id"] = opp_id
            opp["run_date"] = datetime.date.today().isoformat()
            opp["run_time"] = datetime.datetime.now().strftime("%H:%M")

            if opp["commercial_score"] >= min_commercial_score:
                opportunities.append(opp)

        self.active_opportunities = opportunities
        return opportunities

    def approve_opportunity(self, opp_id: str) -> Optional[Dict[str, Any]]:
        """Moves an opportunity from active discoveries into the approved outreach tracker."""
        for opp in self.active_opportunities:
            if opp["opportunity_id"] == opp_id:
                if not any(a["opportunity_id"] == opp_id for a in self.approved_tracker):
                    approved = dict(opp)
                    approved["status"] = "New"
                    self.approved_tracker.append(approved)
                    return approved
        return None

    def reject_opportunity(self, opp_id: str) -> bool:
        """Discards an opportunity from active review."""
        initial_len = len(self.active_opportunities)
        self.active_opportunities = [o for o in self.active_opportunities if o["opportunity_id"] != opp_id]
        return len(self.active_opportunities) < initial_len

    def update_opportunity_details(self, opp_id: str, updates: Dict[str, Any]) -> bool:
        """Allows human editing of problem statement, proposed solution, contacts, or notes."""
        found = False
        for opp in self.active_opportunities:
            if opp["opportunity_id"] == opp_id:
                opp.update(updates)
                found = True
                break
        for opp in self.approved_tracker:
            if opp["opportunity_id"] == opp_id:
                opp.update(updates)
                found = True
                break
        return found

    def update_crm_status(self, opp_id: str, new_status: str, notes: Optional[str] = None, contact_date: Optional[str] = None) -> bool:
        """Updates sales / outreach CRM status for a tracked company."""
        for opp in self.approved_tracker:
            if opp["opportunity_id"] == opp_id:
                opp["status"] = new_status
                if notes is not None:
                    opp["notes"] = notes
                if contact_date:
                    opp["date_contacted"] = contact_date
                return True
        return False

    def export_to_excel_workbook(self) -> Any:
        """Builds a complete openpyxl workbook with 4 sheets and all approved records."""
        wb = storage.create_master_workbook_in_memory()
        records_to_export = self.approved_tracker if self.approved_tracker else self.active_opportunities
        storage.append_or_update_opportunities(wb, records_to_export)

        # Log run
        storage.log_research_run(wb, {
            "date": datetime.date.today().isoformat(),
            "time": datetime.datetime.now().strftime("%H:%M"),
            "region": self.active_opportunities[0].get("region", "Pakistan") if self.active_opportunities else "Pakistan",
            "domain": self.active_opportunities[0].get("domain", "General") if self.active_opportunities else "General",
            "search_period": "Last 90 days",
            "orgs_found": len(records_to_export),
            "opps_found": len(records_to_export),
            "approved_opps": len(self.approved_tracker),
            "status": "Completed",
            "gdrive_status": "Ready"
        })
        return wb

    def save_and_sync_tracker(
        self,
        gdrive_folder_id: str = storage.DEFAULT_FOLDER_ID,
        gdrive_credentials: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        1. Generates local Excel backup.
        2. Attempts upload/update to Google Drive folder.
        3. Returns outcome status without losing local data.
        """
        wb = self.export_to_excel_workbook()
        local_filename = storage.save_local_backup(wb)

        drive_mgr = storage.GoogleDriveManager(folder_id=gdrive_folder_id, credentials_info=gdrive_credentials)

        if not drive_mgr.is_connected():
            return {
                "local_saved": True,
                "local_file": local_filename,
                "gdrive_synced": False,
                "gdrive_message": "Google Drive credentials are not configured in Streamlit Secrets. Local Excel backup created.",
                "file_link": None
            }

        success, msg, link = drive_mgr.upload_or_update_tracker(wb)
        return {
            "local_saved": True,
            "local_file": local_filename,
            "gdrive_synced": success,
            "gdrive_message": msg,
            "file_link": link
        }

    def compute_summary_metrics(self) -> Dict[str, Any]:
        """Generates dashboard metrics."""
        opps = self.active_opportunities
        orgs = set(o["organization"] for o in opps)
        comm_opps = sum(1 for o in opps if o.get("commercial_score", 0) >= 40)
        ai_opps = sum(1 for o in opps if o.get("ai_intent") in ["High", "Medium"])
        jobs = sum(1 for o in opps if o.get("opportunity_type") == "Job/Freelance")
        contacts = sum(1 for o in opps if o.get("contact_name") and o.get("contact_name") != "Not publicly verified")
        high_conf = sum(1 for o in opps if o.get("confidence") == "High")

        return {
            "organizations_found": len(orgs),
            "commercial_opportunities": comm_opps,
            "ai_opportunities": ai_opps,
            "verified_jobs": jobs,
            "verified_contacts": contacts,
            "high_confidence_opportunities": high_conf,
            "total_approved": len(self.approved_tracker)
        }
