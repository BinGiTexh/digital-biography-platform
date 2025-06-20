#!/usr/bin/env python3
"""
BingiTech Digital Biography Agent System
Main orchestrator for content generation and social media management
"""

import os
import json
import asyncio
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class BingiTechAgentSystem:
    """Main agent system for BingiTech digital biography platform"""
    
    def __init__(self):
        self.workspace = Path(__file__).parent.parent / "clients" / "bingitech"
        self.config_path = self.workspace / "config" / "brand_config.json"
        self.content_path = self.workspace / "content"
        
        # Ensure directories exist
        self.content_path.mkdir(parents=True, exist_ok=True)
        (self.content_path / "generated").mkdir(exist_ok=True)
        
        # Load brand configuration
        self.brand_config = self.load_brand_config()
        
        print(f"🚀 BingiTech Agent System initialized")
        print(f"📁 Workspace: {self.workspace}")
        print(f"⚙️  Config loaded: {self.config_path.exists()}")
    
    def load_brand_config(self):
        """Load BingiTech brand configuration"""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            print("✅ Brand configuration loaded")
            return config
        except FileNotFoundError:
            print("❌ Brand configuration not found")
            return {}
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing brand configuration: {e}")
            return {}
    
    def generate_content_idea(self, pillar=None):
        """Generate a content idea based on brand pillars"""
        content_pillars = self.brand_config.get("content_pillars", [])
        
        if not pillar and content_pillars:
            # Select a pillar based on current focus
            pillar = content_pillars[0]  # For now, use first pillar
        
        ideas = {
            "software_development_insights": [
                "The evolution of our development workflow over the past year",
                "Why we chose microservices architecture for our latest project",
                "Debugging strategies that saved us hours of development time",
                "Code review practices that improved our team velocity"
            ],
            "technology_trends_analysis": [
                "How AI is reshaping software development in 2024",
                "The rise of serverless architecture: lessons learned",
                "Why we're excited about the future of web development",
                "Emerging technologies we're watching closely"
            ],
            "problem_solving_methodologies": [
                "Our approach to tackling complex technical challenges",
                "When to refactor vs. rebuild: a decision framework",
                "How we identify and eliminate technical debt",
                "Root cause analysis techniques that work"
            ],
            "team_leadership_in_tech": [
                "Building psychological safety in development teams",
                "Effective communication strategies for remote tech teams",
                "How we mentor junior developers",
                "Creating a culture of continuous learning"
            ]
        }
        
        if pillar in ideas:
            import random
            return {
                "pillar": pillar,
                "idea": random.choice(ideas[pillar]),
                "timestamp": datetime.now().isoformat()
            }
        
        return None
    
    def create_twitter_post(self, content_idea):
        """Create a Twitter post based on content idea"""
        # This would integrate with OpenAI API in a real implementation
        template_posts = {
            "software_development_insights": [
                "Just reflected on how our development workflow has evolved. The biggest game-changer? Implementing proper code review cycles. What seemed like a slowdown initially became our quality accelerator. #SoftwareDevelopment #BingiTech",
                "Microservices taught us that complexity doesn't disappear - it just moves around. The key is choosing where that complexity lives intentionally. #TechLeadership #Architecture"
            ],
            "technology_trends_analysis": [
                "AI pair programming is interesting, but it's not replacing the need for deep technical thinking. It's amplifying our ability to explore solutions faster. #AI #Development #BingiTech",
                "Serverless architecture has been a journey. The promise is real, but the learning curve is steeper than expected. Worth it for the right use cases. #Serverless #TechTrends"
            ]
        }
        
        pillar = content_idea.get("pillar", "")
        if pillar in template_posts:
            import random
            post_content = random.choice(template_posts[pillar])
            
            return {
                "platform": "twitter",
                "content": post_content,
                "pillar": pillar,
                "created_at": datetime.now().isoformat(),
                "status": "draft"
            }
        
        return None
    
    def create_linkedin_post(self, content_idea):
        """Create a LinkedIn post based on content idea"""
        template_posts = {
            "team_leadership_in_tech": """
Building effective tech teams isn't just about technical skills.

Over the past year, we've learned that psychological safety drives innovation more than any framework or tool. When developers feel safe to share incomplete ideas, ask questions, and admit mistakes, the whole team moves faster.

Here's what we've implemented:
• Weekly 'learning moments' where team members share recent discoveries
• Blameless post-mortems that focus on systems, not individuals  
• Dedicated time for experimentation and side projects

The result? Higher code quality, faster problem-solving, and better retention.

What practices have worked for your team?

#TechLeadership #TeamBuilding #BingiTech
            """.strip(),
            
            "problem_solving_methodologies": """
Every complex technical problem follows a pattern.

When facing a challenging issue, we've developed a systematic approach:

1. **Define the real problem** - Often what appears broken isn't the root cause
2. **Map the system** - Understand all components and their interactions
3. **Isolate variables** - Change one thing at a time
4. **Document everything** - Your future self will thank you
5. **Share the solution** - Turn individual learning into team knowledge

This framework has saved us countless hours and prevented recurring issues.

The key insight? Most technical problems are actually communication or process problems in disguise.

What's your approach to systematic problem-solving?

#ProblemSolving #TechnicalLeadership #BingiTech
            """.strip()
        }
        
        pillar = content_idea.get("pillar", "")
        if pillar in template_posts:
            return {
                "platform": "linkedin",
                "content": template_posts[pillar],
                "pillar": pillar,
                "created_at": datetime.now().isoformat(),
                "status": "draft"
            }
        
        return None
    
    def save_content(self, content):
        """Save generated content to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        platform = content.get("platform", "unknown")
        pillar = content.get("pillar", "general")
        
        filename = f"{timestamp}_{platform}_{pillar.replace(' ', '_')}.json"
        filepath = self.content_path / "generated" / filename
        
        try:
            with open(filepath, 'w') as f:
                json.dump(content, f, indent=2)
            print(f"💾 Content saved: {filepath}")
            return filepath
        except Exception as e:
            print(f"❌ Error saving content: {e}")
            return None
    
    def run_content_generation(self):
        """Main content generation workflow"""
        print("\n🎯 Starting content generation for BingiTech...")
        
        # Generate content ideas for different pillars
        pillars = self.brand_config.get("content_pillars", [])[:2]  # First 2 pillars
        
        generated_content = []
        
        for pillar in pillars:
            print(f"\n📝 Working on pillar: {pillar}")
            
            # Generate content idea
            idea = self.generate_content_idea(pillar)
            if not idea:
                continue
            
            print(f"💡 Content idea: {idea['idea']}")
            
            # Create posts for different platforms
            twitter_post = self.create_twitter_post(idea)
            if twitter_post:
                filepath = self.save_content(twitter_post)
                if filepath:
                    generated_content.append(twitter_post)
                    print(f"🐦 Twitter post created")
            
            linkedin_post = self.create_linkedin_post(idea)
            if linkedin_post:
                filepath = self.save_content(linkedin_post)
                if filepath:
                    generated_content.append(linkedin_post)
                    print(f"💼 LinkedIn post created")
        
        print(f"\n✅ Content generation complete!")
        print(f"📊 Generated {len(generated_content)} pieces of content")
        print(f"📁 Content saved in: {self.content_path / 'generated'}")
        
        return generated_content

def main():
    """Main entry point"""
    print("🚀 BingiTech Digital Biography Agent System")
    print("=" * 50)
    
    # Initialize agent system
    agent_system = BingiTechAgentSystem()
    
    # Run content generation
    content = agent_system.run_content_generation()
    
    print("\n🎉 Agent system execution complete!")
    print("Next steps:")
    print("1. Review generated content in clients/bingitech/content/generated/")
    print("2. Edit and approve content before posting")
    print("3. Use make test-twitter to test social media integration")

if __name__ == "__main__":
    main()

