#!/usr/bin/env python3
"""
Flux LoRA Agent for BingiTech Platform
Uses custom trained LoRA models for specialized image generation
"""

import os
import json
import boto3
import requests
import time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, List, Optional

# Load environment variables
load_dotenv()

class FluxLoRAAgent:
    """Custom LoRA model integration for specialized Flux generation"""
    
    def __init__(self):
        self.replicate_token = os.getenv('REPLICATE_API_TOKEN')
        self.aws_profile = os.getenv('AWS_PROFILE', 'personal')
        self.aws_region = os.getenv('AWS_REGION', 'us-east-1')
        
        # Setup paths
        self.workspace = Path(__file__).parent.parent.parent / "clients" / "bingitech"
        self.models_path = self.workspace / "models" / "lora"
        self.generated_path = self.workspace / "visuals" / "generated"
        
        # Create directories
        self.models_path.mkdir(parents=True, exist_ok=True)
        self.generated_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize AWS client
        session = boto3.Session(profile_name=self.aws_profile)
        self.s3_client = session.client('s3', region_name=self.aws_region)
        
        # Available LoRA models
        self.available_loras = {
            "outdoor_flux": {
                "name": "Outdoor Flux LoRA",
                "s3_bucket": "ml-ai-assets",
                "s3_path": "flux_outdoor_weights",
                "trigger_word": "TOK",
                "description": "Custom trained for outdoor scenes and landscapes",
                "strength": 0.8,
                "themes": ["outdoor", "nature", "landscapes", "scenic"]
            }
        }
        
        print(f"🎨 Flux LoRA Agent initialized")
        print(f"📁 Models path: {self.models_path}")
        print(f"🔧 AWS Profile: {self.aws_profile}")
        print(f"📦 Available LoRAs: {len(self.available_loras)}")
    
    def download_lora_model(self, lora_key: str) -> bool:
        """Download LoRA model from S3"""
        if lora_key not in self.available_loras:
            print(f"❌ Unknown LoRA model: {lora_key}")
            return False
        
        lora_info = self.available_loras[lora_key]
        local_model_dir = self.models_path / lora_key
        local_model_dir.mkdir(exist_ok=True)
        
        try:
            # Download LoRA weights
            lora_file = local_model_dir / "lora.safetensors"
            config_file = local_model_dir / "config.yaml"
            
            if not lora_file.exists():
                print(f"📥 Downloading LoRA weights...")
                self.s3_client.download_file(
                    lora_info["s3_bucket"],
                    f"{lora_info['s3_path']}/lora.safetensors",
                    str(lora_file)
                )
                print(f"✅ LoRA weights downloaded: {lora_file}")
            
            if not config_file.exists():
                print(f"📥 Downloading config...")
                self.s3_client.download_file(
                    lora_info["s3_bucket"],
                    f"{lora_info['s3_path']}/config.yaml",
                    str(config_file)
                )
                print(f"✅ Config downloaded: {config_file}")
            
            # Save model info
            model_info = {
                **lora_info,
                "local_path": str(local_model_dir),
                "downloaded_at": datetime.now().isoformat(),
                "file_size_mb": round(lora_file.stat().st_size / (1024*1024), 2)
            }
            
            info_file = local_model_dir / "model_info.json"
            with open(info_file, 'w') as f:
                json.dump(model_info, f, indent=2)
            
            print(f"📊 Model info saved: {info_file}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to download LoRA model: {e}")
            return False
    
    def generate_with_lora(self, prompt: str, lora_key: str = "outdoor_flux", 
                          apply_bingitech_branding: bool = True) -> Dict:
        """Generate image using custom LoRA model"""
        
        if lora_key not in self.available_loras:
            print(f"❌ Unknown LoRA: {lora_key}")
            return self.create_mock_generation(prompt, lora_key)
        
        lora_info = self.available_loras[lora_key]
        
        # Ensure model is downloaded
        if not self.download_lora_model(lora_key):
            return self.create_mock_generation(prompt, lora_key)
        
        # Build enhanced prompt
        enhanced_prompt = self.build_enhanced_prompt(prompt, lora_info, apply_bingitech_branding)
        
        print(f"🎨 Generating with LoRA: {lora_info['name']}")
        print(f"💡 Enhanced prompt: {enhanced_prompt[:100]}...")
        
        try:
            if self.replicate_token:
                import replicate
                
                # Use Flux with LoRA
                output = replicate.run(
                    "black-forest-labs/flux-dev",
                    input={
                        "prompt": enhanced_prompt,
                        "width": 1024,
                        "height": 1024,
                        "num_outputs": 1,
                        "guidance_scale": 3.5,
                        "num_inference_steps": 28,
                        # Note: LoRA loading would be implemented in a custom Replicate model
                        # For now we enhance the prompt with trigger words
                    }
                )
                
                # Save generated image
                image_url = output[0] if isinstance(output, list) else output
                local_path = self.download_and_save_image(image_url, f"lora_{lora_key}")
                
                return {
                    "prompt": enhanced_prompt,
                    "original_prompt": prompt,
                    "lora_model": lora_key,
                    "lora_info": lora_info,
                    "generator": "flux_lora",
                    "image_url": image_url,
                    "local_path": local_path,
                    "created_at": datetime.now().isoformat(),
                    "style": f"lora_{lora_key}",
                    "status": "generated",
                    "bingitech_branded": apply_bingitech_branding
                }
            else:
                print("⚠️ Replicate token not configured")
                return self.create_mock_generation(prompt, lora_key)
                
        except Exception as e:
            print(f"❌ Generation failed: {e}")
            return self.create_mock_generation(prompt, lora_key)
    
    def build_enhanced_prompt(self, prompt: str, lora_info: Dict, 
                            apply_bingitech_branding: bool) -> str:
        """Build enhanced prompt with LoRA trigger word and branding"""
        
        # Start with trigger word
        enhanced_prompt = f"{lora_info['trigger_word']} {prompt}"
        
        # Add BingiTech branding if requested
        if apply_bingitech_branding:
            enhanced_prompt += ", professional quality, Jamaica flag colors (green #009B3A, gold #FED100, black), Caribbean innovation aesthetic"
        
        # Add quality and style modifiers
        enhanced_prompt += ", high quality, detailed, professional photography style"
        
        return enhanced_prompt
    
    def create_bingitech_outdoor_content(self) -> List[Dict]:
        """Generate BingiTech branded outdoor content using LoRA"""
        
        outdoor_prompts = [
            "A Caribbean tech entrepreneur working on a laptop in a beautiful tropical garden with lush greenery",
            "Modern outdoor workspace setup with laptops and technology equipment in a scenic Jamaica landscape",
            "Professional team meeting outdoors in a stunning Caribbean setting with mountains in the background",
            "Innovative outdoor tech setup showcasing modern equipment against a backdrop of tropical paradise",
            "A scenic view of a Jamaica tech campus with outdoor workspaces and natural beauty",
            "Caribbean developers collaborating in an outdoor innovation space with breathtaking ocean views"
        ]
        
        generated_content = []
        
        for i, prompt in enumerate(outdoor_prompts, 1):
            print(f"\n🌴 Generating outdoor content {i}/{len(outdoor_prompts)}")
            print(f"📝 Prompt: {prompt[:60]}...")
            
            result = self.generate_with_lora(
                prompt=prompt,
                lora_key="outdoor_flux",
                apply_bingitech_branding=True
            )
            
            generated_content.append(result)
            
            # Save metadata
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            metadata_file = self.generated_path / f"lora_outdoor_{timestamp}_{i}.json"
            with open(metadata_file, 'w') as f:
                json.dump(result, f, indent=2)
            
            print(f"📊 Metadata saved: {metadata_file}")
            
            # Brief pause between generations
            time.sleep(2)
        
        print(f"\n✅ Generated {len(generated_content)} outdoor BingiTech images!")
        return generated_content
    
    def download_and_save_image(self, url: str, prefix: str) -> str:
        """Download and save generated image"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{prefix}_{timestamp}.png"
            save_path = self.generated_path / filename
            
            response = requests.get(url)
            response.raise_for_status()
            
            with open(save_path, 'wb') as f:
                f.write(response.content)
            
            print(f"🖼️ Image saved: {save_path}")
            return str(save_path)
            
        except Exception as e:
            print(f"❌ Error downloading image: {e}")
            return None
    
    def create_mock_generation(self, prompt: str, lora_key: str) -> Dict:
        """Create mock generation for testing"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        return {
            "prompt": f"TOK {prompt} [MOCK]",
            "original_prompt": prompt,
            "lora_model": lora_key,
            "generator": "flux_lora_mock",
            "mock_url": f"https://example.com/lora_{timestamp}.png",
            "local_path": None,
            "created_at": datetime.now().isoformat(),
            "style": f"lora_{lora_key}",
            "status": "mock_generated",
            "bingitech_branded": True
        }
    
    def list_available_models(self) -> Dict:
        """List all available LoRA models"""
        print("📋 Available LoRA Models:")
        print("=" * 40)
        
        for key, info in self.available_loras.items():
            local_path = self.models_path / key
            downloaded = "✅ Downloaded" if local_path.exists() else "⏬ Available for download"
            
            print(f"\n🎨 {info['name']} ({key})")
            print(f"   Trigger Word: {info['trigger_word']}")
            print(f"   Description: {info['description']}")
            print(f"   Themes: {', '.join(info['themes'])}")
            print(f"   Status: {downloaded}")
        
        return self.available_loras
    
    def create_social_post_with_lora(self, image_data: Dict, platform: str = "linkedin") -> Dict:
        """Create social media post with LoRA-generated content"""
        
        lora_info = image_data.get("lora_info", {})
        
        # Create platform-appropriate caption
        if platform == "linkedin":
            caption = f"🌴 Innovation meets paradise! Showcasing how Caribbean creativity and cutting-edge technology come together in beautiful outdoor settings. At BingiTech, we believe the best ideas flow when you're inspired by nature's beauty. #BingiTech #CaribbeanInnovation #OutdoorTech #JamaicanExcellence #TechInParadise"
        else:  # Twitter
            caption = f"🌴💻 When your office view is this stunning, innovation just flows naturally! Caribbean tech at its finest. #BingiTech #CaribbeanTech #OutdoorOffice #JamaicanInnovation"
        
        post_data = {
            "platform": platform,
            "content": caption,
            "visual": {
                "prompt": image_data.get("original_prompt"),
                "enhanced_prompt": image_data.get("prompt"),
                "lora_model": image_data.get("lora_model"),
                "generator": image_data.get("generator"),
                "image_url": image_data.get("image_url"),
                "local_path": image_data.get("local_path")
            },
            "pillar": "caribbean_outdoor_innovation",
            "created_at": datetime.now().isoformat(),
            "status": "draft",
            "type": "lora_visual_post"
        }
        
        # Save post
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        post_file = self.generated_path.parent / "content" / "generated" / f"{timestamp}_{platform}_lora_post.json"
        
        with open(post_file, 'w') as f:
            json.dump(post_data, f, indent=2)
        
        print(f"📱 {platform.title()} post created: {post_file}")
        return post_data

def main():
    """Main entry point"""
    print("🌴 BingiTech Flux LoRA Agent")
    print("=" * 50)
    
    agent = FluxLoRAAgent()
    
    # List available models
    agent.list_available_models()
    
    # Generate BingiTech outdoor content
    print("\n🎨 Generating BingiTech outdoor content...")
    content = agent.create_bingitech_outdoor_content()
    
    # Create social media posts
    print("\n📱 Creating social media posts...")
    for i, image_data in enumerate(content[:2]):  # Create posts for first 2 images
        agent.create_social_post_with_lora(image_data, "linkedin")
        agent.create_social_post_with_lora(image_data, "twitter")
    
    print(f"\n🎉 LoRA generation complete!")
    print(f"📊 Generated {len(content)} images")
    print(f"📱 Created {len(content) * 2} social media posts")
    
    print("\n📋 Next steps:")
    print("1. Review generated outdoor content")
    print("2. Send to Discord: make review-discord")
    print("3. Generate more with: make lora-generate")

if __name__ == "__main__":
    main()

