#!/usr/bin/env python3
"""
GitHub Integration Agent for BingiTech Platform
Generates content based on GitHub repository activity with Jamaican tech themes
"""

import os
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class GitHubAgent:
    """GitHub integration agent for BingiTech content generation"""
    
    def __init__(self):
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.github_username = os.getenv('GITHUB_USERNAME', 'BinGiTexh')  # Default to your username
        
        # Setup paths
        self.workspace = Path(__file__).parent.parent.parent / "clients" / "bingitech"
        self.content_path = self.workspace / "content" / "generated"
        
        self.api_base = "https://api.github.com"
        
        print(f"🐙 GitHub Agent initialized")
        print(f"👤 Username: {self.github_username}")
        print(f"🔑 Token configured: {bool(self.github_token)}")
        print(f"📁 Content path: {self.content_path}")
    
    def get_recent_repos(self, limit=10):
        """Get recent repositories for the user"""
        url = f"{self.api_base}/users/{self.github_username}/repos"
        params = {
            'sort': 'updated',
            'direction': 'desc',
            'per_page': limit
        }
        
        headers = {}
        if self.github_token:
            headers['Authorization'] = f'token {self.github_token}'
        
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            
            repos = response.json()
            print(f"📊 Found {len(repos)} recent repositories")
            
            return repos
            
        except Exception as e:
            print(f"❌ Error fetching repositories: {e}")
            return self.get_mock_repos()
    
    def get_recent_commits(self, repo_name, limit=5):
        """Get recent commits for a specific repository"""
        url = f"{self.api_base}/repos/{self.github_username}/{repo_name}/commits"
        params = {'per_page': limit}
        
        headers = {}
        if self.github_token:
            headers['Authorization'] = f'token {self.github_token}'
        
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            
            commits = response.json()
            print(f"📝 Found {len(commits)} recent commits for {repo_name}")
            
            return commits
            
        except Exception as e:
            print(f"❌ Error fetching commits for {repo_name}: {e}")
            return []
    
    def get_mock_repos(self):
        """Mock repository data for testing"""
        return [
            {
                "name": "jamdungjobs",
                "description": "Job board platform for Jamaica with AI-powered features",
                "language": "Python",
                "updated_at": "2025-06-20T19:00:00Z",
                "html_url": "https://github.com/BinGiTexh/jamdungjobs",
                "topics": ["python", "jobs", "jamaica", "ai"]
            },
            {
                "name": "bingitech-digital-biography",
                "description": "AI-powered content creation platform for digital presence",
                "language": "Python",
                "updated_at": "2025-06-20T18:00:00Z", 
                "html_url": "https://github.com/BinGiTexh/bingitech-digital-biography",
                "topics": ["ai", "content", "social-media"]
            },
            {
                "name": "soccer-analytics-api",
                "description": "API for soccer match analysis and player statistics",
                "language": "JavaScript",
                "updated_at": "2025-06-19T15:00:00Z",
                "html_url": "https://github.com/BinGiTexh/soccer-analytics-api",
                "topics": ["soccer", "analytics", "api", "sports"]
            }
        ]
    
    def analyze_repo_for_content(self, repo):
        """Analyze repository to determine content themes and generate posts"""
        name = repo.get('name', '')
        description = repo.get('description', '')
        language = repo.get('language', '')
        topics = repo.get('topics', [])
        
        # Determine content themes based on repository
        content_themes = []
        
        if any(keyword in name.lower() or keyword in description.lower() 
               for keyword in ['job', 'career', 'work']):
            content_themes.append('jamaican_job_innovation')
            
        elif any(keyword in name.lower() or keyword in description.lower() 
                 for keyword in ['soccer', 'football', 'sport']):
            content_themes.append('soccer_tech_fusion')
            
        elif any(keyword in name.lower() or keyword in description.lower() 
                 for keyword in ['api', 'backend', 'service']):
            content_themes.append('backend_architecture')
            
        elif any(keyword in name.lower() or keyword in description.lower() 
                 for keyword in ['ai', 'ml', 'machine learning']):
            content_themes.append('ai_innovation')
        
        else:
            content_themes.append('general_tech_innovation')
        
        return content_themes
    
    def generate_repo_content(self, repo, platform="twitter"):
        """Generate social media content based on repository"""
        name = repo.get('name', '')
        description = repo.get('description', '')
        language = repo.get('language', '')
        url = repo.get('html_url', '')
        
        themes = self.analyze_repo_for_content(repo)
        
        # Generate content based on repository themes
        if 'jamaican_job_innovation' in themes:
            if platform == "twitter":
                content = f"Building opportunities for Jamaican talent 🇯🇲💼 Working on {name} - connecting skilled professionals with global opportunities. Innovation meets island pride! #{language}Development #JamaicanTech #BingiTech"
            else:  # LinkedIn
                content = f"""Excited to share progress on {name} - a platform designed to showcase Jamaican talent to the world.

{description}

Building this project reminds me why I love combining technology with social impact. Every feature we develop opens doors for skilled professionals from Jamaica to connect with global opportunities.

The intersection of Caribbean innovation and global tech needs is where magic happens. 

Built with {language} | Check it out: {url}

#JamaicanTech #BingiTech #Innovation #TechForGood"""
        
        elif 'soccer_tech_fusion' in themes:
            if platform == "twitter":
                content = f"When soccer strategy meets software architecture ⚽️💻 {name} combines the beautiful game with data insights. Every play analyzed, every pattern discovered! #{language} #SoccerTech #BingiTech"
            else:  # LinkedIn
                content = f"""The beautiful game teaches us about software development.

Working on {name} has shown me how soccer strategy principles apply directly to system architecture:

• Formation = System Design
• Player positioning = Service placement  
• Game flow = Data flow
• Team coordination = Microservice communication

{description}

Sports analytics isn't just about the game - it's about understanding patterns, optimizing performance, and making data-driven decisions. Skills that translate perfectly to tech.

Built with {language} | {url}

#SoccerTech #BingiTech #SystemsThinking #SportsAnalytics"""
        
        elif 'ai_innovation' in themes:
            if platform == "twitter":
                content = f"AI with a Caribbean twist 🤖🇯🇲 {name} showcases how innovation flows when you blend cutting-edge tech with cultural creativity. Building the future, island style! #AI #{language} #BingiTech"
            else:  # LinkedIn
                content = f"""Innovation happens when technology meets culture.

{name}: {description}

This project represents something special - AI development with a distinctly Caribbean perspective. We're not just building algorithms; we're infusing them with the creativity, problem-solving spirit, and community focus that defines Jamaican innovation.

The future of AI isn't just about computational power - it's about diverse perspectives shaping how technology serves humanity.

Built with {language} | Explore: {url}

#AI #BingiTech #Innovation #DiversityInTech #JamaicanTech"""
        
        else:  # General tech
            if platform == "twitter":
                content = f"Building with purpose 🚀 {name} represents hours of island innovation and global thinking. Every commit tells a story of persistence and creativity! #{language}Dev #BingiTech #Innovation"
            else:  # LinkedIn
                content = f"""Every project tells a story of growth and innovation.

{name}: {description}

Working on this {language} project has been a reminder of why I love building technology. Each feature developed, each problem solved, represents not just code but creativity, persistence, and the drive to build something meaningful.

This is what BingiTech represents - thoughtful development that bridges Caribbean innovation with global tech standards.

Check it out: {url}

#BingiTech #SoftwareDevelopment #{language} #Innovation #TechStory"""
        
        return {
            "platform": platform,
            "content": content,
            "pillar": themes[0] if themes else "general_tech_innovation",
            "repository": {
                "name": name,
                "description": description,
                "language": language,
                "url": url
            },
            "created_at": datetime.now().isoformat(),
            "status": "draft",
            "type": "github_post"
        }
    
    def generate_commit_story(self, repo_name, commits, platform="twitter"):
        """Generate content based on recent commit activity"""
        if not commits:
            return None
        
        recent_commit = commits[0]
        commit_message = recent_commit.get('commit', {}).get('message', '')
        
        if platform == "twitter":
            content = f"Just pushed an update to {repo_name} 🔄 {commit_message[:100]}... The grind never stops when you're building the future! #GitCommit #BingiTech #DevLife"
        else:  # LinkedIn
            content = f"""Progress update on {repo_name}

Latest commit: {commit_message}

There's something deeply satisfying about pushing clean, well-tested code. Each commit represents not just a feature or fix, but hours of problem-solving, research, and iteration.

This is the unsexy side of innovation that people don't see - the daily grind of writing, reviewing, refactoring, and improving. But it's exactly this attention to detail that separates good software from great software.

Building with intention, one commit at a time.

#SoftwareDevelopment #BingiTech #DevLife #TechCraftsmanship"""
        
        return {
            "platform": platform,
            "content": content,
            "pillar": "development_process",
            "repository": {"name": repo_name},
            "commit": {
                "message": commit_message,
                "sha": recent_commit.get('sha', '')[:7]
            },
            "created_at": datetime.now().isoformat(),
            "status": "draft",
            "type": "commit_story"
        }
    
    def run_github_content_generation(self):
        """Main GitHub content generation workflow"""
        print("\\n🐙 Starting GitHub-based content generation...")
        
        # Get recent repositories
        repos = self.get_recent_repos(5)  # Get 5 most recent
        
        generated_content = []
        
        for repo in repos[:3]:  # Focus on top 3 repos
            repo_name = repo.get('name', '')
            print(f"\\n📁 Processing repository: {repo_name}")
            
            # Generate repository-based content
            for platform in ["twitter", "linkedin"]:
                post = self.generate_repo_content(repo, platform)
                
                # Save post
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                post_file = self.content_path / f"{timestamp}_{platform}_github_{repo_name}.json"
                
                with open(post_file, 'w') as f:
                    json.dump(post, f, indent=2)
                
                generated_content.append(post)
                print(f"📝 {platform.title()} post created for {repo_name}")
            
            # Get recent commits and create commit story
            commits = self.get_recent_commits(repo_name, 3)
            if commits:
                commit_post = self.generate_commit_story(repo_name, commits, "linkedin")
                if commit_post:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    commit_file = self.content_path / f"{timestamp}_linkedin_commit_{repo_name}.json"
                    
                    with open(commit_file, 'w') as f:
                        json.dump(commit_post, f, indent=2)
                    
                    generated_content.append(commit_post)
                    print(f"📝 Commit story created for {repo_name}")
        
        print(f"\\n✅ GitHub content generation complete!")
        print(f"📊 Generated {len(generated_content)} GitHub-based posts")
        print(f"📁 Content saved in: {self.content_path}")
        
        return generated_content

def main():
    """Main entry point"""
    print("🐙 BingiTech GitHub Agent")
    print("=" * 30)
    
    agent = GitHubAgent()
    content = agent.run_github_content_generation()
    
    print("\\n🎉 GitHub content generation complete!")
    print("\\n📋 Next steps:")
    print("1. Review generated GitHub-based posts")
    print("2. Configure GITHUB_TOKEN for real API access")
    print("3. Send to Discord: make review-discord")

if __name__ == "__main__":
    main()

