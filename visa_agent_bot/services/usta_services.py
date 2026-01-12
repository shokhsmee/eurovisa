# -*- coding: utf-8 -*-
import logging
from typing import Optional

_logger = logging.getLogger(__name__)

def find_employee_by_telegram(env, tg_user_id):
    """Find employee by Telegram user ID"""
    return env["hr.employee"].sudo().search([
        ("tg_user_id", "=", str(tg_user_id))
    ], limit=1)

def find_employee_by_phone(env, phone):
    """Find employee by phone number"""
    return env["hr.employee"].sudo().search([
        ("mobile_phone", "=", phone)
    ], limit=1) or env["hr.employee"].sudo().search([
        ("work_phone", "=", phone)
    ], limit=1)

def normalize_phone(phone):
    """Normalize phone to +998XXXXXXXXX format"""
    import re
    phone = re.sub(r'[^\d+]', '', phone)
    
    if phone.startswith('+998'):
        return phone
    elif phone.startswith('998'):
        return '+' + phone
    elif phone.startswith('8') and len(phone) == 12:
        return '+998' + phone[1:]
    elif len(phone) == 9:
        return '+998' + phone
    
    return phone

# ===== CRM FUNCTIONS =====

def get_agent_crm_leads(env, employee):
    """Get all CRM leads assigned to this agent"""
    if not employee.user_id:
        return env["crm.lead"].sudo().browse([])
    
    # Search by visa_agent_id (which is res.users)
    return env["crm.lead"].sudo().search([
        ("visa_agent_id", "=", employee.user_id.id),
        ("type", "=", "opportunity")
    ], order="service_number desc")


def search_crm_leads_by_service_number(env, query):
    """
    Search CRM leads by service number with partial matching
    Returns all CRM leads that match the query
    """
    if not query:
        return env["crm.lead"].sudo().browse([])
    
    # Remove any spaces and special characters
    clean_query = query.replace(" ", "").replace("-", "").upper()
    
    # Search with ILIKE for partial matching
    # This will find: CRM-12345, CRM-1234, 12345, etc.
    leads = env["crm.lead"].sudo().search([
        ("service_number", "ilike", f"%{clean_query}%"),
        ("type", "=", "opportunity")
    ], order="service_number desc", limit=50)
    
    return leads


def get_taklifnoma_document(env, lead_id):
    """Get Taklifnoma document for a CRM lead"""
    lead = env["crm.lead"].sudo().browse(lead_id)
    if not lead:
        return None
    
    # Find document type "Taklifnoma"
    doc_type = env["res.partner.document.type"].sudo().search([
        ("name", "ilike", "taklifnoma")
    ], limit=1)
    
    if not doc_type:
        _logger.warning("Taklifnoma document type not found!")
        return None
    
    # Search in CRM lead documents (not partner documents)
    doc = env["crm.lead.document"].sudo().search([
        ("crm_lead_id", "=", lead_id),
        ("type_id", "=", doc_type.id)
    ], limit=1)
    
    return doc


def create_or_get_taklifnoma_doc(env, lead_id):
    """Create Taklifnoma document for CRM lead if not exists"""
    lead = env["crm.lead"].sudo().browse(lead_id)
    if not lead:
        _logger.error(f"CRM lead {lead_id} not found!")
        return None
    
    # Find document type "Taklifnoma"
    doc_type = env["res.partner.document.type"].sudo().search([
        ("name", "ilike", "taklifnoma")
    ], limit=1)
    
    if not doc_type:
        _logger.error("Taklifnoma document type not found!")
        return None
    
    # Check if exists in CRM lead documents
    doc = env["crm.lead.document"].sudo().search([
        ("crm_lead_id", "=", lead_id),
        ("type_id", "=", doc_type.id)
    ], limit=1)
    
    # Create if not exists
    if not doc:
        doc = env["crm.lead.document"].sudo().create({
            "crm_lead_id": lead_id,
            "type_id": doc_type.id,
        })
        _logger.info(f"Created Taklifnoma document for CRM lead {lead_id}")
    
    return doc


def get_agent_balance(env, employee):
    """Get agent balance (placeholder)"""
    # TODO: Implement actual balance calculation
    # This could be based on:
    # - Commission from completed leads
    # - Bonuses
    # - Penalties
    # - etc.
    return 0.0