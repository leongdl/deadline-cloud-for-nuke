# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

"""
Utilities for interacting with AWS ECR (Elastic Container Registry).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from botocore.exceptions import ClientError, NoCredentialsError
from deadline.client.api import get_boto3_client

# Handle different Qt imports for different Nuke versions
try:
    # For Nuke 16+
    from PySide6.QtWidgets import QMessageBox
except ImportError:
    # For Nuke 13-15
    from PySide2.QtWidgets import QMessageBox  # type: ignore


@dataclass
class ECRRepository:
    """Represents an ECR repository with its name and URI."""

    name: str
    uri: str


@dataclass
class ECRImage:
    """Represents an ECR image with its tag and ARN."""

    tag: str
    image_digest: str
    pushed_at: Optional[Any] = None


def list_ecr_repositories() -> list[ECRRepository]:
    """
    List all ECR repositories in the current AWS account.

    Returns:
        A list of ECRRepository objects. Returns empty list if there's an error.
    """
    try:
        ecr_client = get_boto3_client("ecr")
        repositories = []
        paginator = ecr_client.get_paginator("describe_repositories")

        for page in paginator.paginate():
            for repo in page.get("repositories", []):
                repositories.append(
                    ECRRepository(name=repo["repositoryName"], uri=repo["repositoryUri"])
                )

        return sorted(repositories, key=lambda r: r.name)
    except NoCredentialsError:
        QMessageBox.critical(
            None,
            "AWS Credentials Error",
            "AWS credentials are not configured. Please configure your AWS credentials to access ECR repositories.",
        )
        return []
    except ClientError as e:
        QMessageBox.critical(
            None,
            "ECR Error",
            f"Error accessing ECR repositories: {str(e)}",
        )
        return []
    except Exception as e:
        QMessageBox.critical(
            None,
            "Unexpected Error",
            f"An unexpected error occurred while listing ECR repositories: {str(e)}",
        )
        return []


def list_ecr_images(repository_name: str) -> list[ECRImage]:
    """
    List all images in an ECR repository, sorted by time with tagged images first.

    Args:
        repository_name: The name of the ECR repository.

    Returns:
        A list of ECRImage objects sorted by pushed time (newest first),
        with tagged images appearing before untagged ones.
        Returns empty list if there's an error (error is shown in a dialog).
    """
    try:
        ecr_client = get_boto3_client("ecr")
        images = []
        paginator = ecr_client.get_paginator("describe_images")

        for page in paginator.paginate(repositoryName=repository_name):
            for image_detail in page.get("imageDetails", []):
                tags = image_detail.get("imageTags", [])
                pushed_at = image_detail.get("imagePushedAt")
                image_digest = image_detail.get("imageDigest", "")

                # Create an ECRImage for each tag, or one for untagged images
                if tags:
                    for tag in tags:
                        images.append(
                            ECRImage(tag=tag, image_digest=image_digest, pushed_at=pushed_at)
                        )
                else:
                    # Untagged image
                    images.append(
                        ECRImage(
                            tag="<untagged>", image_digest=image_digest, pushed_at=pushed_at
                        )
                    )

        # Sort: tagged images first, then by pushed time (newest first)
        images.sort(
            key=lambda img: (
                img.tag == "<untagged>",  # False (tagged) comes before True (untagged)
                -(img.pushed_at.timestamp() if img.pushed_at else 0),  # Newest first
            )
        )

        return images
    except NoCredentialsError:
        QMessageBox.critical(
            None,
            "AWS Credentials Error",
            "AWS credentials are not configured. Please configure your AWS credentials to access ECR images.",
        )
        return []
    except ClientError as e:
        QMessageBox.critical(
            None,
            "ECR Error",
            f"Error accessing ECR images for repository '{repository_name}': {str(e)}",
        )
        return []
    except Exception as e:
        QMessageBox.critical(
            None,
            "Unexpected Error",
            f"An unexpected error occurred while listing ECR images: {str(e)}",
        )
        return []
