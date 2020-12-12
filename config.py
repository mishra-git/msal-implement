class Config(object):
    # In a production app, store this instead in KeyVault or an environment variable
    # TODO: Enter your client secret from Azure AD below
    CLIENT_SECRET = "Dq08S._vC_~4_2BUcKLaT9xAOa3U.j.V5U" 

    #AUTHORITY = "https://login.microsoftonline.com/common"  # For multi-tenant app
    AUTHORITY = "https://login.microsoftonline.com/3de481f9-a491-4077-9ed7-5daf9bc5e642"

    # TODO: Enter your application client ID here
    CLIENT_ID = "3db03fa0-6222-4d92-84c6-f5450415dd40"

    # TODO: Enter the redirect path you want to use for OAuth requests
    #   Note that this will be the end of the URI entered back in Azure AD
    REDIRECT_PATH = "/cmsproject"  # Used to form an absolute URL, 
        # which must match your app's redirect_uri set in AAD

    # You can find the proper permission names from this document
    # https://docs.microsoft.com/en-us/graph/permissions-reference
    SCOPE = ["User.Read"]

    SESSION_TYPE = "filesystem"  # So token cache will be stored in server-side session