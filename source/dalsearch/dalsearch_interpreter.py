import requests

from constants import DALSEARCH_COURSE_API_ENDPOINT_FORMAT


def get_detailed_course_info(subject: str, code: int):
    call_url = DALSEARCH_COURSE_API_ENDPOINT_FORMAT % f"{subject}{code}"
    try:
        response = requests.get(call_url)
        if response.status_code == 200:
            return response.json()
        else:
            print("**Error**: ", response.status_code)
            return None
    except Exception as e:
        print(e)

    return None

def get_course_prerequisites_as_markdown_strings(subject: str, code: int):
    json = get_detailed_course_info(subject, code)
    markdown_strings = []
    if json["prerequisites"] != None:
        for prereq in json["prerequisites"]:
            markdown_strings.append(f"[{prereq[:4]} {prereq[4:8]}]({get_school_url(prereq[:4], prereq[4:8])})")
        return ", ".join(markdown_strings)
    else: 
        return None
    
def get_school_url(subject: str, code: str):
    return f"https://academiccalendar.dal.ca/Catalog/ViewCatalog.aspx?pageid=viewcatalog&entitytype=CID&entitycode={subject}+{code}"
    