import discord
import mysql.connector
from discord.ext import commands
import os
import math

from constants import ALLOWLISTED_SERVER_IDS
from constants import SUBJECT_ID_TRANSLATOR
from constants import SCHOOL_ID_REVERSE_TRANSLATOR
from constants import DALHOUSIE_SUBJECT_LISTS

class Course_Commands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    course = discord.SlashCommandGroup(
        name="course", 
        description="Course related commands",
        guild_ids=ALLOWLISTED_SERVER_IDS
    )

    async def get_subjects(ctx):
        return [subject for subject in DALHOUSIE_SUBJECT_LISTS if subject.startswith(ctx.value.upper())]

    @course.command(
        name="basic_info",
        description="Gets basic information about courses"
    )
    async def basic_info(
        self, ctx, 
        subject: discord.Option(str, "Subject code, ex. CSCI", autocomplete=get_subjects), 
        code: discord.Option(int, "Course code, ex. 2134")
    ):
        # Code must be an int that is 4 digits long
        if 4 != int(math.log10(code))+1:
            await ctx.respond("**Error**: The course code digit must be 4.", ephemeral=True)
            return
        
        try:
            cnx = mysql.connector.connect(
                user=os.getenv("MYSQL_DB_USERNAME"),
                password=os.getenv("MYSQL_DB_PASSWORD"),
                database=os.getenv("MYSQL_DB_SCHEMA_NAME"),
                host=os.getenv("MYSQL_DB_HOSTNAME")
            )
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
                
            subquery_cursor = cnx.cursor()
            subquery_find_subject_name = f"SELECT Subject_Name FROM `Subject` WHERE Subject_Id = \"{subject_id}\""
            subquery_cursor.execute(subquery_find_subject_name)

            embed=discord.Embed(title=f"{subject.upper()} {course_code}", url=f"{course_schoolurl}", description=f"{course_name}", color=0xfbf182)
            embed.add_field(name="Subject", value=f"{subquery_cursor.fetchone()[0]}", inline=True)
            embed.add_field(name="School", value=f"{SCHOOL_ID_REVERSE_TRANSLATOR.get(school_id)}", inline=True)
            embed.add_field(name="Description", value=f"{course_description}", inline=False)
            embed.add_field(name="Latest Syllabus Link", value=f"Currently being built! Until then, please check the pins in #{subject.lower()}{code} channel to grab the latest available syllabus.", inline=False)
            embed.set_footer(text="Made by @soondae 🦆🦆🦆")
            
            subquery_cursor.close()
            cursor.close()
            cnx.close()
            
            await ctx.respond(embed=embed)
        except:
            if cursor:
                cursor.close()

            if cnx:
                cnx.close()

            await ctx.respond("**Error**: Internal Service Exception. Please try again later or reach out to @soondae!", ephemeral=True)


def setup(bot):
    bot.add_cog(Course_Commands(bot))

def clean_html_frags(s: str):
    return s.replace("&amp;", "&")
    