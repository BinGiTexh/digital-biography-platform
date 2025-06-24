#!/usr/bin/env python3
"""
AI Cost Tracker - Sends cost summaries to Discord
Integrates with AI services for automatic cost logging
"""
import os
import json
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

class CostTracker:
    def __init__(self):
        self.discord_webhook = os.getenv('DISCORD_COST_WEBHOOK_URL')
        self.costs_file = 'costs_log.json'
        
        # Cost estimates per service (update these based on actual pricing)
        self.cost_estimates = {
            'ideogram': {
                'QUALITY': 0.32,  # per image
                'BALANCED': 0.16,
                'FAST': 0.08
            },
            'openai': {
                'gpt-4': 0.03,  # per 1k tokens
                'gpt-3.5-turbo': 0.002
            },
            'cascade': {
                'session': 2.50,  # estimated per coding session
                'tool_calls': 0.10  # per tool call
            }
        }
        
    def auto_log_ideogram(self, count=1, quality='QUALITY'):
        """Automatically log Ideogram costs"""
        cost = self.cost_estimates['ideogram'][quality] * count
        return self.log_cost('Ideogram', f'image_generation_{quality.lower()}', cost, {
            'count': count,
            'quality': quality
        })
    
    def auto_log_cascade(self, session_type='session', tool_calls=0):
        """Automatically log Cascade costs"""
        if session_type == 'session':
            cost = self.cost_estimates['cascade']['session']
        else:
            cost = self.cost_estimates['cascade']['tool_calls'] * tool_calls
            
        return self.log_cost('Cascade', session_type, cost, {
            'tool_calls': tool_calls if tool_calls else None
        })
        
    def log_cost(self, service, operation, cost, details=None):
        """Log a cost entry"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'service': service,
            'operation': operation,
            'cost': cost,
            'details': details or {}
        }
        
        # Load existing costs
        costs = self.load_costs()
        costs.append(entry)
        
        # Save updated costs
        with open(self.costs_file, 'w') as f:
            json.dump(costs, f, indent=2)
            
        return entry
    
    def load_costs(self):
        """Load existing cost log"""
        try:
            with open(self.costs_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def get_daily_summary(self, date=None):
        """Get cost summary for a specific date"""
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
            
        costs = self.load_costs()
        daily_costs = [c for c in costs if c['timestamp'].startswith(date)]
        
        summary = {}
        total = 0
        
        for cost in daily_costs:
            service = cost['service']
            if service not in summary:
                summary[service] = {'count': 0, 'total': 0, 'operations': []}
            
            summary[service]['count'] += 1
            summary[service]['total'] += cost['cost']
            summary[service]['operations'].append(cost['operation'])
            total += cost['cost']
        
        return {
            'date': date,
            'total': total,
            'by_service': summary,
            'entries': daily_costs
        }
    
    def get_weekly_summary(self):
        """Get cost summary for the past 7 days"""
        costs = self.load_costs()
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        
        weekly_costs = [c for c in costs if c['timestamp'] >= week_ago]
        
        summary = {}
        total = 0
        
        for cost in weekly_costs:
            service = cost['service']
            if service not in summary:
                summary[service] = {'count': 0, 'total': 0}
            
            summary[service]['count'] += 1
            summary[service]['total'] += cost['cost']
            total += cost['cost']
        
        return {
            'period': '7 days',
            'total': total,
            'by_service': summary,
            'entries': len(weekly_costs)
        }
    
    def send_to_discord(self, message, title="AI Cost Update"):
        """Send cost update to Discord"""
        if not self.discord_webhook:
            print("⚠️ Discord webhook not configured")
            return False
            
        payload = {
            "embeds": [{
                "title": title,
                "description": message,
                "color": 0x00ff00 if "No costs" in message else 0x3498db,
                "timestamp": datetime.now().isoformat(),
                "footer": {
                    "text": "BingiTech Digital Biography Platform"
                }
            }]
        }
        
        try:
            response = requests.post(self.discord_webhook, json=payload)
            response.raise_for_status()
            print("✅ Cost update sent to Discord")
            return True
        except Exception as e:
            print(f"❌ Failed to send to Discord: {e}")
            return False
    
    def daily_report(self):
        """Generate and send daily cost report"""
        summary = self.get_daily_summary()
        
        if summary['total'] == 0:
            message = "No AI costs recorded today. 🎉"
        else:
            message = f"**Daily AI Costs: ${summary['total']:.2f}**\n\n"
            
            for service, data in summary['by_service'].items():
                message += f"**{service}**: ${data['total']:.2f} ({data['count']} operations)\n"
                operations = list(set(data['operations']))
                if len(operations) <= 3:
                    message += f"  Operations: {', '.join(operations)}\n\n"
                else:
                    message += f"  Operations: {', '.join(operations[:3])} + {len(operations)-3} more\n\n"
        
        # Add weekly context
        weekly = self.get_weekly_summary()
        message += f"**7-day total**: ${weekly['total']:.2f} ({weekly['entries']} operations)"
        
        self.send_to_discord(message, f"Daily AI Cost Report - {summary['date']}")
        return summary

def main():
    """CLI interface"""
    import sys
    
    tracker = CostTracker()
    
    if len(sys.argv) < 2:
        print("Usage: python cost_tracker.py [log|report|summary|auto-ideogram|auto-cascade]")
        return
    
    command = sys.argv[1]
    
    if command == "log":
        if len(sys.argv) < 5:
            print("Usage: python cost_tracker.py log <service> <operation> <cost>")
            return
        service, operation, cost = sys.argv[2], sys.argv[3], float(sys.argv[4])
        entry = tracker.log_cost(service, operation, cost)
        print(f"✅ Logged: {service} - {operation} - ${cost}")
        
    elif command == "auto-ideogram":
        count = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        quality = sys.argv[3] if len(sys.argv) > 3 else 'QUALITY'
        entry = tracker.auto_log_ideogram(count, quality)
        print(f"✅ Auto-logged Ideogram: {count} images at {quality} - ${entry['cost']}")
        
    elif command == "auto-cascade":
        session_type = sys.argv[2] if len(sys.argv) > 2 else 'session'
        tool_calls = int(sys.argv[3]) if len(sys.argv) > 3 else 0
        entry = tracker.auto_log_cascade(session_type, tool_calls)
        print(f"✅ Auto-logged Cascade: {session_type} - ${entry['cost']}")
        
    elif command == "report":
        summary = tracker.daily_report()
        print(f"Daily total: ${summary['total']:.2f}")
        
    elif command == "summary":
        summary = tracker.get_daily_summary()
        print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
