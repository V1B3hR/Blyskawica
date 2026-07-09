"""
Terraform Infrastructure-as-Code Generator
Generates Terraform configurations for cloud deployment
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class CloudProvider(Enum):
    """Supported cloud providers"""

    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"


@dataclass
class TerraformConfig:
    """Terraform configuration"""

    provider: CloudProvider
    region: str
    project_name: str
    environment: str
    enable_monitoring: bool
    enable_backup: bool


class TerraformGenerator:
    """
    Generates Terraform Infrastructure-as-Code configurations

    Features:
    - Multi-cloud support (AWS, Azure, GCP)
    - Database provisioning
    - Storage buckets
    - Networking
    - Monitoring integration
    """

    def __init__(self, config: TerraformConfig):
        """Initialize Terraform generator"""
        self.config = config

    def generate_provider_config(self) -> str:
        """Generate Terraform provider configuration"""
        if self.config.provider == CloudProvider.AWS:
            return self._generate_aws_provider()
        elif self.config.provider == CloudProvider.AZURE:
            return self._generate_azure_provider()
        elif self.config.provider == CloudProvider.GCP:
            return self._generate_gcp_provider()
        else:
            raise ValueError(f"Unsupported provider: {self.config.provider}")

    def _generate_aws_provider(self) -> str:
        """Generate AWS provider configuration"""
        return f"""
terraform {{
  required_version = ">= 1.0"
  required_providers {{
    aws = {{
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }}
  }}
}}

provider "aws" {{
  region = "{self.config.region}"
  
  default_tags {{
    tags = {{
      Project     = "{self.config.project_name}"
      Environment = "{self.config.environment}"
      ManagedBy   = "Terraform"
    }}
  }}
}}
"""

    def _generate_azure_provider(self) -> str:
        """Generate Azure provider configuration"""
        return f"""
terraform {{
  required_version = ">= 1.0"
  required_providers {{
    azurerm = {{
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }}
  }}
}}

provider "azurerm" {{
  features {{}}
  
  subscription_id = var.azure_subscription_id
}}
"""

    def _generate_gcp_provider(self) -> str:
        """Generate GCP provider configuration"""
        return f"""
terraform {{
  required_version = ">= 1.0"
  required_providers {{
    google = {{
      source  = "hashicorp/google"
      version = "~> 5.0"
    }}
  }}
}}

provider "google" {{
  project = var.gcp_project_id
  region  = "{self.config.region}"
}}
"""

    def generate_database(self) -> str:
        """Generate database infrastructure"""
        if self.config.provider == CloudProvider.AWS:
            return self._generate_aws_rds()
        elif self.config.provider == CloudProvider.AZURE:
            return self._generate_azure_database()
        elif self.config.provider == CloudProvider.GCP:
            return self._generate_gcp_cloudsql()
        return ""

    def _generate_aws_rds(self) -> str:
        """Generate AWS RDS PostgreSQL"""
        backup_config = ""
        if self.config.enable_backup:
            backup_config = """
  backup_retention_period = 7
  backup_window          = "03:00-04:00"
"""

        return f"""
resource "aws_db_instance" "nethical_recon" {{
  identifier     = "{self.config.project_name}-{self.config.environment}"
  engine         = "postgres"
  engine_version = "15.3"
  instance_class = "db.t3.medium"
  
  allocated_storage     = 100
  max_allocated_storage = 500
  storage_type         = "gp3"
  storage_encrypted    = true
  
  db_name  = "nethical_recon"
  username = var.db_username
  password = var.db_password
  
  vpc_security_group_ids = [aws_security_group.database.id]
  db_subnet_group_name   = aws_db_subnet_group.database.name
  {backup_config}
  multi_az               = true
  skip_final_snapshot    = false
  final_snapshot_identifier = "{self.config.project_name}-final-snapshot"
  
  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]
}}

resource "aws_security_group" "database" {{
  name        = "{self.config.project_name}-db-sg"
  description = "Security group for Nethical Recon database"
  vpc_id      = aws_vpc.main.id
  
  ingress {{
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [aws_vpc.main.cidr_block]
  }}
}}
"""

    def _generate_azure_database(self) -> str:
        """Generate Azure Database for PostgreSQL"""
        return f"""
resource "azurerm_postgresql_flexible_server" "nethical_recon" {{
  name                = "{self.config.project_name}-{self.config.environment}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  
  administrator_login    = var.db_username
  administrator_password = var.db_password
  
  sku_name   = "GP_Standard_D4s_v3"
  storage_mb = 102400
  version    = "15"
  
  backup_retention_days = 7
  geo_redundant_backup_enabled = true
}}
"""

    def _generate_gcp_cloudsql(self) -> str:
        """Generate GCP Cloud SQL PostgreSQL"""
        return f"""
resource "google_sql_database_instance" "nethical_recon" {{
  name             = "{self.config.project_name}-{self.config.environment}"
  database_version = "POSTGRES_15"
  region           = "{self.config.region}"
  
  settings {{
    tier = "db-custom-4-16384"
    
    backup_configuration {{
      enabled    = true
      start_time = "03:00"
      point_in_time_recovery_enabled = true
    }}
    
    ip_configuration {{
      ipv4_enabled = false
      private_network = google_compute_network.main.id
    }}
  }}
}}
"""

    def generate_storage(self) -> str:
        """Generate cloud storage bucket"""
        if self.config.provider == CloudProvider.AWS:
            return self._generate_s3_bucket()
        elif self.config.provider == CloudProvider.AZURE:
            return self._generate_azure_storage()
        elif self.config.provider == CloudProvider.GCP:
            return self._generate_gcs_bucket()
        return ""

    def _generate_s3_bucket(self) -> str:
        """Generate AWS S3 bucket"""
        return f"""
resource "aws_s3_bucket" "nethical_recon" {{
  bucket = "{self.config.project_name}-{self.config.environment}-data"
}}

resource "aws_s3_bucket_versioning" "nethical_recon" {{
  bucket = aws_s3_bucket.nethical_recon.id
  
  versioning_configuration {{
    status = "Enabled"
  }}
}}

resource "aws_s3_bucket_encryption" "nethical_recon" {{
  bucket = aws_s3_bucket.nethical_recon.id
  
  rule {{
    apply_server_side_encryption_by_default {{
      sse_algorithm = "AES256"
    }}
  }}
}}

resource "aws_s3_bucket_public_access_block" "nethical_recon" {{
  bucket = aws_s3_bucket.nethical_recon.id
  
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}}
"""

    def _generate_azure_storage(self) -> str:
        """Generate Azure Storage Account"""
        return f"""
resource "azurerm_storage_account" "nethical_recon" {{
  name                     = "{self.config.project_name.replace('-', '')}{self.config.environment}"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "GRS"
  
  enable_https_traffic_only = true
  min_tls_version          = "TLS1_2"
}}

resource "azurerm_storage_container" "data" {{
  name                  = "data"
  storage_account_name  = azurerm_storage_account.nethical_recon.name
  container_access_type = "private"
}}
"""

    def _generate_gcs_bucket(self) -> str:
        """Generate GCP Cloud Storage bucket"""
        return f"""
resource "google_storage_bucket" "nethical_recon" {{
  name     = "{self.config.project_name}-{self.config.environment}-data"
  location = "{self.config.region}"
  
  uniform_bucket_level_access = true
  
  versioning {{
    enabled = true
  }}
  
  encryption {{
    default_kms_key_name = google_kms_crypto_key.storage.id
  }}
}}
"""

    def export_all(self) -> dict[str, str]:
        """Export all Terraform configurations"""
        return {
            "provider.tf": self.generate_provider_config(),
            "database.tf": self.generate_database(),
            "storage.tf": self.generate_storage(),
        }
