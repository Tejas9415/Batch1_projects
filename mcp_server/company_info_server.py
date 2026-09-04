import json
import requests

from mcp.server.mcpserver import MCPServer

#create mcp server
mcp = MCPServer("company-info")

HEADERS = {
    "User-Agent": "InterviewPrepCoach/1.0 (student project)"
}

@mcp.tool()
def get_company_overview(company_name: str) -> str:
    """Get a real, free source overview of company from Wikkipedia"""
    try:
        page_name = company_name.strip().replace(" ","_")

        url = (
           "https://en.wikipedia.org/api/rest_v1/page/summary/"
           f"{page_name}"
        )

        response = requests.get(
            url,
            headers= HEADERS,
            timeout= 10
        )

        if response.status_code !=200:
            return json.dumps({
                "found": False,
                "note":(
                    f"'{company_name}' is not found on Wikkipedia. Please use another website or Linekdin"
                )
            })
        data = response.json()

        return json.dumps({
            "found": True,
            "source": "wikipedia",
            "title": data.get("title", company_name),
            "description": data.get("description", ""),
            "summary": data.get("extract", "")

        })
    except Exception as e:
        return json.dumps({
            "found": False,
            "error": str(e)
        })
    
if __name__ == "__main__":
    mcp.run(transport="stdio")
