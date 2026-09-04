from core.mcp_client import call_mcp_tool
from core.state import GraphState

def fetch_company_info_node(state: GraphState) -> dict:
    result = call_mcp_tool("get_company_overview",{"company_name":state["company_name"]})

    if result.get("found"):
        msg = f"[Company_info] '{state["company_name"]}' info found (source: {result['source']})"
    else:
        msg = f"[Company_info]'{state["company_name"]} Didn't found on wikkipedia- we will use general preparation'"

    
    return {
        "company_overview" : result,
        "messages": [{"role":"assistant","content": msg}]
    }