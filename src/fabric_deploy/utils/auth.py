"""
Azure authentication utilities
"""

import os
import logging
from typing import Optional

from azure.identity import DefaultAzureCredential, ClientSecretCredential


def get_azure_credential() -> DefaultAzureCredential:
    """
    Get Azure credential for authentication

    Returns:
        Azure credential instance
    """
    logger = logging.getLogger(__name__)

    # Check if we have explicit service principal credentials
    client_id = os.getenv("AZURE_CLIENT_ID")
    client_secret = os.getenv("AZURE_CLIENT_SECRET")
    tenant_id = os.getenv("AZURE_TENANT_ID")

    if client_id and client_secret and tenant_id:
        logger.info("Using service principal authentication")
        return ClientSecretCredential(tenant_id=tenant_id, client_id=client_id, client_secret=client_secret)

    # Fall back to default credential chain
    logger.info("Using default Azure credential chain")
    return DefaultAzureCredential()


def validate_azure_credentials() -> bool:
    """
    Validate that Azure credentials are available and working

    Returns:
        True if credentials are valid, False otherwise
    """
    logger = logging.getLogger(__name__)

    try:
        credential = get_azure_credential()

        # Try to get a token to validate credentials
        # Using the Fabric scope
        token = credential.get_token("https://analysis.windows.net/powerbi/api/.default")

        if token and token.token:
            logger.info("Azure credentials validated successfully")
            return True
        else:
            logger.error("Failed to obtain Azure access token")
            return False

    except Exception as e:
        logger.error(f"Azure credential validation failed: {e}")
        return False


def get_fabric_token(credential: Optional[DefaultAzureCredential] = None) -> str:
    """
    Get an access token for Microsoft Fabric

    Args:
        credential: Optional Azure credential, will create default if not provided

    Returns:
        Access token string
    """
    if credential is None:
        credential = get_azure_credential()

    token = credential.get_token("https://analysis.windows.net/powerbi/api/.default")
    return token.token
