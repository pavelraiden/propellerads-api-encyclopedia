#!/usr/bin/env python3
"""
Checklist Manager for PropellerAds Campaign Operations

This module provides checklist functionality for systematic campaign management,
ensuring all critical steps are followed and verified.
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class ChecklistStatus(Enum):
    """Status of checklist items"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class ChecklistItem:
    """Individual checklist item"""
    id: str
    title: str
    description: str
    status: ChecklistStatus = ChecklistStatus.PENDING
    completed_at: Optional[datetime] = None
    notes: str = ""
    required: bool = True


@dataclass
class Checklist:
    """Complete checklist for a task"""
    id: str
    title: str
    description: str
    items: List[ChecklistItem]
    created_at: datetime
    completed_at: Optional[datetime] = None
    status: ChecklistStatus = ChecklistStatus.PENDING


class ChecklistManager:
    """Manages checklists for PropellerAds operations"""
    
    def __init__(self):
        self.checklists: Dict[str, Checklist] = {}
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load predefined checklist templates"""
        return {
            "campaign_creation": [
                {
                    "title": "Gather Required Information",
                    "description": "Collect all necessary campaign details",
                    "required": True
                },
                {
                    "title": "Verify Product/Service Details",
                    "description": "Confirm what is being advertised",
                    "required": True
                },
                {
                    "title": "Validate Landing Page URL",
                    "description": "Ensure landing page is accessible and compliant",
                    "required": True
                },
                {
                    "title": "Set Geographic Targeting",
                    "description": "Define target countries/regions",
                    "required": True
                },
                {
                    "title": "Configure Device Targeting",
                    "description": "Set mobile/desktop preferences",
                    "required": True
                },
                {
                    "title": "Separate 3G and WiFi Traffic",
                    "description": "CRITICAL: Create separate campaigns for 3G and WiFi",
                    "required": True
                },
                {
                    "title": "Set Budget and Bidding",
                    "description": "Configure daily budget and bid strategy",
                    "required": True
                },
                {
                    "title": "Upload Creative Assets",
                    "description": "Add ad copy, images, and videos",
                    "required": True
                },
                {
                    "title": "Configure Conversion Tracking",
                    "description": "Set up tracking pixels and postback URLs",
                    "required": True
                },
                {
                    "title": "Review Campaign Settings",
                    "description": "Final review before submission",
                    "required": True
                },
                {
                    "title": "Submit as DRAFT",
                    "description": "Create campaign in DRAFT status initially",
                    "required": True
                }
            ],
            "campaign_optimization": [
                {
                    "title": "Analyze Current Performance",
                    "description": "Review CTR, CPC, CPA, ROI metrics",
                    "required": True
                },
                {
                    "title": "Identify Traffic Quality Issues",
                    "description": "Check for fraud indicators and low-quality sources",
                    "required": True
                },
                {
                    "title": "Analyze Audience Performance",
                    "description": "Review best/worst performing segments",
                    "required": True
                },
                {
                    "title": "Review Creative Performance",
                    "description": "Identify top/bottom performing ads",
                    "required": True
                },
                {
                    "title": "Analyze Geographic Performance",
                    "description": "Review performance by country/region",
                    "required": True
                },
                {
                    "title": "Check Device Performance",
                    "description": "Compare mobile vs desktop effectiveness",
                    "required": True
                },
                {
                    "title": "Identify Time Patterns",
                    "description": "Find best performing hours/days",
                    "required": True
                },
                {
                    "title": "Create Optimization Plan",
                    "description": "Develop specific action items",
                    "required": True
                },
                {
                    "title": "Implement Changes",
                    "description": "Apply optimization recommendations",
                    "required": True
                },
                {
                    "title": "Monitor Results",
                    "description": "Track impact of optimization changes",
                    "required": True
                }
            ],
            "account_audit": [
                {
                    "title": "Check Account Balance",
                    "description": "Verify sufficient funds for campaigns",
                    "required": True
                },
                {
                    "title": "Review Active Campaigns",
                    "description": "Audit all running campaigns",
                    "required": True
                },
                {
                    "title": "Analyze Overall Performance",
                    "description": "Review account-wide metrics",
                    "required": True
                },
                {
                    "title": "Check Compliance Status",
                    "description": "Ensure all campaigns meet platform policies",
                    "required": True
                },
                {
                    "title": "Review Targeting Settings",
                    "description": "Audit targeting configurations",
                    "required": True
                },
                {
                    "title": "Analyze Budget Allocation",
                    "description": "Review budget distribution across campaigns",
                    "required": True
                },
                {
                    "title": "Check Creative Assets",
                    "description": "Review all ad creatives for compliance",
                    "required": True
                },
                {
                    "title": "Verify Tracking Setup",
                    "description": "Ensure conversion tracking is working",
                    "required": True
                },
                {
                    "title": "Generate Recommendations",
                    "description": "Create action plan for improvements",
                    "required": True
                }
            ]
        }
    
    def create_checklist(self, template_name: str, title: str = None, description: str = None) -> str:
        """Create a new checklist from template"""
        if template_name not in self.templates:
            raise ValueError(f"Template '{template_name}' not found")
        
        checklist_id = str(uuid.uuid4())
        template_items = self.templates[template_name]
        
        items = []
        for i, item_data in enumerate(template_items):
            item = ChecklistItem(
                id=f"{checklist_id}_{i}",
                title=item_data["title"],
                description=item_data["description"],
                required=item_data.get("required", True)
            )
            items.append(item)
        
        checklist = Checklist(
            id=checklist_id,
            title=title or f"{template_name.replace('_', ' ').title()} Checklist",
            description=description or f"Systematic checklist for {template_name.replace('_', ' ')}",
            items=items,
            created_at=datetime.now()
        )
        
        self.checklists[checklist_id] = checklist
        return checklist_id
    
    def get_checklist(self, checklist_id: str) -> Optional[Checklist]:
        """Get checklist by ID"""
        return self.checklists.get(checklist_id)
    
    def update_item_status(self, checklist_id: str, item_id: str, status: ChecklistStatus, notes: str = "") -> bool:
        """Update status of a checklist item"""
        checklist = self.checklists.get(checklist_id)
        if not checklist:
            return False
        
        for item in checklist.items:
            if item.id == item_id:
                item.status = status
                item.notes = notes
                if status == ChecklistStatus.COMPLETED:
                    item.completed_at = datetime.now()
                
                # Check if all required items are completed
                required_items = [i for i in checklist.items if i.required]
                completed_required = [i for i in required_items if i.status == ChecklistStatus.COMPLETED]
                
                if len(completed_required) == len(required_items):
                    checklist.status = ChecklistStatus.COMPLETED
                    checklist.completed_at = datetime.now()
                
                return True
        
        return False
    
    def get_checklist_progress(self, checklist_id: str) -> Dict[str, Any]:
        """Get progress summary for a checklist"""
        checklist = self.checklists.get(checklist_id)
        if not checklist:
            return {}
        
        total_items = len(checklist.items)
        completed_items = len([i for i in checklist.items if i.status == ChecklistStatus.COMPLETED])
        required_items = len([i for i in checklist.items if i.required])
        completed_required = len([i for i in checklist.items if i.required and i.status == ChecklistStatus.COMPLETED])
        
        progress_percentage = (completed_items / total_items * 100) if total_items > 0 else 0
        required_progress = (completed_required / required_items * 100) if required_items > 0 else 0
        
        return {
            "checklist_id": checklist_id,
            "title": checklist.title,
            "status": checklist.status.value,
            "total_items": total_items,
            "completed_items": completed_items,
            "required_items": required_items,
            "completed_required": completed_required,
            "progress_percentage": round(progress_percentage, 1),
            "required_progress": round(required_progress, 1),
            "is_complete": checklist.status == ChecklistStatus.COMPLETED,
            "created_at": checklist.created_at.isoformat(),
            "completed_at": checklist.completed_at.isoformat() if checklist.completed_at else None
        }
    
    def export_checklist(self, checklist_id: str) -> Dict[str, Any]:
        """Export checklist to JSON format"""
        checklist = self.checklists.get(checklist_id)
        if not checklist:
            return {}
        
        return {
            "checklist": asdict(checklist),
            "progress": self.get_checklist_progress(checklist_id)
        }
    
    def get_available_templates(self) -> List[str]:
        """Get list of available checklist templates"""
        return list(self.templates.keys())
    
    def generate_claude_checklist_prompt(self, checklist_id: str) -> str:
        """Generate a prompt for Claude to follow the checklist"""
        checklist = self.checklists.get(checklist_id)
        if not checklist:
            return ""
        
        prompt = f"📋 **{checklist.title}**\n\n"
        prompt += f"{checklist.description}\n\n"
        prompt += "**CHECKLIST TO FOLLOW:**\n\n"
        
        for i, item in enumerate(checklist.items, 1):
            status_emoji = "✅" if item.status == ChecklistStatus.COMPLETED else "⏳"
            required_marker = " (REQUIRED)" if item.required else " (OPTIONAL)"
            
            prompt += f"{i}. {status_emoji} **{item.title}**{required_marker}\n"
            prompt += f"   {item.description}\n\n"
        
        prompt += "**INSTRUCTIONS:**\n"
        prompt += "- Follow each step systematically\n"
        prompt += "- Mark each step as ✅ when completed\n"
        prompt += "- Ask for clarification if any step is unclear\n"
        prompt += "- Do not skip required steps\n"
        
        return prompt


# Global checklist manager instance
checklist_manager = ChecklistManager()


def create_campaign_checklist() -> str:
    """Create a campaign creation checklist"""
    return checklist_manager.create_checklist("campaign_creation")


def create_optimization_checklist() -> str:
    """Create a campaign optimization checklist"""
    return checklist_manager.create_checklist("campaign_optimization")


def create_audit_checklist() -> str:
    """Create an account audit checklist"""
    return checklist_manager.create_checklist("account_audit")


if __name__ == "__main__":
    # Test the checklist manager
    print("🔧 Testing Checklist Manager")
    print("=" * 50)
    
    # Create a test checklist
    checklist_id = create_campaign_checklist()
    print(f"Created checklist: {checklist_id}")
    
    # Get progress
    progress = checklist_manager.get_checklist_progress(checklist_id)
    print(f"Initial progress: {progress['progress_percentage']}%")
    
    # Complete first item
    checklist = checklist_manager.get_checklist(checklist_id)
    first_item = checklist.items[0]
    checklist_manager.update_item_status(checklist_id, first_item.id, ChecklistStatus.COMPLETED, "Test completion")
    
    # Get updated progress
    progress = checklist_manager.get_checklist_progress(checklist_id)
    print(f"Updated progress: {progress['progress_percentage']}%")
    
    # Generate Claude prompt
    prompt = checklist_manager.generate_claude_checklist_prompt(checklist_id)
    print("\nGenerated Claude prompt:")
    print(prompt[:200] + "...")
    
    print("✅ Checklist Manager test completed!")
