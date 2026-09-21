"""
storage.py - Persistence and Tracker Storage Module
Part of '🚀 Startup Planning & Organizer AI'

Handles:
- Deterministic Opportunity ID generation (SHA256 hash)
- Excel Master Workbook management with 4 sheets using openpyxl:
    1. Opportunities (Main database)
    2. Research Runs (Execution logs)
    3. Sources (Source-level evidence)
    4. Contacts (Verified decision makers)
- Deduplication and record updates
- Local backup creation (timestamped)
- Google Drive API integration for folder ID '1QJnRIqDLOpkaArrNIcpaehgYlHWOyXEG'
"""

import os
import hashlib
import datetime
import io
from typing import Dict, List, Any, Optional, Tuple

try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False

try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
    GOOGLE_DRIVE_AVAILABLE = True
except ImportError:
    GOOGLE_DRIVE_AVAILABLE = False


MASTER_TRACKER_FILENAME = "Startup_Planning_Organizer_Tracker.xlsx"
DEFAULT_FOLDER_ID = "1QJnRIqDLOpkaArrNIcpaehgYlHWOyXEG"

OPPORTUNITY_COLUMNS = [
    "Opportunity ID", "Run Date", "Run Time", "Region", "Domain",
    "Organization", "Organization Type", "Country", "Website", "Opportunity Type",
    "Job/Project Title", "Job URL", "Application Eligibility", "Remote Status",
    "Problem Statement", "Problem Evidence", "AI Solution", "Proposed App Name",
    "AI/Automation Intent", "Commercial Intent Score", "Commercial Evidence",
    "Research Confidence", "Contact Name", "Contact Position", "Contact Email",
    "Email Verification Status", "LinkedIn URL", "Contact Source", "Source URLs",
    "Source Dates", "Why Selected", "Outreach Email", "LinkedIn Message",
    "Status", "Date Contacted", "Follow-up Date", "Outcome", "Notes"
]

RESEARCH_RUNS_COLUMNS = [
    "Run ID", "Date", "Time", "Region", "Domain", "Search Period",
    "Organizations Found", "Opportunities Found", "Approved Opportunities",
    "Research Status", "Google Drive Sync Status"
]

SOURCES_COLUMNS = [
    "Opportunity ID", "Source", "Source Type", "URL", "Publication Date",
    "Retrieved Date", "Evidence Summary", "Source Quality"
]

CONTACTS_COLUMNS = [
    "Opportunity ID", "Organization", "Name", "Position", "Email",
    "Email Verification", "LinkedIn", "LinkedIn Verification", "Source"
]


def generate_opportunity_id(organization: str, opp_type: str, title: str, source_url: str) -> str:
    """Deterministic hash for duplicate prevention."""
    raw = f"{organization.strip().lower()}|{opp_type.strip().lower()}|{title.strip().lower()}|{source_url.strip().lower()}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def create_master_workbook_in_memory() -> Any:
    """Create an empty master Excel workbook with the 4 required sheets and formatted headers."""
    if not OPENPYXL_AVAILABLE:
        raise RuntimeError("openpyxl is required to generate Excel workbooks.")

    wb = openpyxl.Workbook()
    # Sheet 1: Opportunities
    ws_opps = wb.active
    ws_opps.title = "Opportunities"
    _style_headers(ws_opps, OPPORTUNITY_COLUMNS, "1E3A8A")  # Deep Blue

    # Sheet 2: Research Runs
    ws_runs = wb.create_sheet(title="Research Runs")
    _style_headers(ws_runs, RESEARCH_RUNS_COLUMNS, "065F46")  # Deep Emerald

    # Sheet 3: Sources
    ws_sources = wb.create_sheet(title="Sources")
    _style_headers(ws_sources, SOURCES_COLUMNS, "78350F")  # Deep Amber

    # Sheet 4: Contacts
    ws_contacts = wb.create_sheet(title="Contacts")
    _style_headers(ws_contacts, CONTACTS_COLUMNS, "4C1D95")  # Deep Purple

    return wb


def _style_headers(ws: Any, columns: List[str], header_color: str):
    fill = PatternFill(start_color=header_color, end_color=header_color, fill_type="solid")
    font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    align = Alignment(horizontal="center", vertical="center", wrap_text=True)
    thin_border = Border(
        left=Side(style='thin', color='D1D5DB'),
        right=Side(style='thin', color='D1D5DB'),
        top=Side(style='thin', color='D1D5DB'),
        bottom=Side(style='medium', color='111827')
    )

    ws.row_dimensions[1].height = 28
    for col_idx, col_name in enumerate(columns, start=1):
        cell = ws.cell(row=1, column=col_idx, value=col_name)
        cell.fill = fill
        cell.font = font
        cell.alignment = align
        cell.border = thin_border
        col_letter = get_column_letter(col_idx)
        ws.column_dimensions[col_letter].width = max(len(col_name) + 4, 15)


def append_or_update_opportunities(wb: Any, opportunities: List[Dict[str, Any]]) -> Tuple[int, int]:
    """
    Appends new opportunities or updates existing ones based on Opportunity ID.
    Returns (added_count, updated_count).
    """
    ws_opps = wb["Opportunities"]
    ws_sources = wb["Sources"]
    ws_contacts = wb["Contacts"]

    # Map existing Opportunity IDs to row numbers in ws_opps
    existing_ids = {}
    for row in range(2, ws_opps.max_row + 1):
        val = ws_opps.cell(row=row, column=1).value
        if val:
            existing_ids[str(val).strip()] = row

    added = 0
    updated = 0

    for opp in opportunities:
        opp_id = opp.get("opportunity_id") or generate_opportunity_id(
            opp.get("organization", ""),
            opp.get("opportunity_type", ""),
            opp.get("job_title", opp.get("problem_statement", "")[:30]),
            opp.get("primary_source_url", "")
        )

        row_data = [
            opp_id,
            opp.get("run_date", datetime.date.today().isoformat()),
            opp.get("run_time", datetime.datetime.now().strftime("%H:%M")),
            opp.get("region", "Pakistan"),
            opp.get("domain", ""),
            opp.get("organization", ""),
            opp.get("organization_type", "Company"),
            opp.get("country", ""),
            opp.get("website", ""),
            opp.get("opportunity_type", "Operational Problem"),
            opp.get("job_title", ""),
            opp.get("job_url", ""),
            opp.get("application_eligibility", "Verified eligible" if opp.get("region") == "Pakistan" else "Unknown"),
            opp.get("remote_status", "Not specified"),
            opp.get("problem_statement", ""),
            "; ".join(opp.get("problem_evidence", [])) if isinstance(opp.get("problem_evidence"), list) else str(opp.get("problem_evidence", "")),
            opp.get("proposed_solution", ""),
            opp.get("app_name", ""),
            opp.get("ai_intent", "Medium"),
            opp.get("commercial_score", 0),
            "; ".join(opp.get("commercial_evidence", [])) if isinstance(opp.get("commercial_evidence"), list) else str(opp.get("commercial_evidence", "")),
            opp.get("confidence", "Medium"),
            opp.get("contact_name", "Not publicly verified"),
            opp.get("contact_position", "Not publicly verified"),
            opp.get("contact_email", "Not publicly verified"),
            opp.get("email_verification_status", "Unverified"),
            opp.get("contact_linkedin", "LinkedIn: Not found"),
            opp.get("contact_source", "Not publicly verified"),
            "; ".join(opp.get("source_urls", [])) if isinstance(opp.get("source_urls"), list) else str(opp.get("source_urls", "")),
            "; ".join(opp.get("source_dates", [])) if isinstance(opp.get("source_dates"), list) else str(opp.get("source_dates", "")),
            opp.get("why_selected", ""),
            opp.get("outreach_email", ""),
            opp.get("linkedin_message", ""),
            opp.get("status", "New"),
            opp.get("date_contacted", ""),
            opp.get("follow_up_date", ""),
            opp.get("outcome", ""),
            opp.get("notes", "")
        ]

        if opp_id in existing_ids:
            # Update specific evidence fields while preserving status and notes
            target_row = existing_ids[opp_id]
            # Update problem evidence, commercial score, outreach if renewed
            ws_opps.cell(row=target_row, column=16, value=row_data[15])  # Problem Evidence
            ws_opps.cell(row=target_row, column=20, value=row_data[19])  # Commercial Score
            ws_opps.cell(row=target_row, column=21, value=row_data[20])  # Commercial Evidence
            updated += 1
        else:
            # Append new row
            ws_opps.append(row_data)
            existing_ids[opp_id] = ws_opps.max_row
            added += 1

            # Append source rows
            sources_list = opp.get("sources_detail", [])
            for src in sources_list:
                ws_sources.append([
                    opp_id,
                    src.get("source_name", "Web Source"),
                    src.get("source_type", "Tier 2 — High-quality secondary"),
                    src.get("url", ""),
                    src.get("date", datetime.date.today().isoformat()),
                    datetime.date.today().isoformat(),
                    src.get("evidence", ""),
                    src.get("quality", "Tier 2")
                ])

            # Append contact row if contact exists
            if opp.get("contact_name") and opp.get("contact_name") != "Not publicly verified":
                ws_contacts.append([
                    opp_id,
                    opp.get("organization", ""),
                    opp.get("contact_name", ""),
                    opp.get("contact_position", ""),
                    opp.get("contact_email", "Not publicly verified"),
                    opp.get("email_verification_status", "Unverified"),
                    opp.get("contact_linkedin", "LinkedIn: Not found"),
                    "Verified" if opp.get("contact_linkedin") and "linkedin.com" in opp.get("contact_linkedin") else "Not found",
                    opp.get("contact_source", "Official")
                ])

    return added, updated


def log_research_run(wb: Any, run_info: Dict[str, Any]):
    """Appends an execution record to the 'Research Runs' worksheet."""
    ws = wb["Research Runs"]
    run_id = f"RUN-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}"
    ws.append([
        run_id,
        run_info.get("date", datetime.date.today().isoformat()),
        run_info.get("time", datetime.datetime.now().strftime("%H:%M")),
        run_info.get("region", "Pakistan"),
        run_info.get("domain", "General"),
        run_info.get("search_period", "Last 90 days"),
        run_info.get("orgs_found", 0),
        run_info.get("opps_found", 0),
        run_info.get("approved_opps", 0),
        run_info.get("status", "Completed"),
        run_info.get("gdrive_status", "Pending")
    ])


def save_local_backup(wb: Any, custom_filename: Optional[str] = None) -> str:
    """Saves a timestamped local backup .xlsx file to protect against transient errors."""
    timestamp = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M")
    filename = custom_filename or f"startup_opportunities_{timestamp}.xlsx"
    wb.save(filename)
    return filename


def get_workbook_bytes(wb: Any) -> bytes:
    """Exports the workbook to in-memory bytes for direct web download."""
    bio = io.BytesIO()
    wb.save(bio)
    bio.seek(0)
    return bio.getvalue()


class GoogleDriveManager:
    """Manages synchronization with the user's designated Google Drive folder."""

    def __init__(self, folder_id: str = DEFAULT_FOLDER_ID, credentials_info: Optional[Dict[str, Any]] = None):
        self.folder_id = folder_id or DEFAULT_FOLDER_ID
        self.credentials_info = credentials_info
        self.service = None
        self._authenticate()

    def _authenticate(self):
        if not GOOGLE_DRIVE_AVAILABLE:
            return
        if not self.credentials_info:
            return
        try:
            scopes = ['https://www.googleapis.com/auth/drive.file', 'https://www.googleapis.com/auth/drive']
            creds = service_account.Credentials.from_service_account_info(
                self.credentials_info, scopes=scopes
            )
            self.service = build('drive', 'v3', credentials=creds)
        except Exception as e:
            self.service = None
            self.auth_error = str(e)

    def is_connected(self) -> bool:
        return self.service is not None

    def find_master_tracker_file(self) -> Optional[Dict[str, str]]:
        """Finds 'Startup_Planning_Organizer_Tracker.xlsx' inside the designated folder."""
        if not self.service:
            return None
        try:
            query = (
                f"'{self.folder_id}' in parents and "
                f"name = '{MASTER_TRACKER_FILENAME}' and "
                f"trashed = false"
            )
            response = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name, modifiedTime, webViewLink)'
            ).execute()
            files = response.get('files', [])
            return files[0] if files else None
        except Exception:
            return None

    def download_tracker(self, file_id: str) -> Optional[Any]:
        """Downloads the existing tracker workbook from Google Drive into openpyxl."""
        if not self.service or not OPENPYXL_AVAILABLE:
            return None
        try:
            request = self.service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()
            fh.seek(0)
            return openpyxl.load_workbook(fh)
        except Exception:
            return None

    def upload_or_update_tracker(self, wb: Any) -> Tuple[bool, str, Optional[str]]:
        """
        Updates the existing master tracker if present; creates it inside folder if absent.
        Returns (success: bool, message: str, file_link: Optional[str]).
        """
        if not self.service:
            return False, "Google Drive service is not authenticated. Please configure Streamlit Secrets.", None

        existing_file = self.find_master_tracker_file()
        file_bytes = get_workbook_bytes(wb)
        media = MediaIoBaseUpload(
            io.BytesIO(file_bytes),
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            resumable=True
        )

        try:
            if existing_file:
                # Update existing file
                updated = self.service.files().update(
                    fileId=existing_file['id'],
                    media_body=media,
                    fields='id, name, webViewLink'
                ).execute()
                link = updated.get('webViewLink') or f"https://drive.google.com/file/d/{updated['id']}/view"
                return True, f"Successfully updated existing master tracker '{MASTER_TRACKER_FILENAME}'.", link
            else:
                # Create file inside specified folder
                file_metadata = {
                    'name': MASTER_TRACKER_FILENAME,
                    'parents': [self.folder_id]
                }
                created = self.service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id, name, webViewLink'
                ).execute()
                link = created.get('webViewLink') or f"https://drive.google.com/file/d/{created['id']}/view"
                return True, f"Created new master tracker '{MASTER_TRACKER_FILENAME}' in target folder.", link
        except Exception as e:
            return False, f"Google Drive upload failed: {str(e)}", None
