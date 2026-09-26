"""Local Audit Logger for MVP - Local file-based audit storage"""

import json
import os
from datetime import datetime
from typing import Dict, Any, Optional

from shared.models import AuditEvent


class LocalAuditLogger:
    """
    Local audit logger simulates S3 for MVP.
    Records audit events to local JSON files.
    """

    def __init__(self, data_dir: str = "data/audit"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)

    def log_event(self, audit_event: AuditEvent) -> bool:
        """
        Log an audit event to local storage.
        
        Args:
            audit_event: AuditEvent object
            
        Returns:
            bool: Success status
        """
        try:
            event_file = f"{self.data_dir}/event_{audit_event.event_id}.json"
            
            # Convert datetime to ISO format
            event_dict = {
                'event_id': audit_event.event_id,
                'timestamp': audit_event.timestamp.isoformat(),
                'actor': audit_event.actor,
                'action': audit_event.action,
                'details': audit_event.details,
                'incident_id': audit_event.incident_id
            }
            
            with open(event_file, 'w') as f:
                json.dump(event_dict, f, indent=2)
            
            return True
            
        except Exception:
            return False

    def get_events_by_incident(self, incident_id: str) -> list:
        """
        Retrieve all audit events for an incident.
        
        Args:
            incident_id: Incident identifier
            
        Returns:
            List of audit events
        """
        events = []
        
        for filename in os.listdir(self.data_dir):
            if filename.endswith('.json'):
                try:
                    with open(f"{self.data_dir}/{filename}", 'r') as f:
                        event = json.load(f)
                        if event.get('incident_id') == incident_id:
                            # Convert timestamp back to datetime
                            event['timestamp'] = datetime.fromisoformat(event['timestamp'])
                            events.append(event)
                except Exception:
                    continue
        
        # Sort by timestamp
        events.sort(key=lambda x: x['timestamp'])
        return events

    def get_events_by_actor(self, actor: str) -> list:
        """
        Retrieve all audit events by a specific actor.
        
        Args:
            actor: Actor name (component name)
            
        Returns:
            List of audit events
        """
        events = []
        
        for filename in os.listdir(self.data_dir):
            if filename.endswith('.json'):
                try:
                    with open(f"{self.data_dir}/{filename}", 'r') as f:
                        event = json.load(f)
                        if event.get('actor') == actor:
                            event['timestamp'] = datetime.fromisoformat(event['timestamp'])
                            events.append(event)
                except Exception:
                    continue
        
        events.sort(key=lambda x: x['timestamp'])
        return events