from io import StringIO
from typing import List, Tuple, TypedDict

import pandas as pd

from Utilities.report_tools import ReportAssembler

class CompilerDict(TypedDict):
    account_name: str
    orders: List[str]
    inventory: List[str]

def main(name: CompilerDict) -> Tuple[str, str]:
    """
    Intended to compile the following activities and pivot the data into a raw on-hand report for 1 account;
        -Activity_Order1
        -Activity_Order2
        -Activity_Order3
        -Activity_Inventory
        
    Parameters:
        -name: A dictionary with 3 items conforming to the CompilerDict class format
        (pass orders/inventory in lists even if only one json is being passed)
    
    Example_Dict = {
        'account_name': 'BIZ',
        'orders': [orders1, orders2, orders...n],
        'inventory': [inventory1]
    }
        
    Returns: 
        -Tuple[str, str]: The name of the report, and the compiled on-hand report as json string
    """
    # extract needed values from the input
    account_name = name.get('account_name')
    orders_str_list = name.get('orders')
    inventory_str_list = name.get('inventory')
    
    # compile the orders jsons to one df    
    order_df_list = [pd.read_json(StringIO(orders)) for orders in orders_str_list]
    order_df = pd.concat(order_df_list, ignore_index=True).drop_duplicates() 
                          
    # compile the inventory jsons to one df  
    inv_df_list = [pd.read_json(StringIO(inventory)) for inventory in inventory_str_list]
    inventory_df = pd.concat(inv_df_list, ignore_index=True).drop_duplicates()
    
    # generate pivot table df
    assembler = ReportAssembler(account_name=account_name)
    final_df = assembler.on_hand_report_compiler(orders=order_df, inventory=inventory_df)
    
    # convert back to json
    final_df = final_df.to_json(orient='records')
    report_name = assembler.set_on_hand_report_name()        

    return report_name, final_df    
