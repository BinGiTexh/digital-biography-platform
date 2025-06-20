#!/usr/bin/env python3
"""
Discord Agent for BingiTech Platform
Sends content drafts to Discord for review and approval
"""

import os
import json
import requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DiscordAgent:
    """Discord integration agent for BingiTech content review"""
    
    def __init__(self):
        self.webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
        
        # Setup paths
        self.workspace = Path(__file__).parent.parent.parent / "clients" / "bingitech"
        self.content_path = self.workspace / "content" / "generated"
        
        print(f"🎮 Discord Agent initialized")
        print(f"📁 Content path: {self.content_path}")
        print(f"🔗 Webhook configured: {bool(self.webhook_url)}")
        
        if not self.webhook_url:
            print("⚠️  Discord webhook not configured")
            print("💡 Add DISCORD_WEBHOOK_URL to .env to enable Discord integration")
    
    def get_draft_posts(self, platform=None):
        """Get all draft posts from content directory"""
        if not self.content_path.exists():
            print("❌ Content directory not found")
            return []
        
        posts = []
        pattern = f"*{platform}*.json" if platform else "*.json"
        
        for file_path in self.content_path.glob(pattern):
            try:
                with open(file_path, 'r') as f:
                    post_data = json.load(f)
                    if post_data.get('status') == 'draft':
                        post_data['file_path'] = str(file_path)
                        posts.append(post_data)
            except Exception as e:
                print(f"❌ Error reading {file_path}: {e}")
        
        return sorted(posts, key=lambda x: x.get('created_at', ''))
    
    def format_discord_message(self, post_data):
        """Format post data for Discord message"""
        content = post_data.get('content', '')
        platform = post_data.get('platform', 'unknown')
        pillar = post_data.get('pillar', 'general')
        created_at = post_data.get('created_at', '')
        
        # Create Discord embed
        embed = {
            "title": f"📝 BingiTech {platform.title()} Draft",
            "description": content,
            "color": 0x1DA1F2 if platform == 'twitter' else 0x0077B5,  # Twitter blue or LinkedIn blue
            "fields": [
                {
                    "name": "📊 Content Pillar",
                    "value": pillar.replace('_', ' ').title(),
                    "inline": True
                },
                {
                    "name": "📱 Platform",
                    "value": platform.title(),
                    "inline": True
                },
                {
                    "name": "📏 Length",
                    "value": f"{len(content)} characters",
                    "inline": True
                }
            ],
            "footer": {
                "text": f"Created: {created_at[:19].replace('T', ' ')}"
            },
            "timestamp": datetime.now().isoformat()
        }
        
        # Add reaction buttons for approval
        message = {
            "embeds": [embed],
            "content": f"**New BingiTech {platform.title()} Draft Ready for Review**\\n\\n"
                      f"React with:\\n"
                      f"✅ to approve\\n"
                      f"❌ to reject\\n"
                      f"✏️ to edit\\n"
        }
        
        return message
    
    def send_to_discord(self, post_data):
        """Send post draft to Discord webhook"""
        if not self.webhook_url:
            print("❌ Discord webhook not configured")
            return False
        
        try:
            message = self.format_discord_message(post_data)
            
            response = requests.post(
                self.webhook_url,
                json=message,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 204:
                print("✅ Draft sent to Discord successfully")
                # Update the post status to 'discord_sent'
                self.update_post_status(post_data, 'discord_sent')
                return True
            else:
                print(f"❌ Discord webhook failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending to Discord: {e}")
            return False
    
    def send_mock_to_discord(self, post_data):
        """Mock Discord sending for testing"""
        print(f"\\n🎮 MOCK DISCORD MESSAGE")
        print(f"Channel: #bingitech-content-review")
        print(f"=" * 50)
        
        content = post_data.get('content', '')
        platform = post_data.get('platform', 'unknown')
        pillar = post_data.get('pillar', 'general')
        
        print(f"📝 **BingiTech {platform.title()} Draft**")
        print(f"📊 Content Pillar: {pillar.replace('_', ' ').title()}")
        print(f"📏 Length: {len(content)} characters")
        print()
        print(f"**Content:**")
        print(f"```")
        print(content)
        print(f"```")
        print()
        print(f"React with: ✅ (approve) | ❌ (reject) | ✏️ (edit)")
        print(f"=" * 50)
        
        return True
    
    def update_post_status(self, post_data, status='discord_sent'):
        """Update the status of a post in the JSON file"""
        file_path = post_data.get('file_path')
        if not file_path:
            return False
        
        try:
            # Update the post data
            post_data['status'] = status
            post_data['discord_sent_at'] = datetime.now().isoformat()
            
            # Remove file_path from data before saving
            save_data = {k: v for k, v in post_data.items() if k != 'file_path'}
            
            with open(file_path, 'w') as f:
                json.dump(save_data, f, indent=2)
            
            print(f"📝 Post status updated to: {status}")
            return True
        except Exception as e:
            print(f"❌ Error updating post status: {e}")
            return False
    
    def send_content_summary(self, posts):
        """Send a summary of all draft posts to Discord"""
        if not posts:
            print("📭 No draft posts to send")
            return
        
        # Group posts by platform
        by_platform = {}
        for post in posts:
            platform = post.get('platform', 'unknown')
            if platform not in by_platform:
                by_platform[platform] = []
            by_platform[platform].append(post)
        
        print(f"\\n📋 SENDING {len(posts)} DRAFTS TO DISCORD")
        print(f"=" * 50)
        
        for platform, platform_posts in by_platform.items():
            print(f"\\n📱 {platform.upper()} POSTS ({len(platform_posts)}):")
            for i, post in enumerate(platform_posts, 1):
                print(f"\\n--- Draft {i} ---")
                if self.webhook_url:
                    success = self.send_to_discord(post)
                else:
                    success = self.send_mock_to_discord(post)
                
                if not success:
                    print(f"⚠️ Failed to send draft {i}")
    
    def run_discord_review(self):
        """Main workflow: send all drafts to Discord for review"""
        print("\\n🎮 Starting Discord content review...")
        
        # Get all draft posts
        draft_posts = self.get_draft_posts()
        
        if not draft_posts:
            print("📭 No draft posts found")
            print("💡 Generate content first with: make generate-content")
            return
        
        print(f"📋 Found {len(draft_posts)} draft posts")
        
        # Send to Discord
        self.send_content_summary(draft_posts)
        
        print(f"\\n🎉 Discord review process complete!")
        if not self.webhook_url:
            print("\\n💡 To enable real Discord integration:")
            print("1. Create a Discord webhook in your server")
            print("2. Add DISCORD_WEBHOOK_URL to your .env file")
            print("3. Run this command again")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='BingiTech Discord Agent')
    parser.add_argument('--platform', choices=['twitter', 'linkedin'], help='Filter by platform')
    
    args = parser.parse_args()
    
    print("🎮 BingiTech Discord Agent")
    print("=" * 30)
    
    agent = DiscordAgent()
    agent.run_discord_review()

if __name__ == "__main__":
    main()

