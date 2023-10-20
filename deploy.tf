provider "aws" {
  region  = "us-east-1"
  version = "~> 3.0"
}

# EC2 Instance
resource "aws_instance" "example" {
  ami           = "ami-xxxxxxxxxxxxxxxxx"  # Replace with the appropriate AMI ID
  instance_type = "t2.micro"
  key_name      = "your-key-pair"  # Replace with your key pair name
  subnet_id     = "subnet-xxxxxxxx,subnet-yyyyyyyy"  # Replace with appropriate subnet IDs
  security_groups = ["Hw2ExtensionSG"]  # Replace with your security group name
}

# Elastic Load Balancer
resource "aws_lb" "example" {
  name               = "Hw2ExtensionLoadBalancer"
  internal           = false
  load_balancer_type = "application"
  enable_deletion_protection = false
  security_groups    = [aws_security_group.Hw2ExtensionSG.id]
  subnets            = ["subnet-xxxxxxxx", "subnet-yyyyyyyy"]  # Replace with appropriate subnet IDs
}

# Security Group
resource "aws_security_group" "Hw2ExtensionSG" {
  name        = "Hw2ExtensionSG"
  description = "Hw2Swarm"
  vpc_id      = "vpc-xxxxxxxx"  # Replace with your VPC ID

  ingress {
    from_port   = 8888
    to_port     = 8888
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Launch Configuration
resource "aws_launch_configuration" "example" {
  name               = "Hw2Extension"
  image_id           = "ami-xxxxxxxxxxxxxxxxx"  # Replace with the appropriate AMI ID
  instance_type      = "t2.micro"
  security_groups    = [aws_security_group.Hw2ExtensionSG.id]
  key_name           = "your-key-pair"  # Replace with your key pair name
  associate_public_ip_address = true
}

# Auto Scaling Group
resource "aws_autoscaling_group" "example" {
  desired_capacity     = 1
  max_size             = 3
  min_size             = 1
  health_check_type    = "EC2"
  health_check_grace_period = 300
  force_delete          = true
  launch_configuration = aws_launch_configuration.example.id
  vpc_zone_identifier  = ["subnet-xxxxxxxx", "subnet-yyyyyyyy"]  # Replace with appropriate subnet IDs

  tag {
    key                 = "Name"
    value               = "Hw2Extension"
    propagate_at_launch = true
  }
}

# Target Group
resource "aws_lb_target_group" "example" {
  name     = "Hw2Extension-targets"
  port     = 8888
  protocol = "HTTP"
  vpc_id   = "vpc-xxxxxxxx"  # Replace with your VPC ID

  health_check {
    path = "/"
  }
}

# Listener
resource "aws_lb_listener" "example" {
  load_balancer_arn = aws_lb.example.arn
  port              = 8888
  protocol          = "HTTP"

  default_action {
    type             = "fixed-response"
    fixed_response_type = "200"
    fixed_response_body = "OK"
  }
}

# Auto Scaling Policy
resource "aws_autoscaling_policy" "example" {
  scaling_adjustment      = 1
  cooldown                = 200
  estimated_instance_warmup = 200
  metric_aggregation_type = "Average"
  policy_type             = "TargetTrackingScaling"

  target_tracking_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ASGAverageCPUUtilization"
    }

    target_value = 60  # Adjust the target value based on your requirements
  }

  scaling_adjustment_type = "ChangeInCapacity"

  # Link the policy to the Auto Scaling Group
  scaling_adjustment_type = "ChangeInCapacity"
  autoscaling_group_name  = ""
  name                    = ""
}
