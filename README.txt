This is an ETL pipeline that utilizes durable functions.

It generates several reports from Amazon SP-API for several accounts. The reports are requested sequentially for each individual account to prevent throttle, but runs each account in parallel to optimize runtime. 

The report generated is a 90D sell-thru. It is uploaded to a blob container. Example .xlsx output included in main branch.

    Requirements: 
        (1). AZ Key Vault(s) with SP-API keys: [client secret, client id, refresh token, rotation deadline] 

        (2). Environment Variables in local.settings.example.json created in your Function App settings

    Example: 
        (a). For account "Platinum Organisation", create a KV "po-kv"
        (b). Add the SP-API keys specified in (1) to this new KV as secrets          
        (c). In your Function App, create the env-variables specified in (2)
        (d). If you have several accounts, create a separate KV for each, and add acc initials to ACCOUNTS_LIST

        In this scenario, modify ACCOUNTS_LIST to include 'PO' (e.g. "['acc1', 'PO']")
        Then, create an env-var "PO_VAULT_NAME" - its value would be the name of the KV ("po-kv")
        Next, pass the SPI-API keys from (1) as Function App env-variables - title them exactly as shown in (2)
        For example, within KV "po-kv" create secret name "po-client-secret" with secret value "ABCD1234"
        Then, in the Function App, create an env-variable "CLIENT_SECRET" with value "po-client-secret"
        Repeat for 'CLIENT_SECRET', 'REFRESH_TOKEN' and 'ROTATION_DEADLINE'
        
        (TL;DR - the environment variables point to the key-names, which point to the secret values)

        'MARKETPLACE_ID', 'ENDPOINT', 'TOKEN_REQUEST_URL' can be simply entered as env-variables without KV
                             
    Considerations:        
        -Maximum date range for any report in this API is 31 days. For longer ranges, run in loops
        
        -This class uses `DefaultAzureCredential` authentication, so ensure your managed identities are in order

        -Eager-validates environment variables and keys, so ensure the above above requirements are all met

        -Full list of available reports to generate using this class: 
        https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba    