# AWS S3 Setup Guide

This document explains how to configure the AI Document Intelligence Platform to use AWS S3 for document storage instead of MinIO.

## Overview

The application is designed to work with both:
- **MinIO** (local development) - S3-compatible object storage
- **AWS S3** (production) - Amazon's cloud storage service

Both services use the same S3 API, so switching between them only requires configuration changes.

## Prerequisites

- AWS Account
- AWS CLI installed (optional, for easier setup)
- Access to create S3 buckets and IAM users

## Step 1: Create S3 Bucket

### Option A: Using AWS Console

1. Go to [AWS S3 Console](https://console.aws.amazon.com/s3/)
2. Click "Create bucket"
3. Configure bucket:
   - **Bucket name**: `ai-doc-intelligence-prod` (must be globally unique)
   - **Region**: `us-east-1` (or your preferred region)
   - **Block Public Access**: Keep all blocks enabled (recommended)
   - **Versioning**: Optional (recommended for production)
   - **Encryption**: Enable server-side encryption (AES-256)
4. Click "Create bucket"

### Option B: Using AWS CLI

```bash
# Create bucket
aws s3 mb s3://ai-doc-intelligence-prod --region us-east-1

# Enable versioning (optional)
aws s3api put-bucket-versioning \
    --bucket ai-doc-intelligence-prod \
    --versioning-configuration Status=Enabled

# Enable encryption
aws s3api put-bucket-encryption \
    --bucket ai-doc-intelligence-prod \
    --server-side-encryption-configuration '{
        "Rules": [{
            "ApplyServerSideEncryptionByDefault": {
                "SSEAlgorithm": "AES256"
            }
        }]
    }'
```

## Step 2: Create IAM User for Application

### Option A: Using AWS Console

1. Go to [IAM Console](https://console.aws.amazon.com/iam/)
2. Navigate to "Users" → "Create user"
3. User details:
   - **User name**: `ai-doc-intelligence-app`
   - **Access type**: Programmatic access
4. Attach policy directly:
   - Click "Attach policies directly"
   - Click "Create policy"
   - Use the JSON policy below
5. Save the **Access Key ID** and **Secret Access Key**

### IAM Policy

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "DocumentStorageAccess",
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject",
                "s3:DeleteObject",
                "s3:ListBucket",
                "s3:HeadBucket"
            ],
            "Resource": [
                "arn:aws:s3:::ai-doc-intelligence-prod",
                "arn:aws:s3:::ai-doc-intelligence-prod/*"
            ]
        }
    ]
}
```

### Option B: Using AWS CLI

```bash
# Create IAM user
aws iam create-user --user-name ai-doc-intelligence-app

# Create and attach policy
cat > s3-policy.json <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "DocumentStorageAccess",
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject",
                "s3:DeleteObject",
                "s3:ListBucket",
                "s3:HeadBucket"
            ],
            "Resource": [
                "arn:aws:s3:::ai-doc-intelligence-prod",
                "arn:aws:s3:::ai-doc-intelligence-prod/*"
            ]
        }
    ]
}
EOF

aws iam create-policy \
    --policy-name AIDocIntelligenceS3Access \
    --policy-document file://s3-policy.json

# Attach policy to user
aws iam attach-user-policy \
    --user-name ai-doc-intelligence-app \
    --policy-arn arn:aws:iam::YOUR_ACCOUNT_ID:policy/AIDocIntelligenceS3Access

# Create access keys
aws iam create-access-key --user-name ai-doc-intelligence-app
```

Save the output containing `AccessKeyId` and `SecretAccessKey`.

## Step 3: Configure Application

### For Docker Compose

Update the environment variables in `docker-compose.yml` or create a `.env` file:

```env
# AWS S3 Configuration
S3_ENDPOINT_URL=              # Leave empty for AWS S3 (not MinIO)
S3_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
S3_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
S3_BUCKET_NAME=ai-doc-intelligence-prod
S3_REGION=us-east-1
USE_SSL=true                  # Always use SSL for AWS
```

### For Kubernetes

Update the secrets in `k8s/config/secrets.yaml`:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: ai-doc-secrets
  namespace: ai-doc-intelligence
type: Opaque
stringData:
  # ... other secrets ...

  # AWS S3 Configuration
  S3_ENDPOINT_URL: ""  # Empty for AWS S3
  S3_ACCESS_KEY_ID: "AKIAIOSFODNN7EXAMPLE"
  S3_SECRET_ACCESS_KEY: "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
  S3_BUCKET_NAME: "ai-doc-intelligence-prod"
  S3_REGION: "us-east-1"
```

Then apply the changes:

```bash
kubectl apply -f k8s/config/secrets.yaml
kubectl rollout restart deployment -n ai-doc-intelligence
```

### Environment Variable Reference

| Variable | Description | MinIO Value | AWS S3 Value |
|----------|-------------|-------------|--------------|
| `S3_ENDPOINT_URL` | S3 API endpoint | `http://minio:9000` | `` (empty) |
| `S3_ACCESS_KEY_ID` | Access key | `minioadmin` | Your AWS access key |
| `S3_SECRET_ACCESS_KEY` | Secret key | `minioadmin` | Your AWS secret key |
| `S3_BUCKET_NAME` | Bucket name | `documents` | Your bucket name |
| `S3_REGION` | AWS region | `us-east-1` | Your region |
| `USE_SSL` | Use HTTPS | `false` | `true` |

## Step 4: Test the Configuration

### Upload a Test Document

```bash
# Get auth token
TOKEN=$(curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password"}' \
  | jq -r '.access_token')

# Upload document
curl -X POST http://localhost:8001/documents/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@test.pdf"
```

### Verify in AWS Console

1. Go to S3 Console
2. Open your bucket (`ai-doc-intelligence-prod`)
3. Verify files are being uploaded

### Check Application Logs

```bash
# Docker Compose
docker-compose logs document-service | grep S3
docker-compose logs ingestion-worker | grep S3

# Kubernetes
kubectl logs -l app=document-service -n ai-doc-intelligence | grep S3
kubectl logs -l app=ingestion-worker -n ai-doc-intelligence | grep S3
```

## Cost Estimation

AWS S3 Free Tier (12 months):
- **Storage**: 5 GB
- **GET Requests**: 20,000 per month
- **PUT Requests**: 2,000 per month

After free tier:
- **Storage**: ~$0.023 per GB per month (us-east-1)
- **GET Requests**: $0.0004 per 1,000 requests
- **PUT Requests**: $0.005 per 1,000 requests
- **Data Transfer Out**: First 100GB free per month, then $0.09 per GB

**Example Demo Usage** (monthly):
- 100 documents × 1MB each = 100 MB storage (~$0.002)
- 500 uploads = 500 PUT requests (~$0.0025)
- 2,000 downloads = 2,000 GET requests (~$0.0008)
- **Total**: ~$0.005 per month (essentially free within free tier)

## Switching Back to MinIO

To switch back to MinIO for local development:

```env
S3_ENDPOINT_URL=http://minio:9000
S3_ACCESS_KEY_ID=minioadmin
S3_SECRET_ACCESS_KEY=minioadmin
S3_BUCKET_NAME=documents
S3_REGION=us-east-1
USE_SSL=false
```

## Security Best Practices

1. **Never commit credentials**: Use environment variables or secret managers
2. **Use IAM roles** (for EC2/ECS/EKS deployments):
   - Eliminates need for access keys
   - Automatically rotates credentials
3. **Enable MFA** for AWS console access
4. **Enable S3 bucket versioning** for data protection
5. **Enable CloudTrail** for audit logging
6. **Use VPC Endpoints** for private connectivity (production)
7. **Implement lifecycle policies** to archive old documents to S3 Glacier

## Troubleshooting

### Error: "NoSuchBucket"
- Verify bucket exists and name is correct
- Check region matches configuration

### Error: "AccessDenied"
- Verify IAM policy allows required actions
- Check access key and secret are correct
- Ensure bucket policy doesn't block access

### Error: "InvalidAccessKeyId"
- Access key is incorrect or deleted
- Create new access key in IAM console

### SSL Certificate Errors
- Ensure `USE_SSL=true` for AWS S3
- Ensure `USE_SSL=false` for local MinIO

## Additional Resources

- [AWS S3 Documentation](https://docs.aws.amazon.com/s3/)
- [boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [S3 Pricing Calculator](https://calculator.aws/#/createCalculator/S3)
