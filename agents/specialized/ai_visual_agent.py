#!/usr/bin/env python3
"""
AI Visual Content Agent for BingiTech Platform
Generates Jamaican-themed visuals using Ideogram AI for social media content
"""

import os
import json
import requests
from datetime import datetime
from pathlib import Path
import sys

# Add utils to path for cost tracking
sys.path.append(str(Path(__file__).parent.parent.parent / "utils"))
from cost_tracker import CostTracker

import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AIVisualAgent:
    """AI visual content generator for BingiTech with Jamaican themes"""
    
    def __init__(self):
        self.replicate_token = os.getenv('REPLICATE_API_TOKEN')
        self.ideogram_token = os.getenv('IDEOGRAM_API_TOKEN')
        
        # Initialize cost tracker
        self.cost_tracker = CostTracker()
        
        # Setup paths
        self.workspace = Path(__file__).parent.parent.parent / "clients" / "bingitech"
        self.visuals_path = self.workspace / "visuals" / "generated"
        self.content_path = self.workspace / "content" / "generated"
        
        # Create directories
        self.visuals_path.mkdir(parents=True, exist_ok=True)
        self.content_path.mkdir(parents=True, exist_ok=True)
        
        print(f"🎨 AI Visual Agent initialized")
        print(f"📁 Visuals path: {self.visuals_path}")
        print(f"🔑 Replicate configured: {bool(self.replicate_token)}")
        print(f"🔑 Ideogram configured: {bool(self.ideogram_token)}")
        print(f"💰 Cost tracking enabled: {bool(self.cost_tracker.discord_webhook)}")
    
    def get_malik_campaign_prompts(self):
        """Prompts specifically crafted for Malik reference photos (Nike-style with best practices)."""
        return {
            "malik_precision_shot": [
                "Elite soccer player executing a precision free kick at golden hour. Shot on 85mm f/1.4, 1/1250s, ISO 200. Warm golden side-light creating dramatic shadows, subtle rim lighting on ball. Ball frozen mid-flight with slight motion blur on grass, cleats planted firmly. Leather ball texture crisp, jersey fabric detail, grass blades sharp. Deep soccer green field, subtle Jamaican flag colors in wristband or socks. Focused determination, 'precision meets passion' mood. Rule of thirds composition, ball trajectory leading eye, negative space for copy."
            ],
            "malik_dynamic_sprint": [
                "Soccer player in full sprint, chasing down the ball. Shot on 35mm f/2.0, 1/1000s panning shot, ISO 400. Stadium floodlights creating dramatic contrast, motion-blur background. Legs mid-stride, slight motion blur on background, ball sharp in frame. Sweat droplets visible, jersey rippling with movement, turf texture. Vibrant team colors with subtle green/gold accent details. Unstoppable drive, 'speed meets strategy' mood. Diagonal energy composition, leading lines from field markings."
            ],
            "malik_tech_fusion": [
                "Soccer field where the yard lines are made of glowing code syntax, player dribbling through data streams. Shot on 50mm f/1.8, 1/800s, ISO 100. Neon code glow from field lines, cool blue tech ambiance with warm player lighting. Ball leaving digital trail particles, player in dynamic dribbling pose. Holographic code text, realistic player and ball, grass with digital overlay. Jamaican green/gold accents, electric blue code, warm skin tones. Innovation meets athleticism, 'where sport meets tech' mood. Symmetrical field perspective, player as focal point."
            ]
        }

    def get_jamaican_tech_prompts(self):
        """Generate Jamaican-themed tech visual prompts"""
        return {
            "code_vibes": [
                "A vibrant scene of a developer coding on a laptop with Jamaican flag colors glowing from the screen. The background shows a beautiful Caribbean sunset with palm trees. The code on screen shows clean, modern programming syntax. Reggae-inspired geometric patterns frame the image. Professional yet tropical aesthetic.",
                
                "Modern minimalist workspace with a MacBook displaying colorful code syntax highlighting in green, gold, and black - Jamaica flag colors. A soccer ball sits beside the laptop. Clean desk setup with tropical plants in the background. Professional developer aesthetic with Caribbean flair.",
                
                "Abstract representation of data flowing like reggae music waves in Jamaican flag colors. Digital nodes and connections form musical note patterns. Green (#009B3A), gold (#FED100), and black create a sophisticated tech visualization with cultural pride."
            ],
            
            "soccer_tech": [
                "A futuristic soccer field where the lines are made of glowing code syntax. Players are represented as elegant geometric shapes in Jamaican colors. The ball is a 3D geometric sphere with digital circuit patterns. Clean, professional sports-tech aesthetic.",
                
                "Soccer strategy formation displayed as a beautiful data visualization. Player positions shown as connected nodes in green and gold, with movement patterns traced in elegant curves. Black background with technical grid overlay. Modern sports analytics aesthetic.",
                
                "A soccer ball transforming into a globe showing Caribbean islands, with digital connections linking Jamaica to the world. Tech elements include clean code snippets floating around. Professional, inspirational design in flag colors."
            ],
            
            "jamaican_innovation": [
                "Elegant paint strokes in Jamaican flag colors forming the shape of a lightbulb - symbolizing innovation. The strokes are modern and sophisticated with clean edges. Black background with subtle tech grid pattern. Corporate innovation aesthetic with cultural pride.",
                
                "Abstract representation of Jamaica as a digital innovation hub. Clean, geometric island outline with flowing data streams in green and gold. Modern typography elements suggesting 'Innovation Island'. Professional tech company branding style.",
                
                "A modern interpretation of traditional Jamaican patterns (like those found in craft work) merged with circuit board designs. Green and gold pathways on black background creating a sophisticated tech-cultural fusion."
            ],
            
            "team_building": [
                "Professional team collaboration scene with diverse developers around a modern conference table. Laptops display code in syntax highlighting that uses green, gold, and black themes. Caribbean elements subtly integrated through plants and artwork. Clean, corporate aesthetic.",
                
                "Remote work setup showing a developer working from a beautiful Caribbean balcony. Clean, modern laptop and workspace with the ocean in the background. Professional but relaxed 'island time' productivity aesthetic.",
                
                "Team building concept shown through soccer team formation merged with development team structure. Clean, minimalist design showing how sports strategy applies to tech team organization."
            ]
        }
    
    def generate_github_themed_prompts(self, repo_name, repo_description="", commit_message=""):
        """Generate visual prompts based on GitHub repository activity"""
        repo_prompts = []
        
        # Base template for GitHub-inspired visuals
        base_context = f"Professional tech visualization for GitHub repository '{repo_name}'"
        
        if "job" in repo_name.lower() or "career" in repo_name.lower():
            repo_prompts.append(
                f"{base_context}: A clean, modern job board interface design with Jamaican flag color accents. Professional layout with green (#009B3A) and gold (#FED100) highlights on black background. Caribbean professional aesthetic."
            )
        
        elif "soccer" in repo_name.lower() or "football" in repo_name.lower():
            repo_prompts.append(
                f"{base_context}: Soccer analytics dashboard with clean data visualization. Field diagrams in Jamaican colors, modern charts and graphs. Professional sports-tech aesthetic."
            )
        
        elif "api" in repo_name.lower() or "backend" in repo_name.lower():
            repo_prompts.append(
                f"{base_context}: Elegant API architecture diagram with flowing connections. Data flow represented in Jamaican flag colors on sophisticated black background. Clean, technical illustration."
            )
        
        else:
            # General tech repository
            repo_prompts.append(
                f"{base_context}: Modern code architecture visualization with clean geometric shapes in green, gold, and black. Professional developer aesthetic with Caribbean cultural elements."
            )
        
        return repo_prompts
    
    def download_image(self, url, filename_prefix="bingitech"):
        """Download generated image and save locally"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{filename_prefix}_{timestamp}.png"
            save_path = self.visuals_path / filename
            
            response = requests.get(url)
            response.raise_for_status()
            
            with open(save_path, 'wb') as f:
                f.write(response.content)
            
            print(f"🖼️ Image saved: {save_path}")
            return str(save_path)
            
        except Exception as e:
            print(f"❌ Error downloading image: {e}")
            return None
    
    def generate_with_ideogram(self, prompt, style_type="GENERAL", rendering_speed="QUALITY"):
        """Generate visual using Ideogram 3.0 API.

        Args:
            prompt (str): Text prompt describing the image.
            style_type (str): One of Ideogram's style keywords, e.g. GENERAL, PHOTO, etc.

            rendering_speed (str): One of FLASH, TURBO, BALANCED, DEFAULT, QUALITY. QUALITY offers best fidelity.
        Returns:
            dict: Visual metadata (same shape as create_mock_visual).
        """
        if not self.ideogram_token:
            print("⚠️ Ideogram API token not configured – falling back to mock mode")
            return self.create_mock_visual(prompt, "ideogram_mock")

        try:
            print(f"🎨 Generating with Ideogram: {prompt[:100]}…")
            url = "https://api.ideogram.ai/v1/ideogram-v3/generate"
            headers = {
                "Api-Key": self.ideogram_token,
            }
            # multipart/form-data fields
            # Prepare multipart fields (non-file)
            base_fields = {
                "prompt": (None, prompt),
                "rendering_speed": (None, rendering_speed),
                "resolution": (None, "832x1248"),
                "style_type": (None, style_type),
            }

            # Build files list for requests
            files_to_upload = list(base_fields.items())

            # Attach reference images, if any
            ref_dir = self.visuals_path.parent / "refs"
            if ref_dir.exists():
                for img_path in ref_dir.iterdir():
                    if img_path.suffix.lower() in [".jpg", ".jpeg", ".png", ".webp"]:
                        files_to_upload.append(
                            (
                                "style_reference_images[]",
                                (img_path.name, open(img_path, "rb"), "image/jpeg"),
                            )
                        )
            else:
                print("ℹ️ No reference images folder found – skipping style_reference_images[] upload")

            response = requests.post(url, files=files_to_upload, headers=headers, timeout=90)
            if not response.ok:
                print(f"❌ Ideogram API error {response.status_code}: {response.text[:400]}")
            response.raise_for_status()
            payload = response.json()
            image_url = payload["data"][0]["url"]

            local_path = self.download_image(image_url, "ideogram_visual")

            visual_data = {
                "prompt": prompt,
                "generator": "ideogram",
                "created_at": datetime.now().isoformat(),
                "style": style_type,
                "colors": ["#009B3A", "#FED100", "#000000"],  # Jamaica flag colours
                "status": "generated",
                "image_url": image_url,
                "local_path": local_path,
                "themes": ["jamaican", "tech", "professional"]
            }

            # Save metadata
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            visual_file = self.visuals_path / f"visual_{timestamp}_ideogram.json"
            with open(visual_file, "w") as f:
                json.dump(visual_data, f, indent=2)

            # Log cost
            self.cost_tracker.auto_log_ideogram(1, rendering_speed)

            print("✅ Ideogram image generated and saved!")
            print(f"📊 Visual metadata saved: {visual_file}")
            return visual_data

        except Exception as e:
            print(f"❌ Ideogram generation failed: {e}")
            return self.create_mock_visual(prompt, "ideogram_error")
    
    def generate_with_replicate(self, prompt):
        """Generate visual using Replicate (like your existing code)"""
        if not self.replicate_token:
            print("⚠️ Replicate API token not configured")
            return self.create_mock_visual(prompt, "replicate")
        
        try:
            import replicate
            
            print(f"🔄 Generating with Replicate: {prompt[:100]}...")
            
            # Initialize the Replicate client
            client = replicate.Client(api_token=self.replicate_token)
            
            # Run the Ideogram model (same as your generate_designs.py)
            output = client.run(
                "ideogram-ai/ideogram-v3-quality",
                input={
                    "prompt": prompt,
                    "resolution": "None",
                    "style_type": "None", 
                    "aspect_ratio": "3:2",
                    "magic_prompt_option": "Off"
                }
            )
            
            # Download and save the generated image
            image_url = output[0] if isinstance(output, list) else output
            local_path = self.download_image(image_url, "replicate_visual")
            
            visual_data = {
                "prompt": prompt,
                "generator": "replicate",
                "created_at": datetime.now().isoformat(),
                "style": "jamaican_tech_fusion",
                "colors": ["#009B3A", "#FED100", "#000000"],
                "status": "generated",
                "image_url": image_url,
                "local_path": local_path,
                "themes": ["jamaican", "tech", "professional"]
            }
            
            # Save visual metadata
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            visual_file = self.visuals_path / f"visual_{timestamp}_replicate.json"
            with open(visual_file, 'w') as f:
                json.dump(visual_data, f, indent=2)
            
            print(f"✅ Real image generated and saved!")
            print(f"📊 Visual metadata saved: {visual_file}")
            
            return visual_data
            
        except ImportError:
            print("❌ Replicate package not installed. Run: pip install replicate")
            return self.create_mock_visual(prompt, "replicate")
        except Exception as e:
            print(f"❌ Replicate generation failed: {e}")
            return self.create_mock_visual(prompt, "replicate")
    
    def create_mock_visual(self, prompt, generator="mock"):
        """Create mock visual data for testing"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        mock_visual = {
            "prompt": prompt,
            "generator": generator,
            "created_at": datetime.now().isoformat(),
            "style": "jamaican_tech_fusion",
            "colors": ["#009B3A", "#FED100", "#000000"],  # Jamaica flag colors
            "status": "generated",
            "mock_url": f"https://example.com/generated_{timestamp}.png",
            "local_path": None,
            "themes": ["jamaican", "tech", "professional"]
        }
        
        # Save visual metadata
        visual_file = self.visuals_path / f"visual_{timestamp}_{generator}.json"
        with open(visual_file, 'w') as f:
            json.dump(mock_visual, f, indent=2)
        
        print(f"📊 Visual metadata saved: {visual_file}")
        return mock_visual
    
    def create_social_post_with_visual(self, prompt, visual_data, platform="twitter"):
        """Create social media post incorporating the generated visual"""
        
        # Generate caption based on the visual theme
        if "code" in prompt.lower():
            caption = "Building the future with Caribbean innovation 🇯🇲💻 Every line of code tells a story of persistence and creativity. #BingiTech #JamaicanTech #CodeLife"
        elif "soccer" in prompt.lower():
            caption = "Strategy on the field, strategy in code ⚽️💡 The beautiful game teaches us about teamwork and precision in software development. #BingiTech #TechStrategy #SoccerMeetsCode"
        elif "team" in prompt.lower():
            caption = "Building world-class teams with island innovation 🌴👥 Remote work, Caribbean style - where productivity meets paradise. #BingiTech #RemoteWork #TeamBuilding"
        else:
            caption = "Innovation flows through everything we build 🚀 Bringing Jamaican creativity to the global tech stage. #BingiTech #Innovation #JamaicanExcellence"
        
        post_data = {
            "platform": platform,
            "content": caption,
            "visual": {
                "prompt": prompt,
                "generator": visual_data.get("generator"),
                "style": visual_data.get("style"),
                "colors": visual_data.get("colors"),
                "mock_url": visual_data.get("mock_url")
            },
            "pillar": "jamaican_tech_innovation",
            "created_at": datetime.now().isoformat(),
            "status": "draft",
            "type": "visual_post"
        }
        
        # Save post with visual
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        post_file = self.content_path / f"{timestamp}_{platform}_visual_post.json"
        
        with open(post_file, 'w') as f:
            json.dump(post_data, f, indent=2)
        
        print(f"📝 Visual post created: {post_file}")
        return post_data
    
    def run_visual_generation(self, theme="jamaican_tech"):
        """Main visual generation workflow"""
        print(f"\\n🎨 Starting AI visual generation for theme: {theme}")
        
        if theme == "malik_campaign":
            prompts = self.get_malik_campaign_prompts()
        else:
            prompts = self.get_jamaican_tech_prompts()
        
        generated_content = []
        
        # Generate visuals for different themes
        for theme_name, theme_prompts in prompts.items():
            print(f"\\n🎯 Working on theme: {theme_name}")
            
            # Pick one prompt from this theme
            prompt = theme_prompts[0]  # Use first prompt for demo
            
            print(f"💡 Prompt: {prompt[:100]}...")
            
            # Generate visual with Ideogram 3.0
            visual_data = self.generate_with_ideogram(prompt)
            
            if visual_data:
                # Create social media post with this visual
                for platform in ["twitter", "linkedin"]:
                    post = self.create_social_post_with_visual(prompt, visual_data, platform)
                    generated_content.append(post)
                    print(f"📱 {platform.title()} post created with visual")
        
        print(f"\\n✅ Visual generation complete!")
        print(f"📊 Generated {len(generated_content)} visual posts")
        print(f"🖼️ Visuals saved in: {self.visuals_path}")
        print(f"📝 Posts saved in: {self.content_path}")
        
        return generated_content

def main():
    """Main entry point"""
    print("🎨 BingiTech AI Visual Agent")
    print("=" * 40)
    
    agent = AIVisualAgent()
    content = agent.run_visual_generation()
    
    print("\\n🎉 AI visual generation complete!")
    print("\\n📋 Next steps:")
    print("1. Review generated visuals and posts")
    print("2. Configure Ideogram/Replicate API keys for real generation")
    print("3. Send to Discord: make review-discord")

if __name__ == "__main__":
    main()
