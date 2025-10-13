import os
import logging

from azure.identity import DefaultAzureCredential, ClientSecretCredential


def get_azure_credential() -> DefaultAzureCredential | ClientSecretCredential:
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
