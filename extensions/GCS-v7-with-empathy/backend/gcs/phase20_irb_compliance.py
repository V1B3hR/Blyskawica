"""
phase20_irb_compliance.py - IRB/Ethics Compliance Framework for Phase 20 Pilots

Phase 20 completion: Comprehensive compliance infrastructure for societal pilots
- IRB approval tracking and documentation
- Ethics board oversight coordination
- Regulatory compliance validation (HIPAA, GDPR, etc.)
- Incident response protocols
- Participant protection measures
- Multi-jurisdiction compliance management

This module ensures Phase 20 pilots meet all ethical and regulatory requirements
before deployment across education, healthcare, and workplace contexts.
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from enum import Enum
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)


class ComplianceStatus(Enum):
    """Compliance check status"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    CONDITIONAL_APPROVAL = "conditional_approval"
    REJECTED = "rejected"
    EXPIRED = "expired"
    WITHDRAWN = "withdrawn"


class RegulatoryFramework(Enum):
    """Applicable regulatory frameworks"""
    HIPAA = "hipaa"  # Healthcare
    FERPA = "ferpa"  # Education
    GDPR = "gdpr"  # European Union
    CCPA = "ccpa"  # California
    IRB_45_CFR_46 = "irb_45_cfr_46"  # Common Rule (US)
    FDA_IDE = "fda_ide"  # Investigational Device Exemption
    ISO_14155 = "iso_14155"  # Clinical investigation
    LOCAL_ETHICS = "local_ethics"  # Site-specific ethics


class IncidentSeverityLevel(Enum):
    """Incident severity for reporting"""
    MINOR = "minor"
    MODERATE = "moderate"
    SERIOUS = "serious"
    LIFE_THREATENING = "life_threatening"
    FATAL = "fatal"


@dataclass
class IRBApproval:
    """IRB approval record"""
    irb_id: str
    institution: str
    protocol_number: str
    approval_date: datetime
    expiration_date: datetime
    status: ComplianceStatus
    conditions: List[str] = field(default_factory=list)
    amendments: List[Dict[str, Any]] = field(default_factory=list)
    annual_reviews: List[datetime] = field(default_factory=list)
    contact_person: str = ""
    contact_email: str = ""
    documents: Dict[str, str] = field(default_factory=dict)


@dataclass
class InformedConsent:
    """Informed consent documentation"""
    consent_id: str
    participant_id: str
    site_id: str
    consent_version: str
    consent_date: datetime
    consent_form_signed: bool
    withdrawal_allowed: bool = True
    data_sharing_consent: bool = False
    long_term_followup_consent: bool = False
    genetic_data_consent: bool = False
    comprehension_test_score: Optional[float] = None
    witness_signature: bool = False
    parent_guardian_consent: bool = False  # For minors


@dataclass
class ComplianceCheck:
    """Individual compliance requirement check"""
    check_id: str
    requirement_name: str
    framework: RegulatoryFramework
    status: ComplianceStatus
    last_verified: datetime
    next_review: datetime
    responsible_person: str
    evidence_documents: List[str] = field(default_factory=list)
    notes: str = ""


@dataclass
class AdverseEvent:
    """Adverse event report"""
    event_id: str
    site_id: str
    participant_id: str
    event_date: datetime
    severity: IncidentSeverityLevel
    description: str
    causality_assessment: str  # "definitely_related", "probably_related", "possibly_related", etc.
    reported_to_irb: bool = False
    reported_to_sponsor: bool = False
    reported_to_fda: bool = False
    resolution_status: str = "open"
    resolution_date: Optional[datetime] = None


class IRBComplianceManager:
    """
    Comprehensive IRB and ethics compliance management for Phase 20 pilots.
    
    Manages:
    - IRB approval tracking across multiple sites
    - Informed consent documentation and validation
    - Regulatory compliance verification
    - Adverse event reporting
    - Ethics board coordination
    - Multi-jurisdiction compliance
    """
    
    def __init__(self, data_dir: Optional[Path] = None):
        """Initialize compliance manager"""
        self.data_dir = data_dir or Path("/tmp/phase20_compliance")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.irb_approvals: Dict[str, IRBApproval] = {}
        self.consents: Dict[str, InformedConsent] = {}
        self.compliance_checks: Dict[str, ComplianceCheck] = {}
        self.adverse_events: List[AdverseEvent] = []
        
        # Initialize standard compliance requirements
        self._initialize_compliance_framework()
        
        logger.info("IRBComplianceManager initialized")
    
    def _initialize_compliance_framework(self):
        """Initialize standard compliance requirements"""
        # HIPAA compliance for healthcare pilots
        self.add_compliance_check(ComplianceCheck(
            check_id="HIPAA_001",
            requirement_name="HIPAA Privacy Rule Compliance",
            framework=RegulatoryFramework.HIPAA,
            status=ComplianceStatus.NOT_STARTED,
            last_verified=datetime.now(),
            next_review=datetime.now() + timedelta(days=180),
            responsible_person="Privacy Officer"
        ))
        
        # FERPA compliance for education pilots
        self.add_compliance_check(ComplianceCheck(
            check_id="FERPA_001",
            requirement_name="FERPA Student Privacy Protection",
            framework=RegulatoryFramework.FERPA,
            status=ComplianceStatus.NOT_STARTED,
            last_verified=datetime.now(),
            next_review=datetime.now() + timedelta(days=180),
            responsible_person="Education Compliance Officer"
        ))
        
        # GDPR compliance (if EU participants)
        self.add_compliance_check(ComplianceCheck(
            check_id="GDPR_001",
            requirement_name="GDPR Data Protection Compliance",
            framework=RegulatoryFramework.GDPR,
            status=ComplianceStatus.NOT_STARTED,
            last_verified=datetime.now(),
            next_review=datetime.now() + timedelta(days=90),
            responsible_person="Data Protection Officer"
        ))
        
        # IRB Common Rule compliance
        self.add_compliance_check(ComplianceCheck(
            check_id="IRB_001",
            requirement_name="45 CFR 46 Common Rule Compliance",
            framework=RegulatoryFramework.IRB_45_CFR_46,
            status=ComplianceStatus.NOT_STARTED,
            last_verified=datetime.now(),
            next_review=datetime.now() + timedelta(days=365),
            responsible_person="IRB Administrator"
        ))
    
    def register_irb_approval(self, approval: IRBApproval) -> str:
        """
        Register IRB approval for a pilot site.
        
        Phase 20 entry criterion: IRB approvals required for all sites.
        """
        if approval.irb_id in self.irb_approvals:
            logger.warning(f"IRB approval {approval.irb_id} already registered. Updating.")
        
        self.irb_approvals[approval.irb_id] = approval
        
        # Save to disk
        self._save_irb_approval(approval)
        
        logger.info(f"IRB approval registered: {approval.irb_id} - {approval.institution}")
        logger.info(f"  Protocol: {approval.protocol_number}")
        logger.info(f"  Approved: {approval.approval_date.strftime('%Y-%m-%d')}")
        logger.info(f"  Expires: {approval.expiration_date.strftime('%Y-%m-%d')}")
        
        return approval.irb_id
    
    def record_informed_consent(self, consent: InformedConsent) -> str:
        """
        Record informed consent from participant.
        
        Phase 20 requirement: Comprehensive informed consent for all participants.
        """
        if not consent.consent_form_signed:
            raise ValueError("Consent form must be signed")
        
        if consent.comprehension_test_score is not None and consent.comprehension_test_score < 0.8:
            logger.warning(f"Participant {consent.participant_id} comprehension test score "
                         f"below 80%: {consent.comprehension_test_score:.1%}")
        
        self.consents[consent.consent_id] = consent
        
        # Save to disk
        self._save_consent(consent)
        
        logger.info(f"Informed consent recorded: {consent.consent_id}")
        logger.info(f"  Participant: {consent.participant_id}")
        logger.info(f"  Site: {consent.site_id}")
        logger.info(f"  Consent date: {consent.consent_date.strftime('%Y-%m-%d')}")
        
        return consent.consent_id
    
    def add_compliance_check(self, check: ComplianceCheck):
        """Add compliance requirement check"""
        self.compliance_checks[check.check_id] = check
    
    def update_compliance_status(self,
                                 check_id: str,
                                 status: ComplianceStatus,
                                 evidence_document: Optional[str] = None):
        """Update status of compliance check"""
        if check_id not in self.compliance_checks:
            raise ValueError(f"Compliance check {check_id} not found")
        
        check = self.compliance_checks[check_id]
        check.status = status
        check.last_verified = datetime.now()
        
        if evidence_document:
            check.evidence_documents.append(evidence_document)
        
        logger.info(f"Compliance check updated: {check.requirement_name} -> {status.value}")
    
    def report_adverse_event(self, event: AdverseEvent) -> str:
        """
        Report adverse event.
        
        Phase 20 requirement: Zero critical ethical incidents.
        """
        self.adverse_events.append(event)
        
        # Determine reporting requirements based on severity
        if event.severity in [IncidentSeverityLevel.SERIOUS, 
                             IncidentSeverityLevel.LIFE_THREATENING,
                             IncidentSeverityLevel.FATAL]:
            logger.critical(f"SERIOUS ADVERSE EVENT: {event.event_id}")
            logger.critical(f"  Severity: {event.severity.value}")
            logger.critical(f"  Site: {event.site_id}")
            logger.critical(f"  Description: {event.description}")
            
            # Trigger immediate reporting
            self._trigger_serious_adverse_event_protocol(event)
        else:
            logger.warning(f"Adverse event reported: {event.event_id} ({event.severity.value})")
        
        # Save to disk
        self._save_adverse_event(event)
        
        return event.event_id
    
    def _trigger_serious_adverse_event_protocol(self, event: AdverseEvent):
        """
        Trigger serious adverse event protocol.
        
        Would implement:
        - Immediate IRB notification
        - Sponsor notification
        - FDA notification (if required)
        - Site suspension consideration
        - Participant protection measures
        """
        logger.critical("ACTIVATING SERIOUS ADVERSE EVENT PROTOCOL")
        logger.critical("  1. Notifying IRB within 24 hours")
        logger.critical("  2. Notifying sponsor within 24 hours")
        logger.critical("  3. Evaluating need for FDA notification")
        logger.critical("  4. Assessing site suspension")
        logger.critical("  5. Implementing participant protection measures")
        
        # In production, would send actual notifications
    
    def get_compliance_dashboard(self) -> Dict[str, Any]:
        """
        Get comprehensive compliance dashboard.
        
        Returns compliance status for all Phase 20 requirements.
        """
        # IRB approval status
        active_irbs = sum(1 for irb in self.irb_approvals.values() 
                         if irb.status == ComplianceStatus.APPROVED
                         and irb.expiration_date > datetime.now())
        
        expired_irbs = sum(1 for irb in self.irb_approvals.values()
                          if irb.expiration_date <= datetime.now())
        
        # Consent status
        total_consents = len(self.consents)
        valid_consents = sum(1 for c in self.consents.values() if c.consent_form_signed)
        
        # Compliance checks
        checks_by_status = {}
        for status in ComplianceStatus:
            checks_by_status[status.value] = sum(
                1 for c in self.compliance_checks.values() if c.status == status
            )
        
        # Adverse events
        adverse_events_by_severity = {}
        for severity in IncidentSeverityLevel:
            adverse_events_by_severity[severity.value] = sum(
                1 for e in self.adverse_events if e.severity == severity
            )
        
        serious_events = sum(
            1 for e in self.adverse_events 
            if e.severity in [IncidentSeverityLevel.SERIOUS,
                            IncidentSeverityLevel.LIFE_THREATENING,
                            IncidentSeverityLevel.FATAL]
        )
        
        dashboard = {
            'timestamp': datetime.now().isoformat(),
            'irb_approvals': {
                'total': len(self.irb_approvals),
                'active': active_irbs,
                'expired': expired_irbs,
                'details': [
                    {
                        'irb_id': irb.irb_id,
                        'institution': irb.institution,
                        'status': irb.status.value,
                        'expires': irb.expiration_date.strftime('%Y-%m-%d')
                    }
                    for irb in self.irb_approvals.values()
                ]
            },
            'informed_consents': {
                'total': total_consents,
                'valid': valid_consents,
                'consent_rate': (valid_consents / total_consents * 100) if total_consents > 0 else 0
            },
            'compliance_checks': {
                'total': len(self.compliance_checks),
                'by_status': checks_by_status,
                'approved_percentage': (checks_by_status.get('approved', 0) / 
                                       len(self.compliance_checks) * 100) 
                                      if self.compliance_checks else 0
            },
            'adverse_events': {
                'total': len(self.adverse_events),
                'by_severity': adverse_events_by_severity,
                'serious_events': serious_events
            },
            'phase20_compliance': {
                'irb_approvals_obtained': active_irbs > 0,
                'all_irbs_active': expired_irbs == 0,
                'consent_rate_adequate': (valid_consents / total_consents * 100) >= 95 if total_consents > 0 else False,
                'no_serious_adverse_events': serious_events == 0,
                'compliance_framework_approved': checks_by_status.get('approved', 0) >= len(self.compliance_checks) * 0.8,
                'ready_for_pilot_launch': (
                    active_irbs > 0 and
                    expired_irbs == 0 and
                    serious_events == 0 and
                    checks_by_status.get('approved', 0) >= len(self.compliance_checks) * 0.8
                )
            }
        }
        
        return dashboard
    
    def _save_irb_approval(self, approval: IRBApproval):
        """Save IRB approval to disk"""
        irb_dir = self.data_dir / "irb_approvals"
        irb_dir.mkdir(parents=True, exist_ok=True)
        
        filepath = irb_dir / f"{approval.irb_id}.json"
        
        data = {
            'irb_id': approval.irb_id,
            'institution': approval.institution,
            'protocol_number': approval.protocol_number,
            'approval_date': approval.approval_date.isoformat(),
            'expiration_date': approval.expiration_date.isoformat(),
            'status': approval.status.value,
            'conditions': approval.conditions,
            'contact_person': approval.contact_person,
            'contact_email': approval.contact_email
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _save_consent(self, consent: InformedConsent):
        """Save informed consent to disk"""
        consent_dir = self.data_dir / "consents" / consent.site_id
        consent_dir.mkdir(parents=True, exist_ok=True)
        
        filepath = consent_dir / f"{consent.consent_id}.json"
        
        data = {
            'consent_id': consent.consent_id,
            'participant_id': consent.participant_id,
            'site_id': consent.site_id,
            'consent_version': consent.consent_version,
            'consent_date': consent.consent_date.isoformat(),
            'consent_form_signed': consent.consent_form_signed,
            'data_sharing_consent': consent.data_sharing_consent,
            'comprehension_test_score': consent.comprehension_test_score
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _save_adverse_event(self, event: AdverseEvent):
        """Save adverse event to disk"""
        ae_dir = self.data_dir / "adverse_events"
        ae_dir.mkdir(parents=True, exist_ok=True)
        
        filepath = ae_dir / f"{event.event_id}.json"
        
        data = {
            'event_id': event.event_id,
            'site_id': event.site_id,
            'participant_id': event.participant_id,
            'event_date': event.event_date.isoformat(),
            'severity': event.severity.value,
            'description': event.description,
            'causality_assessment': event.causality_assessment,
            'reported_to_irb': event.reported_to_irb,
            'resolution_status': event.resolution_status
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)


def main():
    """Demonstrate IRB compliance management"""
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    
    manager = IRBComplianceManager()
    
    print("\n" + "="*70)
    print("  Phase 20 IRB/Ethics Compliance Framework")
    print("="*70)
    
    # Register sample IRB approval
    irb = IRBApproval(
        irb_id="IRB_2025_001",
        institution="Example University",
        protocol_number="PROTO-2025-GCS-001",
        approval_date=datetime.now(),
        expiration_date=datetime.now() + timedelta(days=365),
        status=ComplianceStatus.APPROVED,
        contact_person="Dr. Jane Smith",
        contact_email="j.smith@example.edu"
    )
    manager.register_irb_approval(irb)
    
    # Update compliance checks
    manager.update_compliance_status("IRB_001", ComplianceStatus.APPROVED, "IRB_approval_letter.pdf")
    manager.update_compliance_status("HIPAA_001", ComplianceStatus.APPROVED, "HIPAA_compliance_cert.pdf")
    
    # Get dashboard
    dashboard = manager.get_compliance_dashboard()
    
    print("\n" + "="*70)
    print("  Compliance Dashboard")
    print("="*70)
    print(f"IRB Approvals: {dashboard['irb_approvals']['active']} active, "
          f"{dashboard['irb_approvals']['expired']} expired")
    print(f"Compliance Checks: {dashboard['compliance_checks']['approved_percentage']:.0f}% approved")
    print(f"Adverse Events: {dashboard['adverse_events']['total']} total, "
          f"{dashboard['adverse_events']['serious_events']} serious")
    print(f"\nReady for Pilot Launch: "
          f"{'✓ YES' if dashboard['phase20_compliance']['ready_for_pilot_launch'] else '✗ NO'}")
    

if __name__ == '__main__':
    main()
