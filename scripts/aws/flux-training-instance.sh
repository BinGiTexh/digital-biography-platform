#!/bin/bash
set -e

# BingiTech Flux Fine-Tuning AWS Instance Setup
# Creates g6e.xlarge instance, sets up Flux, and handles training workflow

# Load environment variables
source .env 2>/dev/null || echo "⚠️ No .env file found, using defaults"

# Configuration
INSTANCE_TYPE="${FLUX_INSTANCE_TYPE:-g6e.xlarge}"
REGION="${AWS_REGION:-us-east-1}"
AWS_PROFILE="${AWS_PROFILE:-default}"
KEY_NAME="${AWS_KEY_NAME:-bingitech-flux-key}"
SECURITY_GROUP_NAME="bingitech-flux-sg"
AMI_ID="${FLUX_AMI_ID:-ami-0c02fb55956c7d316}"  # Ubuntu 22.04 LTS
STORAGE_SIZE="${FLUX_STORAGE_SIZE:-100}"  # GB

echo "🚀 BingiTech Flux Fine-Tuning Instance Setup"
echo "============================================="
echo "Instance Type: $INSTANCE_TYPE"
echo "Region: $REGION"
echo "AWS Profile: $AWS_PROFILE"
echo "Key Name: $KEY_NAME"
echo ""

# Function to create SSH key pair if it doesn't exist
create_ssh_key() {
    echo "🔑 Setting up SSH key pair..."
    
    # Check if key exists locally
    if [[ ! -f ~/.ssh/$KEY_NAME ]]; then
        echo "Creating new SSH key pair..."
        ssh-keygen -t rsa -b 4096 -f ~/.ssh/$KEY_NAME -N "" -C "bingitech-flux-$(date +%Y%m%d)"
        chmod 600 ~/.ssh/$KEY_NAME
        chmod 644 ~/.ssh/$KEY_NAME.pub
    fi
    
    # Import to AWS if not exists
    if ! aws ec2 describe-key-pairs --key-names $KEY_NAME --profile $AWS_PROFILE &>/dev/null; then
        echo "Importing key pair to AWS..."
        aws ec2 import-key-pair \
            --key-name $KEY_NAME \
            --public-key-material fileb://~/.ssh/$KEY_NAME.pub \
            --profile $AWS_PROFILE \
            --region $REGION
    else
        echo "✅ Key pair already exists in AWS"
    fi
}

# Function to create security group
create_security_group() {
    echo "🔒 Setting up security group..."
    
    # Check if security group exists
    SG_ID=$(aws ec2 describe-security-groups \
        --group-names $SECURITY_GROUP_NAME \
        --profile $AWS_PROFILE \
        --region $REGION \
        --query 'SecurityGroups[0].GroupId' \
        --output text 2>/dev/null || echo "None")
    
    if [[ "$SG_ID" == "None" ]]; then
        echo "Creating security group..."
        SG_ID=$(aws ec2 create-security-group \
            --group-name $SECURITY_GROUP_NAME \
            --description "BingiTech Flux Fine-tuning Security Group" \
            --profile $AWS_PROFILE \
            --region $REGION \
            --query 'GroupId' \
            --output text)
        
        # Allow SSH access
        aws ec2 authorize-security-group-ingress \
            --group-id $SG_ID \
            --protocol tcp \
            --port 22 \
            --cidr 0.0.0.0/0 \
            --profile $AWS_PROFILE \
            --region $REGION
        
        # Allow Jupyter access (optional)
        aws ec2 authorize-security-group-ingress \
            --group-id $SG_ID \
            --protocol tcp \
            --port 8888 \
            --cidr 0.0.0.0/0 \
            --profile $AWS_PROFILE \
            --region $REGION
    else
        echo "✅ Security group already exists: $SG_ID"
    fi
    
    echo "Security Group ID: $SG_ID"
}

# Function to create user data script for instance initialization
create_user_data() {
    cat > /tmp/flux-userdata.sh << 'EOF'
#!/bin/bash
set -e

# Update system
apt-get update -y
apt-get upgrade -y

# Install essential packages
apt-get install -y \
    curl \
    wget \
    git \
    build-essential \
    python3 \
    python3-pip \
    python3-venv \
    docker.io \
    nvidia-docker2 \
    awscli \
    zip \
    unzip

# Install NVIDIA drivers
apt-get install -y nvidia-driver-535 nvidia-utils-535

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Install Cog
curl -o /usr/local/bin/cog -L https://github.com/replicate/cog/releases/latest/download/cog_`uname -s`_`uname -m`
chmod +x /usr/local/bin/cog

# Add ubuntu user to docker group
usermod -aG docker ubuntu

# Install PyTorch and dependencies
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Install Google Drive CLI (rclone)
curl https://rclone.org/install.sh | bash

# Create workspace
mkdir -p /home/ubuntu/flux-workspace
chown ubuntu:ubuntu /home/ubuntu/flux-workspace

# Clone Flux fine-tuner (will need SSH key setup)
# This will be done after SSH key is added to GitHub

# Install additional Python packages
pip3 install \
    pillow \
    requests \
    boto3 \
    google-api-python-client \
    google-auth-httplib2 \
    google-auth-oauthlib

# Create systemd service for automatic setup completion
cat > /etc/systemd/system/flux-setup.service << 'EOL'
[Unit]
Description=Flux Fine-tuning Setup Completion
After=network.target

[Service]
Type=oneshot
User=ubuntu
WorkingDirectory=/home/ubuntu
ExecStart=/home/ubuntu/complete-setup.sh
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOL

# Create setup completion script
cat > /home/ubuntu/complete-setup.sh << 'EOL'
#!/bin/bash
set -e

cd /home/ubuntu/flux-workspace

# Clone flux fine-tuner (requires SSH key to be set up)
if [[ ! -d "flux-fine-tuner" ]]; then
    echo "Waiting for SSH key setup..."
    while [[ ! -f ~/.ssh/id_rsa ]]; do
        sleep 30
    done
    
    # Add GitHub to known hosts
    ssh-keyscan github.com >> ~/.ssh/known_hosts
    
    # Clone the repository
    git clone --recurse-submodules git@github.com:replicate/flux-fine-tuner.git
fi

echo "✅ Flux setup complete!"
echo "Instance ready for fine-tuning at: $(date)" > /home/ubuntu/setup-complete.txt
EOL

chmod +x /home/ubuntu/complete-setup.sh
chown ubuntu:ubuntu /home/ubuntu/complete-setup.sh

# Enable the service
systemctl enable flux-setup.service

# Reboot to ensure NVIDIA drivers are loaded
echo "Setup script completed, rebooting in 2 minutes..."
shutdown -r +2

EOF

    echo "📝 User data script created"
}

# Function to launch EC2 instance
launch_instance() {
    echo "🚀 Launching EC2 instance..."
    
    create_user_data
    
    INSTANCE_ID=$(aws ec2 run-instances \
        --image-id $AMI_ID \
        --count 1 \
        --instance-type $INSTANCE_TYPE \
        --key-name $KEY_NAME \
        --security-group-ids $SG_ID \
        --user-data file:///tmp/flux-userdata.sh \
        --block-device-mappings "[{\"DeviceName\":\"/dev/sda1\",\"Ebs\":{\"VolumeSize\":$STORAGE_SIZE,\"VolumeType\":\"gp3\"}}]" \
        --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=bingitech-flux-trainer},{Key=Project,Value=BingiTech},{Key=Purpose,Value=FluxFineTuning}]" \
        --profile $AWS_PROFILE \
        --region $REGION \
        --query 'Instances[0].InstanceId' \
        --output text)
    
    echo "✅ Instance launched: $INSTANCE_ID"
    
    # Wait for instance to be running
    echo "⏳ Waiting for instance to be running..."
    aws ec2 wait instance-running \
        --instance-ids $INSTANCE_ID \
        --profile $AWS_PROFILE \
        --region $REGION
    
    # Get public IP
    PUBLIC_IP=$(aws ec2 describe-instances \
        --instance-ids $INSTANCE_ID \
        --profile $AWS_PROFILE \
        --region $REGION \
        --query 'Reservations[0].Instances[0].PublicIpAddress' \
        --output text)
    
    echo "✅ Instance is running!"
    echo "Public IP: $PUBLIC_IP"
    echo "Instance ID: $INSTANCE_ID"
    
    # Save instance details
    cat > flux-instance-details.txt << EOF
Instance ID: $INSTANCE_ID
Public IP: $PUBLIC_IP
Private Key: ~/.ssh/$KEY_NAME
SSH Command: ssh -i ~/.ssh/$KEY_NAME ubuntu@$PUBLIC_IP
Launch Time: $(date)
Instance Type: $INSTANCE_TYPE
Region: $REGION
EOF
    
    echo "📄 Instance details saved to: flux-instance-details.txt"
}

# Function to setup SSH key on the instance for GitHub access
setup_github_ssh() {
    echo "🔑 Setting up GitHub SSH access..."
    
    # Wait for instance to be accessible
    echo "⏳ Waiting for SSH access..."
    while ! ssh -i ~/.ssh/$KEY_NAME -o ConnectTimeout=5 -o StrictHostKeyChecking=no ubuntu@$PUBLIC_IP exit &>/dev/null; do
        echo "Still waiting for SSH..."
        sleep 30
    done
    
    echo "✅ SSH access established"
    
    # Generate SSH key on instance for GitHub
    ssh -i ~/.ssh/$KEY_NAME ubuntu@$PUBLIC_IP << 'EOF'
# Generate SSH key for GitHub
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N "" -C "bingitech-flux-ec2-$(date +%Y%m%d)"

# Display public key
echo "🔑 Add this SSH public key to your GitHub account:"
echo "=================="
cat ~/.ssh/id_rsa.pub
echo "=================="
echo ""
echo "Add it at: https://github.com/settings/ssh/new"
echo ""
EOF
    
    echo ""
    echo "📋 Next steps:"
    echo "1. Copy the SSH public key shown above"
    echo "2. Add it to your GitHub account at: https://github.com/settings/ssh/new"
    echo "3. Run: ssh -i ~/.ssh/$KEY_NAME ubuntu@$PUBLIC_IP"
    echo "4. Test GitHub access: ssh -T git@github.com"
    echo "5. Clone flux-fine-tuner: git clone --recurse-submodules git@github.com:replicate/flux-fine-tuner.git"
}

# Function to create training script
create_training_script() {
    cat > flux-training-helper.sh << 'EOF'
#!/bin/bash
# BingiTech Flux Fine-tuning Helper Script
# Run this on the EC2 instance

set -e

IMAGES_PATH=${1:-"/home/ubuntu/training-images"}
MODEL_NAME=${2:-"bingitech-custom-flux"}
GOOGLE_DRIVE_PATH=${3:-""}

echo "🎨 BingiTech Flux Fine-tuning"
echo "============================"
echo "Images Path: $IMAGES_PATH"
echo "Model Name: $MODEL_NAME"
echo "Google Drive Path: $GOOGLE_DRIVE_PATH"
echo ""

# Function to download from Google Drive
download_from_gdrive() {
    if [[ -n "$GOOGLE_DRIVE_PATH" ]]; then
        echo "📁 Setting up Google Drive access..."
        
        # Configure rclone for Google Drive
        echo "Please run: rclone config"
        echo "Then setup Google Drive remote and run this script again"
        
        # Download images
        rclone copy "gdrive:$GOOGLE_DRIVE_PATH" "$IMAGES_PATH" -P
        
        echo "✅ Images downloaded from Google Drive"
    fi
}

# Function to prepare training images
prepare_images() {
    echo "🖼️ Preparing training images..."
    
    if [[ ! -d "$IMAGES_PATH" ]]; then
        mkdir -p "$IMAGES_PATH"
        echo "Created images directory: $IMAGES_PATH"
    fi
    
    # Count images
    IMAGE_COUNT=$(find "$IMAGES_PATH" -type f \( -name "*.jpg" -o -name "*.jpeg" -o -name "*.png" \) | wc -l)
    echo "Found $IMAGE_COUNT training images"
    
    if [[ $IMAGE_COUNT -eq 0 ]]; then
        echo "❌ No training images found. Please add images to $IMAGES_PATH"
        exit 1
    fi
    
    # Create training zip
    cd "$(dirname "$IMAGES_PATH")"
    zip -r "$(basename "$IMAGES_PATH").zip" "$(basename "$IMAGES_PATH")"
    echo "✅ Training images packaged: $(basename "$IMAGES_PATH").zip"
}

# Function to build and train model
train_model() {
    echo "🏗️ Building Flux model..."
    
    cd flux-fine-tuner
    
    # Build the model
    cog build -t "$MODEL_NAME"
    
    echo "🎯 Starting fine-tuning..."
    
    # Start training
    cog train -i "input_images=@../$(basename "$IMAGES_PATH").zip"
    
    echo "✅ Training completed!"
}

# Function to save model to S3
save_to_s3() {
    local bucket_name="bingitech-flux-models"
    local model_key="models/$MODEL_NAME-$(date +%Y%m%d-%H%M%S).tar.gz"
    
    echo "💾 Saving model to S3..."
    
    # Create model archive
    tar -czf "$MODEL_NAME.tar.gz" -C flux-fine-tuner .
    
    # Upload to S3
    aws s3 cp "$MODEL_NAME.tar.gz" "s3://$bucket_name/$model_key"
    
    echo "✅ Model saved to: s3://$bucket_name/$model_key"
}

# Main execution
main() {
    echo "Starting Flux fine-tuning process..."
    
    # Download images if Google Drive path provided
    if [[ -n "$GOOGLE_DRIVE_PATH" ]]; then
        download_from_gdrive
    fi
    
    # Prepare training data
    prepare_images
    
    # Train the model
    train_model
    
    # Save to S3
    save_to_s3
    
    echo "🎉 Flux fine-tuning complete!"
    echo "📊 Model trained with $IMAGE_COUNT images"
    echo "🏷️ Model name: $MODEL_NAME"
}

# Show usage if no arguments
if [[ $# -eq 0 ]]; then
    echo "Usage: $0 [images_path] [model_name] [google_drive_path]"
    echo ""
    echo "Examples:"
    echo "  $0 /home/ubuntu/bingitech-images bingitech-v1"
    echo "  $0 /home/ubuntu/training-data bingitech-branded bingitech-training-images"
    echo ""
    exit 1
fi

main "$@"
EOF

    chmod +x flux-training-helper.sh
    echo "📝 Training helper script created: flux-training-helper.sh"
}

# Function to terminate instance
terminate_instance() {
    if [[ -f "flux-instance-details.txt" ]]; then
        INSTANCE_ID=$(grep "Instance ID:" flux-instance-details.txt | cut -d' ' -f3)
        
        echo "🛑 Terminating instance: $INSTANCE_ID"
        aws ec2 terminate-instances \
            --instance-ids $INSTANCE_ID \
            --profile $AWS_PROFILE \
            --region $REGION
        
        echo "✅ Instance termination initiated"
        rm flux-instance-details.txt
    else
        echo "❌ No instance details found"
    fi
}

# Main menu
case "${1:-launch}" in
    "launch")
        create_ssh_key
        create_security_group
        launch_instance
        sleep 60  # Wait a bit for instance to boot
        setup_github_ssh
        create_training_script
        ;;
    "terminate")
        terminate_instance
        ;;
    "status")
        if [[ -f "flux-instance-details.txt" ]]; then
            cat flux-instance-details.txt
        else
            echo "No active instance found"
        fi
        ;;
    "ssh")
        if [[ -f "flux-instance-details.txt" ]]; then
            PUBLIC_IP=$(grep "Public IP:" flux-instance-details.txt | cut -d' ' -f3)
            ssh -i ~/.ssh/$KEY_NAME ubuntu@$PUBLIC_IP
        else
            echo "No active instance found"
        fi
        ;;
    *)
        echo "Usage: $0 {launch|terminate|status|ssh}"
        echo ""
        echo "Commands:"
        echo "  launch    - Create and setup new Flux training instance"
        echo "  terminate - Terminate the current instance"
        echo "  status    - Show current instance details"
        echo "  ssh       - SSH into the current instance"
        exit 1
        ;;
esac

