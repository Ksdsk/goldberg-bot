import requests
import re
import mysql.connector
import os

from uuid import uuid4
from dotenv import load_dotenv
from bs4 import BeautifulSoup


COURSE_SUBJECT = "ASSC"
COURSE_CODES_TO_IGNORE = [

]
COURSE_LOWER_BOUND = 1000
COURSE_UPPER_BOUND = 10000

SUBJECT_ID_TRANSLATOR = {
    "CSCI": "a38d54eb-559d-4d6a-9a28-edfc1a4e67d5",
    "PSYO": "15f332e2-1f8a-428d-ab4e-41d06e9435fe",
    "MATH": "02074a28-392e-48e8-8ed3-417205cd1915",
    "STAT": "f49f0a99-2481-4a1d-95ad-095bd7d6e72c",
    "BUSS": "2dfdb588-0589-45d1-8dbb-0b5bc3b8e523",
    "ECON": "078792e2-b807-45f1-b923-35608d8f6df5",
    "MGMT": "f5f6e5ff-cd3e-48a1-81f7-e4fc11460672",
    "ASSC": "e877fae1-e7c8-49a1-bc14-cd35314444f7",
    "ENGL": "8dc800dd-7b81-43b7-90b9-f25cfa838cc7"
}

SCHOOL_ID_TRANSLATOR = {
    "Dalhousie University": "18345bee-1ad5-45cf-bd7e-61d660845f8f"
}

load_dotenv()

cnx = mysql.connector.connect(
    user=os.getenv("MYSQL_DB_USERNAME"),
    password=os.getenv("MYSQL_DB_PASSWORD"),
    database=os.getenv("MYSQL_DB_SCHEMA_NAME"),
    host=os.getenv("MYSQL_DB_HOSTNAME")
)
cursor = cnx.cursor()

def html_tag_remover(s: str):
    while len(re.findall(r">(.*)<", s)) > 0:
        s = re.sub(r"<.*>", re.findall(r">(.*)<", s)[0], s)
    return s

for code in range(COURSE_LOWER_BOUND, COURSE_UPPER_BOUND):

    if code in COURSE_CODES_TO_IGNORE:
        continue

    schoolurl = f"https://academiccalendar.dal.ca/Catalog/ViewCatalog.aspx?pageid=viewcatalog&entitytype=CID&entitycode={COURSE_SUBJECT}+{code}"
    r = requests.get(schoolurl)
    soup = BeautifulSoup(r.content, "html.parser")

    title_soup = soup.find("span", "catalogtitle")
    title_findall = re.findall(r">Welcome - (.*)<", str(title_soup))

    if len(title_findall) == 0:
        continue

    title = title_findall[0]

    desc_soup = soup.find("div", "maincontent")
    desc = re.findall(r"CREDIT HOURS: \d<br/>\r*(.*?)<br/>", str(desc_soup).replace("\n", ""))[0]
    desc = str(desc).replace("\"", "\\\"")
    desc = html_tag_remover(desc)

    print(f"{COURSE_SUBJECT} {code} - {title}")
    print(f"{desc}")

    query = f"INSERT INTO Course (Course_Id, Subject_Id, School_Id, Course_Name, Course_Code, Course_Description, Course_SchoolUrl) VALUES (\"{uuid4()}\", \"{SUBJECT_ID_TRANSLATOR[COURSE_SUBJECT.upper()]}\", \"{SCHOOL_ID_TRANSLATOR["Dalhousie University"]}\", \"{title}\", {code}, \"{desc}\", \"{schoolurl}\")"
    cursor.execute(query)
    cnx.commit()


cursor.close()
cnx.close()