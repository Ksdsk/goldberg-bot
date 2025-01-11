import discord
import mysql.connector
from discord.ext import commands
import os
import math
import boto3

from constants import ALLOWLISTED_SERVER_IDS
from constants import SUBJECT_ID_TRANSLATOR
from constants import SCHOOL_ID_REVERSE_TRANSLATOR
from constants import DALHOUSIE_SUBJECT_LISTS

from dalsearch import dalsearch_interpreter

class Course_Commands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    course = discord.SlashCommandGroup(
        name="course", 
        description="Course related commands",
        guild_ids=ALLOWLISTED_SERVER_IDS
    )

    DEFAULT_EXPIRATION = 600

    async def get_subjects(ctx):
        return [subject for subject in DALHOUSIE_SUBJECT_LISTS if subject.startswith(ctx.value.upper())]


    @course.command(
        name="syllabus",
        description="Gets the syllabus of the course"
    )
    async def syllabus(
        self, ctx,
        subject: discord.Option(str, "Subject code, ex. CSCI", autocomplete=get_subjects),
        code: discord.Option(int, "Course code, ex. 2134")
    ):
        if not is_valid_code(code):
            await ctx.respond("**Error**: The course code digit must be 4.", ephemeral=True)
            return
        
        if not does_course_exist(subject, code):
            await ctx.respond("**Error**: This course does not exist, or has not been added yet to the database. Please try again later or reach out to @soondae!", ephemeral=True)
            return

        matching_syllabus = get_all_matching_syllabus(subject.upper(), code)

        if (len(matching_syllabus) == 0):
            embed=discord.Embed(title=f"Syllabus for {subject.upper()} {code}", description=f"Found {len(matching_syllabus)} matches.")
            embed.set_footer(text="Made by @soondae 🦆🦆🦆")
            await ctx.respond(embed=embed)
            return

        embed=discord.Embed(title=f"Syllabus for {subject.upper()} {code}", description=f"Found {len(matching_syllabus)} matches. Link expires in {int(self.DEFAULT_EXPIRATION / 60)} minutes!")
        
        for syllabus in matching_syllabus:
            embed.add_field(name=f"{extract_term_and_convert_to_readable(syllabus)} w/ {', '.join(extract_instructor_names(syllabus))}", 
                            value=f"[Download Link]({get_presigned_url_for_getobject(syllabus, self.DEFAULT_EXPIRATION)})", 
                            inline=False)

        embed.set_footer(text="Made by @soondae 🦆🦆🦆")
        
        await ctx.respond(embed=embed)

    @course.command(
        name="info",
        description="Gets basic information about courses"
    )
    async def info(
        self, ctx, 
        subject: discord.Option(str, "Subject code, ex. CSCI", autocomplete=get_subjects), 
        code: discord.Option(int, "Course code, ex. 2134")
    ):

        if not is_valid_code(code):
            await ctx.respond("**Error**: The course code digit must be 4.", ephemeral=True)
            return
        
        try:
            # Initial query to fetch courses
            cnx = get_db_connection()
            cursor = cnx.cursor()
            query = f"SELECT School_Id, Subject_Id, Course_Name, Course_Code, Course_Description, Course_SchoolUrl FROM Course WHERE Subject_Id = \"{SUBJECT_ID_TRANSLATOR.get(subject.upper())}\" AND Course_Code = {code}"
            cursor.execute(query)

            res = cursor.fetchone()

            if res == None:
                cursor.close()
                cnx.close()
                await ctx.respond("**Error**: This course does not exist, or has not been added yet to the database. Please try again later or reach out to @soondae!", ephemeral=True)
                return

            school_id = res[0]
            subject_id = res[1]
            course_name = clean_html_frags(res[2])
            course_code = res[3]
            course_description = res[4]
            course_schoolurl = res[5]
                
            # Second query to determine subject name
            subquery_cursor = cnx.cursor()
            subquery_find_subject_name = f"SELECT Subject_Name FROM `Subject` WHERE Subject_Id = \"{subject_id}\""
            subquery_cursor.execute(subquery_find_subject_name)

            prereqs = dalsearch_interpreter.get_course_prerequisites_as_markdown_strings(subject, course_code)

            embed = discord.Embed(title=f"{subject.upper()} {course_code}", url=f"{course_schoolurl}", description=f"{course_name}", color=0xfbf182)
            embed.add_field(name="Subject", value=f"{subquery_cursor.fetchone()[0]}", inline=True)
            embed.add_field(name="School", value=f"{SCHOOL_ID_REVERSE_TRANSLATOR.get(school_id)}", inline=True)
            embed.add_field(name="Description", value=f"{cut_limit(clean_html_frags(course_description))}", inline=False)
            
            if prereqs: 
                embed.add_field(name="Prerequisites", value=f"{prereqs}", inline=False)
            
            matching_syllabus = get_all_matching_syllabus(subject.upper(), code)
            if (len(matching_syllabus) == 0):
                embed.add_field(name="Latest Syllabus Link", value=f"No syllabus was found for this course!", inline=False)
            else:
                latest_syllabus = matching_syllabus[0]
                embed.add_field(name="Latest Syllabus Link", value=f"[{extract_term_and_convert_to_readable(latest_syllabus)} w/ {', '.join(extract_instructor_names(latest_syllabus))}]({get_presigned_url_for_getobject(latest_syllabus, self.DEFAULT_EXPIRATION)}) (expires in {int(self.DEFAULT_EXPIRATION / 60)} minutes)", inline=False)
            embed.set_footer(text="Made by @soondae 🦆🦆🦆")
            
            subquery_cursor.close()
            cursor.close()
            cnx.close()            
            
            await ctx.respond(embed=embed)
        except Exception as e:
            if cursor:
                cursor.close()

            if cnx:
                cnx.close()

            print(e)
            await ctx.respond("**Error**: Internal Service Exception. Please try again later or reach out to @soondae!", ephemeral=True)


def setup(bot):
    bot.add_cog(Course_Commands(bot))

def clean_html_frags(s: str):
    return s.replace("&amp;", "&")

def cut_limit(s: str):
    if len(s) > 1024:
        s = s[0:1020] + "..."
    return s

def is_valid_code(code: int):
    # Code must be an int that is 4 digits long
    if 4 != int(math.log10(code))+1:
        return False
    return True

def get_db_connection():
    return mysql.connector.connect(
        user=os.getenv("MYSQL_DB_USERNAME"),
        password=os.getenv("MYSQL_DB_PASSWORD"),
        database=os.getenv("MYSQL_DB_SCHEMA_NAME"),
        host=os.getenv("MYSQL_DB_HOSTNAME")
    )

def get_s3_bucket():
    return boto3.resource(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
    ).Bucket(os.getenv("AWS_S3_BUCKET_NAME"))

def get_s3_client():
    return boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
    )

def get_s3_bucket_name():
    return os.getenv("AWS_S3_BUCKET_NAME")

def sort_syllabus_name_reverse_chronologically(arr: list):
    arr.sort(key=lambda x: x[11:13], reverse=True)

def extract_instructor_names(filename: str):
    instructor_names = []
    extract = filename.removesuffix(".pdf").split("_")[3:]

    for i in range(0,len(extract),2):
        instructor_names.append(f"{extract[i]} {extract[i+1]}")

    return instructor_names
    
def extract_term_and_convert_to_readable(filename: str):
    term = filename[10:11]
    year = filename[11:13]
    if term == "F":
        return f"Fall 20{year}"
    elif term == "S":
        return f"Summer 20{year}"
    elif term == "W":
        return f"Winter 20{year}"
    else:
        return "Unknown"
    
def does_course_exist(subject: str, code: int):
    cnx = get_db_connection()
    cursor = cnx.cursor()
    query = f"SELECT School_Id, Subject_Id, Course_Name, Course_Code, Course_Description, Course_SchoolUrl FROM Course WHERE Subject_Id = \"{SUBJECT_ID_TRANSLATOR.get(subject.upper())}\" AND Course_Code = {code}"
    cursor.execute(query)

    res = cursor.fetchone()

    cursor.close()
    cnx.close()

    if res == None:
        return False

    return True

def get_all_matching_syllabus(subject: str, code: int):
    s3_client = get_s3_client()
    matching_syllabus = []

    for item in s3_client.list_objects_v2(Bucket=get_s3_bucket_name())["Contents"]:
        if item["Key"].startswith(f"{subject.upper()}_{code}"):
            matching_syllabus.append(item["Key"])

    sort_syllabus_name_reverse_chronologically(matching_syllabus)

    return matching_syllabus

def get_presigned_url_for_getobject(filename: str, expiry: int):
    s3_client = get_s3_client()
    return s3_client.generate_presigned_url('get_object', Params={'Bucket': get_s3_bucket_name(), 'Key': filename}, ExpiresIn=expiry)