import discord
import mysql.connector
from discord.ext import commands
import os
import math
import boto3
import asyncio
import re

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
        
        await ctx.defer(ephemeral=False)

        matching_syllabus = get_all_matching_syllabus(subject.upper(), code)

        if (len(matching_syllabus) == 0):
            embed=discord.Embed(title=f"Syllabus for {subject.upper()} {code}", description=f"Found {len(matching_syllabus)} matches.")
            embed.set_footer(text="Made by @soondae 🦆🦆🦆")
            await ctx.respond(embed=embed)
            return

        embed=discord.Embed(title=f"Syllabus for {subject.upper()} {code}", description=f"Showing the first {min(len(matching_syllabus), 10)} matches. Link expires in {int(self.DEFAULT_EXPIRATION / 60)} minutes!")
        
        ct = 1
        for syllabus in matching_syllabus:
            if ct == 10:
                break
            ct += 1
            embed.add_field(name=f"{syllabus}", 
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
                embed.add_field(name="Latest Syllabus Link", value=f"[{latest_syllabus}]({get_presigned_url_for_getobject(latest_syllabus, self.DEFAULT_EXPIRATION)})", inline=False)
                embed.add_field(name="", value=f"Use `/course syllabus {subject.upper()} {code}` to get more syllabus for this course!", inline=False)

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
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        config=boto3.session.Config(signature_version='s3v4')
    )

def get_s3_bucket_name():
    return os.getenv("AWS_S3_BUCKET_NAME")

def sort_syllabus_name_reverse_chronologically(arr: list):
  # Define valid seasons and year range
    valid_seasons = ['Fall', 'Winter', 'Summer']
    valid_year_range = range(2000, 2100)
    
    # Regular expression to match the year (2000-2099) and season
    year_season_pattern = re.compile(r'(\b(?:20\d{2})\b)\s*(Fall|Winter|Summer)')
    
    # Filter the list based on the year and season
    filtered_items = []
    for item in arr:
        match = year_season_pattern.search(item)
        if match:
            year, season = int(match.group(1)), match.group(2)
            if year in valid_year_range and season in valid_seasons:
                # Store the item along with the extracted year and season
                filtered_items.append((item, year, season))
    
    # Sort the filtered list by year and season
    sorted_items = sorted(filtered_items, key=lambda x: (x[1], ['Fall', 'Winter', 'Summer'].index(x[2])))
    
    # Get back the original items, after sorting by year and season
    sorted_items = [item[0] for item in sorted_items]

    # Reverse the sorted list
    sorted_items.reverse()
    
    return sorted_items

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

    all_items = s3_client.list_objects_v2(Bucket=get_s3_bucket_name(), Prefix=f"{subject.upper()} {code}")

    if "Contents" not in all_items:
        return matching_syllabus
    
    for item in all_items["Contents"]:
        matching_syllabus.append(item["Key"])
    
    matching_syllabus = sort_syllabus_name_reverse_chronologically(matching_syllabus)

    return matching_syllabus

def get_presigned_url_for_getobject(filename: str, expiry: int):
    s3_client = get_s3_client()
    return s3_client.generate_presigned_url('get_object', Params={'Bucket': get_s3_bucket_name(), 'Key': filename}, ExpiresIn=expiry)