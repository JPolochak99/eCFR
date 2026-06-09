
from cfr_exporterOld.table_parser import table_html_to_df
from cfr_exporterOld.table_parser import format_df

def prepare_table(selected_item):
    selected_df = table_html_to_df(selected_item["html"])
    formatted_df, _ = format_df(selected_df)
    return selected_df, formatted_df