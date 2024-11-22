import io 
from io import StringIO
import logging
import os

import openpyxl as xl
import pandas as pd

from azure.durable_functions import DurableOrchestrationContext, Orchestrator

from Utilities.report_tools import ReportAssembler
from Utilities.utils import Helpers, BlobHandler


def orchestrator_function(context: DurableOrchestrationContext):
    """
    SubOrchestrator_Assembler: 
    
    Uses results from the SubOrchestrator_Generator to create a final, formatted .xlsx report, and uploads to blob

    Required Environment Variables:
        -STORAGE_ACCOUNT_NAME: the name of your storage account
        -ON_HAND_BLOB_CONTAINER_NAME: the name of the blob container within your storage        
    """
    # get input - results from the parallel task run 
    results = context.get_input()

    helpers = Helpers()  # exp backoff helper method

    # write the raw reports to an Excel buffer (one tab for each account)
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        for report_name, report_contents in results:
            df = pd.read_json(StringIO(report_contents))
            df.to_excel(writer, sheet_name=report_name, index=False)
    buffer.seek(0)

    # now visually format with xl (can't do this in the previous loop as pd doesn't save io objects)
    inst = ReportAssembler()
    wb = xl.load_workbook(buffer)
    for sheet in wb.sheetnames:
        account_initials = sheet.split(' ')[0]  # for table names
        ws = wb[sheet]
        inst.on_hand_report_formatter(ws, table_name=account_initials)
        buffer.seek(0)
    wb.save(buffer)
    buffer.seek(0)
    
    # upload buffer to blob container
    uploaded = False
    upload_attempt = 1
    max_attempts = 3
    while upload_attempt <= max_attempts:
        try: 
            blob_client = BlobHandler(
                storage_account=os.getenv('STORAGE_ACCOUNT_NAME'), 
                container_name=os.getenv('ON_HAND_BLOB_CONTAINER_NAME')
                )        
            blob_client.save_to_blob(buffer, save_as=f"On Hand Reports {inst.today}.xlsx")
            uploaded = True
            break
        
        except Exception as e:
            logging.error(f"Failed to upload finished report to blob - {str(e)}")
            helpers.exponential_backoff(upload_attempt)
    
    if not uploaded:
        raise RuntimeError(
            "Could not upload report to blob. Review the logs and check access to your storage account"
            )
    
    return None


main = Orchestrator.create(orchestrator_function)