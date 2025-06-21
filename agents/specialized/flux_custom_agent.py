#!/usr/bin/env python3
"""
Flux Custom Model Agent for BingiTech Platform
Handles custom Flux model training and generation using AWS GPU instances
"""

import os
import json
import subprocess
import time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import boto3
from typing import List, Dict, Optional

# Load environment variables
load_dotenv()

class FluxCustomAgent:
    """Custom Flux model training and generation agent"""
    
    def __init__(self):
        self.aws_profile = os.getenv('AWS_PROFILE', 'default')
        self.aws_region = os.getenv('AWS_REGION', 'us-east-1')
        self.replicate_token = os.getenv('REPLICATE_API_TOKEN')
        
        # Setup paths
        self.workspace = Path(__file__).parent.parent.parent / "clients" / "bingitech"
        self.models_path = self.workspace / "models"
        self.training_data_path = self.workspace / "training_data"
        self.generated_path = self.workspace / "visuals" / "generated"
        
        # Create directories
        self.models_path.mkdir(parents=True, exist_ok=True)
        self.training_data_path.mkdir(parents=True, exist_ok=True)
        self.generated_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize AWS clients
        session = boto3.Session(profile_name=self.aws_profile)
        self.s3_client = session.client('s3', region_name=self.aws_region)
        self.ec2_client = session.client('ec2', region_name=self.aws_region)
        
        print(f"🎨 Flux Custom Agent initialized")
        print(f"📁 Models path: {self.models_path}")
        print(f"📁 Training data path: {self.training_data_path}")
        print(f"🔧 AWS Profile: {self.aws_profile}")
        print(f"🌍 AWS Region: {self.aws_region}")
    
    def prepare_bingitech_training_data(self) -> Dict:
        """Prepare BingiTech-specific training images and metadata"""
        
        # Define BingiTech visual style guide
        style_guide = {
            "brand_colors": ["#009B3A", "#FED100", "#000000"],  # Jamaica flag colors
            "visual_themes": [
                "jamaican_tech_fusion",
                "caribbean_innovation",
                "professional_development",
                "soccer_analytics",
                "tropical_minimalism"
            ],
            "aesthetic_principles": [
                "clean_modern_design",
                "cultural_pride_integration",
                "professional_presentation",
                "warm_caribbean_atmosphere",
                "technical_sophistication"
            ]
        }
        
        # Create training prompt templates
        training_prompts = [
            # Developer/Tech themes
            "A professional Caribbean developer working on modern code, clean workspace with Jamaica flag colors, tropical plants, sophisticated lighting, photorealistic style",
            "Modern tech startup office in Jamaica, developers collaborating, green and gold accent lighting, professional photography style",
            "Clean minimalist code editor with Jamaica flag color syntax highlighting, modern monitor setup, professional developer aesthetic",
            
            # Soccer/Sports themes  
            "Professional soccer analytics dashboard with Caribbean styling, clean data visualization in green and gold, modern sports tech aesthetic",
            "Futuristic soccer field with digital overlays, Jamaica flag colors integrated into field design, high-tech sports visualization",
            "Soccer ball with circuit board patterns, floating in space with Jamaica flag colors, professional product photography",
            
            # Innovation/Business themes
            "Caribbean innovation hub, modern architecture with green and gold accents, professional business photography style",
            "Elegant lightbulb made of flowing paint in Jamaica flag colors, black background, artistic product photography",
            "Modern conference room with Caribbean professionals, laptops showing colorful code, professional corporate photography",
            
            # Abstract/Artistic themes
            "Abstract flowing data streams in Jamaica flag colors, elegant curves and nodes, sophisticated technical visualization",
            "Geometric patterns inspired by traditional Jamaican art merged with circuit board designs, modern artistic interpretation",
            "Tropical minimalist workspace, clean lines, subtle Jamaica flag color accents, professional lifestyle photography"
        ]
        
        # Prepare training dataset metadata
        training_data = {
            "dataset_name": f"bingitech_custom_flux_{datetime.now().strftime('%Y%m%d')}",
            "style_guide": style_guide,
            "training_prompts": training_prompts,
            "image_count": len(training_prompts),
            "created_at": datetime.now().isoformat(),
            "purpose": "Custom BingiTech brand visual generation",
            "model_type": "flux_fine_tuned",
            "training_config": {
                "epochs": 1000,
                "learning_rate": 1e-4,
                "batch_size": 1,
                "resolution": "1024x1024",
                "trigger_word": "BINGITECH_STYLE"
            }
        }
        
        # Save training data configuration
        config_file = self.training_data_path / f"training_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(config_file, 'w') as f:
            json.dump(training_data, f, indent=2)
        
        print(f"📊 Training data configuration saved: {config_file}")
        return training_data
    
    def check_aws_instance_status(self) -> Optional[Dict]:
        """Check if there's an active Flux training instance"""
        try:
            # Check for running instances with BingiTech tags
            response = self.ec2_client.describe_instances(
                Filters=[
                    {'Name': 'tag:Project', 'Values': ['BingiTech']},
                    {'Name': 'tag:Purpose', 'Values': ['FluxFineTuning']},
                    {'Name': 'instance-state-name', 'Values': ['running', 'pending']}
                ]
            )
            
            if response['Reservations']:
                instance = response['Reservations'][0]['Instances'][0]
                return {
                    "instance_id": instance['InstanceId'],
                    "public_ip": instance.get('PublicIpAddress'),
                    "state": instance['State']['Name'],
                    "instance_type": instance['InstanceType'],
                    "launch_time": instance['LaunchTime']
                }
            return None
            
        except Exception as e:
            print(f"❌ Error checking AWS instance: {e}")
            return None
    
    def launch_flux_training_instance(self) -> bool:
        """Launch AWS instance for Flux training"""
        print("🚀 Launching Flux training instance...")
        
        try:
            # Use the existing script
            result = subprocess.run([
                "./scripts/aws/flux-training-instance.sh", "launch"
            ], capture_output=True, text=True, cwd=self.workspace.parent.parent)
            
            if result.returncode == 0:
                print("✅ Flux training instance launched successfully")
                return True
            else:
                print(f"❌ Failed to launch instance: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error launching instance: {e}")
            return False
    
    def upload_training_data_to_s3(self, local_path: Path, s3_key: str) -> bool:
        """Upload training data to S3 for the training instance"""
        bucket_name = "bingitech-flux-training"
        
        try:
            # Create bucket if it doesn't exist
            try:
                self.s3_client.head_bucket(Bucket=bucket_name)
            except:
                self.s3_client.create_bucket(Bucket=bucket_name)
                print(f"📦 Created S3 bucket: {bucket_name}")
            
            # Upload file
            self.s3_client.upload_file(str(local_path), bucket_name, s3_key)
            print(f"📤 Uploaded to S3: s3://{bucket_name}/{s3_key}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to upload to S3: {e}")
            return False
    
    def generate_with_custom_model(self, prompt: str, model_name: str = "bingitech-custom-flux") -> Dict:
        """Generate image using custom-trained Flux model"""
        
        # Add BingiTech trigger word to prompt
        enhanced_prompt = f"BINGITECH_STYLE {prompt}, professional quality, Jamaica flag colors (green #009B3A, gold #FED100, black), Caribbean innovation aesthetic"
        
        print(f"🎨 Generating with custom model: {model_name}")
        print(f"💡 Enhanced prompt: {enhanced_prompt[:100]}...")
        
        try:
            if self.replicate_token:
                import replicate
                
                # Use custom model if available, fallback to base model
                try:
                    # Try custom model first
                    output = replicate.run(
                        f"bingitech/{model_name}",
                        input={
                            "prompt": enhanced_prompt,
                            "width": 1024,
                            "height": 1024,
                            "num_outputs": 1,
                            "guidance_scale": 7.5
                        }
                    )
                except:
                    # Fallback to base Flux model with enhanced prompt
                    print("🔄 Custom model not available, using base Flux...")
                    output = replicate.run(
                        "black-forest-labs/flux-schnell",
                        input={
                            "prompt": enhanced_prompt,
                            "width": 1024,
                            "height": 1024,
                            "num_outputs": 1
                        }
                    )
                
                # Save generated image
                image_url = output[0] if isinstance(output, list) else output
                local_path = self.download_and_save_image(image_url, f"flux_custom_{model_name}")
                
                return {
                    "prompt": enhanced_prompt,
                    "original_prompt": prompt,
                    "model": model_name,
                    "generator": "flux_custom",
                    "image_url": image_url,
                    "local_path": local_path,
                    "created_at": datetime.now().isoformat(),
                    "style": "bingitech_custom",
                    "colors": ["#009B3A", "#FED100", "#000000"],
                    "status": "generated"
                }
            else:
                print("⚠️ Replicate token not configured, creating mock")
                return self.create_mock_generation(prompt, model_name)
                
        except Exception as e:
            print(f"❌ Generation failed: {e}")
            return self.create_mock_generation(prompt, model_name)
    
    def download_and_save_image(self, url: str, prefix: str) -> str:
        """Download and save generated image"""
        import requests
        
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
    
    def create_mock_generation(self, prompt: str, model_name: str) -> Dict:
        """Create mock generation data for testing"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        return {
            "prompt": f"BINGITECH_STYLE {prompt}",
            "original_prompt": prompt,
            "model": model_name,
            "generator": "flux_custom_mock",
            "mock_url": f"https://example.com/flux_{timestamp}.png",
            "local_path": None,
            "created_at": datetime.now().isoformat(),
            "style": "bingitech_custom",
            "colors": ["#009B3A", "#FED100", "#000000"],
            "status": "mock_generated"
        }
    
    def run_training_workflow(self) -> Dict:
        """Run complete Flux custom training workflow"""
        print("🎯 Starting Flux custom training workflow...")
        
        workflow_results = {
            "started_at": datetime.now().isoformat(),
            "steps": [],
            "status": "running"
        }
        
        # Step 1: Prepare training data
        print("\n📊 Step 1: Preparing training data...")
        training_data = self.prepare_bingitech_training_data()
        workflow_results["steps"].append({
            "step": "prepare_training_data",
            "status": "completed",
            "data": training_data["dataset_name"]
        })
        
        # Step 2: Check/Launch AWS instance
        print("\n🔍 Step 2: Checking AWS instance...")
        instance_status = self.check_aws_instance_status()
        
        if not instance_status:
            print("🚀 No active instance found, launching new one...")
            if self.launch_flux_training_instance():
                workflow_results["steps"].append({
                    "step": "launch_instance",
                    "status": "completed"
                })
            else:
                workflow_results["steps"].append({
                    "step": "launch_instance", 
                    "status": "failed"
                })
                workflow_results["status"] = "failed"
                return workflow_results
        else:
            print(f"✅ Using existing instance: {instance_status['instance_id']}")
            workflow_results["steps"].append({
                "step": "instance_check",
                "status": "existing_instance_found",
                "instance": instance_status
            })
        
        # Step 3: Provide training instructions
        print("\n📋 Step 3: Training instructions prepared...")
        instructions = self.get_training_instructions()
        workflow_results["steps"].append({
            "step": "training_instructions",
            "status": "prepared",
            "instructions": instructions
        })
        
        workflow_results["status"] = "ready_for_training"
        workflow_results["completed_at"] = datetime.now().isoformat()
        
        # Save workflow results
        results_file = self.models_path / f"training_workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump(workflow_results, f, indent=2)
        
        print(f"\n✅ Training workflow prepared!")
        print(f"📄 Results saved: {results_file}")
        
        return workflow_results
    
    def get_training_instructions(self) -> Dict:
        """Get detailed training instructions for the AWS instance"""
        return {
            "manual_steps": [
                "1. SSH into the instance: make flux-ssh",
                "2. Wait for setup completion: cat ~/setup-complete.txt",
                "3. Verify GitHub access: ssh -T git@github.com",
                "4. Navigate to workspace: cd ~/flux-workspace",
                "5. Clone flux-fine-tuner if not done: git clone --recurse-submodules git@github.com:replicate/flux-fine-tuner.git",
                "6. Upload your training images to ~/training-images/",
                "7. Run training: ~/flux-training-helper.sh ~/training-images bingitech-custom-v1"
            ],
            "automated_commands": [
                "make flux-setup     # Launch instance",
                "make flux-status    # Check status", 
                "make flux-ssh       # Connect to instance",
                "make flux-terminate # Cleanup when done"
            ],
            "training_data_info": {
                "images_needed": "10-50 high-quality images showing BingiTech brand style",
                "image_format": "PNG/JPG, 1024x1024 recommended",
                "style_consistency": "Jamaica flag colors, professional aesthetic, Caribbean innovation themes"
            }
        }
    
    def run_generation_demo(self) -> List[Dict]:
        """Run a demo of custom model generation"""
        print("🎨 Running Flux custom generation demo...")
        
        demo_prompts = [
            "A Caribbean developer coding in a modern workspace with tropical plants",
            "Professional soccer analytics dashboard with Jamaica flag color scheme", 
            "Elegant lightbulb symbol made of flowing green and gold paint strokes",
            "Modern tech startup office in Jamaica with collaborative atmosphere"
        ]
        
        generated_content = []
        
        for i, prompt in enumerate(demo_prompts, 1):
            print(f"\n🎯 Demo {i}/4: {prompt[:50]}...")
            
            result = self.generate_with_custom_model(prompt, "bingitech-demo-v1")
            generated_content.append(result)
            
            # Save metadata
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            metadata_file = self.generated_path / f"flux_demo_{timestamp}_{i}.json"
            with open(metadata_file, 'w') as f:
                json.dump(result, f, indent=2)
            
            print(f"📊 Metadata saved: {metadata_file}")
        
        print(f"\n✅ Demo complete! Generated {len(generated_content)} images")
        return generated_content

def main():
    """Main entry point"""
    print("🎨 BingiTech Flux Custom Agent")
    print("=" * 50)
    
    agent = FluxCustomAgent()
    
    # Check if instance exists
    instance = agent.check_aws_instance_status()
    if instance:
        print(f"🔍 Found active instance: {instance['instance_id']}")
        print(f"📍 Status: {instance['state']}")
        print(f"🌐 IP: {instance.get('public_ip', 'N/A')}")
    
    # Run training workflow preparation
    workflow = agent.run_training_workflow()
    
    # Run generation demo
    demo_results = agent.run_generation_demo()
    
    print("\n🎉 Flux Custom Agent complete!")
    print("\n📋 Next steps:")
    print("1. Follow training instructions to create custom model")
    print("2. Use custom model for BingiTech-branded image generation")
    print("3. Integrate with social media content workflow")

if __name__ == "__main__":
    main()

