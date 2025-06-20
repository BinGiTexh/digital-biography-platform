#!/usr/bin/env python3
"""
Twitter Agent for BingiTech Platform
Handles Twitter/X integration for content posting and engagement
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class TwitterAgent:
    """Twitter/X integration agent for BingiTech"""
    
    def __init__(self, test_mode=True):
        self.test_mode = test_mode
        self.api_credentials = self.load_credentials()
        
        # Setup paths
        self.workspace = Path(__file__).parent.parent.parent / "clients" / "bingitech"
        self.content_path = self.workspace / "content" / "generated"
        
        print(f"🐦 Twitter Agent initialized (Test Mode: {test_mode})")
        print(f"📁 Content path: {self.content_path}")
        
        if not self.test_mode and not self.api_credentials:
            print("❌ Twitter API credentials not configured")
            sys.exit(1)
    
    def load_credentials(self):
        """Load Twitter API credentials from environment"""
        credentials = {
            'api_key': os.getenv('X_API_KEY'),
            'api_secret': os.getenv('X_API_SECRET'),
            'bearer_token': os.getenv('X_BEARER_TOKEN'),
            'access_token': os.getenv('X_ACCESS_TOKEN'),
            'access_token_secret': os.getenv('X_ACCESS_TOKEN_SECRET')
        }
        
        # Check if credentials are configured
        missing_creds = [key for key, value in credentials.items() 
                        if not value or value == f'your-{key.replace("_", "-")}-here']
        
        if missing_creds and not self.test_mode:
            print(f"❌ Missing Twitter credentials: {missing_creds}")
            return None
        
        if not missing_creds:
            print("✅ Twitter credentials loaded")
        else:
            print("⚠️  Twitter credentials not configured (test mode)")
        
        return credentials if not missing_creds else None
    
    def get_draft_posts(self):
        """Get all draft Twitter posts from content directory"""
        if not self.content_path.exists():
            print("❌ Content directory not found")
            return []
        
        twitter_posts = []
        for file_path in self.content_path.glob("*twitter*.json"):
            try:
                with open(file_path, 'r') as f:
                    post_data = json.load(f)
                    if post_data.get('platform') == 'twitter' and post_data.get('status') == 'draft':
                        post_data['file_path'] = str(file_path)
                        twitter_posts.append(post_data)
            except Exception as e:
                print(f"❌ Error reading {file_path}: {e}")
        
        return twitter_posts
    
    def validate_post(self, post_content):
        """Validate Twitter post content"""
        if not post_content:
            return False, "Empty content"
        
        if len(post_content) > 280:
            return False, f"Content too long: {len(post_content)} characters (max 280)"
        
        return True, "Valid"
    
    def preview_post(self, post_data):
        """Preview a Twitter post"""
        content = post_data.get('content', '')
        pillar = post_data.get('pillar', 'general')
        created_at = post_data.get('created_at', '')
        
        print(f"\\n📝 Post Preview:")
        print(f"Content Pillar: {pillar}")
        print(f"Created: {created_at}")
        print(f"Characters: {len(content)}/280")
        print("-" * 50)
        print(content)
        print("-" * 50)
        
        is_valid, message = self.validate_post(content)
        if is_valid:
            print("✅ Post is valid")
        else:
            print(f"❌ Post validation failed: {message}")
        
        return is_valid
    
    def post_to_twitter(self, post_data):
        """Post content to Twitter (mock implementation for testing)"""
        if self.test_mode:
            return self.mock_post_to_twitter(post_data)
        
        # Real Twitter API implementation would go here
        # For now, return mock success
        return {
            'success': True,
            'post_id': f"mock_id_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'message': 'Posted successfully (mock)'
        }
    
    def mock_post_to_twitter(self, post_data):
        """Mock Twitter posting for testing"""
        content = post_data.get('content', '')
        
        print(f"\\n🧪 MOCK TWITTER POST")
        print(f"Account: @BingiTech (Test Mode)")
        print(f"Content: {content}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"Status: Would be posted if API credentials were configured")
        
        return {
            'success': True,
            'post_id': f"test_post_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'message': 'Mock post created successfully'
        }
    
    def update_post_status(self, post_data, status='posted'):
        """Update the status of a post in the JSON file"""
        file_path = post_data.get('file_path')
        if not file_path:
            return False
        
        try:
            # Update the post data
            post_data['status'] = status
            post_data['posted_at'] = datetime.now().isoformat()
            
            # Remove file_path from data before saving
            save_data = {k: v for k, v in post_data.items() if k != 'file_path'}
            
            with open(file_path, 'w') as f:
                json.dump(save_data, f, indent=2)
            
            print(f"📝 Post status updated to: {status}")
            return True
        except Exception as e:
            print(f"❌ Error updating post status: {e}")
            return False
    
    def run_test_posting(self):
        """Test the posting workflow"""
        print("\\n🧪 Testing Twitter integration...")
        
        # Get draft posts
        draft_posts = self.get_draft_posts()
        
        if not draft_posts:
            print("❌ No draft Twitter posts found")
            print("💡 Generate content first with: make generate-content")
            return
        
        print(f"📋 Found {len(draft_posts)} draft Twitter posts")
        
        for i, post in enumerate(draft_posts, 1):
            print(f"\\n--- Post {i}/{len(draft_posts)} ---")
            
            # Preview the post
            is_valid = self.preview_post(post)
            
            if is_valid:
                # Ask for confirmation in test mode
                if self.test_mode:
                    response = input("\\n💭 Would you like to 'post' this? (y/n): ").lower().strip()
                    if response == 'y':
                        result = self.post_to_twitter(post)
                        if result['success']:
                            self.update_post_status(post, 'posted')
                            print(f"✅ {result['message']}")
                        else:
                            print(f"❌ Posting failed: {result.get('message', 'Unknown error')}")
                    else:
                        print("⏭️ Skipped")
                else:
                    # Auto-post in production mode
                    result = self.post_to_twitter(post)
                    if result['success']:
                        self.update_post_status(post, 'posted')
                        print(f"✅ {result['message']}")
            else:
                print("⚠️ Skipping invalid post")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='BingiTech Twitter Agent')
    parser.add_argument('--test', action='store_true', help='Run in test mode')
    parser.add_argument('--post', action='store_true', help='Post to Twitter (requires API keys)')
    
    args = parser.parse_args()
    
    # Default to test mode unless explicitly posting
    test_mode = args.test or not args.post
    
    print("🐦 BingiTech Twitter Agent")
    print("=" * 30)
    
    agent = TwitterAgent(test_mode=test_mode)
    agent.run_test_posting()
    
    print("\\n🎉 Twitter agent execution complete!")
    
    if test_mode:
        print("\\n📋 Next steps:")
        print("1. Configure Twitter API credentials in .env")
        print("2. Run with --post flag to actually post to Twitter")
        print("3. Review posted content in the content directory")

if __name__ == "__main__":
    main()

