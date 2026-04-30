from apps.backend.services.az_token_manager import AzureTokenManager

async def get_auth_headers():
    token_manager = AzureTokenManager().get_token()
    token = await token_manager
    return {"Authorization": f"Bearer {token}"}


# async def main():
#     # Await the function within an async context
#     token = await get_auth_headers()
#     print(token)

# Run the main event loop
# if __name__ == "__main__":
#     asyncio.run(main())