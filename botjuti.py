import discord
from discord.ext import commands
from myserver import server_on
import requests

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

servers = {
    'Starcommunity 1': '103.91.190.189',
    'Starcommunity 2': '103.91.190.68',
    'Starcommunity 3': '103.208.27.132',
    'Starcommunity 4': '103.91.190.230',
    'Starcommunity 5': '103.208.27.17',
    'Starcommunity 6': '103.208.27.176',
    'Starcommunity 7': '103.91.190.164',
    'Starcommunity 8': '103.91.190.171',
    'Starcommunity 9': '103.91.190.103',
    'Starcommunity 10': '103.91.190.233',
    'MAFIA CITY': '103.216.159.124',
    'STREER BOXING': '151.101.40.193'

}

PORT = '30120'

async def check_player(channel, server_ip: str, player_id: str):
    try:
        info_url = f'http://{server_ip}:{PORT}/info.json'
        info_response = requests.get(info_url)

        server_name = "ไม่พบชื่อเซิร์ฟเวอร์"
        if info_response.status_code == 200:
            server_info = info_response.json()
            server_name = server_info.get('vars', {}).get('sv_projectName', 'ไม่พบชื่อเซิร์ฟเวอร์')

        url = f'http://{server_ip}:{PORT}/players.json'
        response = requests.get(url)

        if response.status_code == 200:
            players = response.json()
            player_data = next((player for player in players if str(player['id']) == player_id), None)

            if player_data:
                player_name = player_data.get('name', 'ไม่พบชื่อผู้เล่น')
                discord_id = next((identifier.split(":")[1] for identifier in player_data['identifiers'] if identifier.startswith('discord')), None)
                steam_hex = next((identifier for identifier in player_data['identifiers'] if 'steam' in identifier), 'ไม่พบ Steam Hex')
                ping = player_data.get('ping', 'ไม่พบ Ping')
                online_count = len(players)

                # สร้างลิงก์ Steam Profile
                if steam_hex != 'ไม่พบ Steam Hex' and steam_hex.startswith('steam:'):
                    steam_id64 = int(steam_hex.split(':')[1], 16)
                    steam_link = f"https://steamcommunity.com/profiles/{steam_id64}"
                else:
                    steam_link = "ไม่พบลิงก์ Steam โปรไฟล์"

                if discord_id:
                    discord_user = await bot.fetch_user(discord_id)
                    discord_username = discord_user.name
                    discord_mention = discord_user.mention
                    discord_avatar = discord_user.avatar.url if discord_user.avatar else None

                    embed = discord.Embed(
                        title=f"📊 ข้อมูลเซิร์ฟเวอร์\n {server_name}",
                        description=f"**จำนวนผู้เล่นออนไลน์:** {online_count}\n\n\n",
                        color=discord.Color.blurple()
                    )

                    player_info = (
                        f"**🗒️ ข้อมูลผู้เล่น 🗒️**\n\n"
                        f"**⛳️ ชื่อผู้เล่น**\n {player_name}\n\n"
                        f"**🪪 ID**\n {player_id}\n\n"
                        f"**🏓 Ping**\n {ping} ms\n\n"
                        f"**👤 ชื่อผู้ใช้ Discord**\n {discord_username}\n\n"
                        f"**🔗 Discord Mention**\n {discord_mention}\n\n"
                        f"**🎮 Steam Hex**\n {steam_hex}\n\n"
                        f"**🌐 Steam Profile**\n [คลิกที่นี่]({steam_link})" if steam_hex != 'ไม่พบ Steam Hex' else steam_link
                    ) 

                    embed.add_field(name="", value=player_info, inline=False)

                    if discord_avatar:
                        embed.set_thumbnail(url=discord_avatar)

                    gif_url = "https://media.discordapp.net/attachments/1260172651578658907/1308675428050931712/Blue_and_Pink_Neon_Thanks_for_Watching_Video_1.gif?ex=673ece78&is=673d7cf8&hm=0106613feb031c0507cfefef34fa8553f907e661a4b12bbf3f55510bd9aa92b1&=&width=550&height=309"
                    embed.set_image(url=gif_url)

                    embed.set_footer(text=f"ค้นหาข้อมูลโดย {channel.guild.name}", icon_url=channel.guild.icon.url)
                    embed.set_author(name="FiveM Player Checker", icon_url="https://pluspng.com/logo-img/fi13fiv6efe-fivem-logo-fivem-icon-in-color-style.png")

                    view = discord.ui.View()
                    button = discord.ui.Button(label="ปิดข้อความ", style=discord.ButtonStyle.danger)

                    async def button_callback(interaction):
                        await interaction.message.delete()
                        await interaction.response.send_message("ข้อความถูกปิดแล้ว!", ephemeral=True)

                    button.callback = button_callback
                    view.add_item(button)

                    await channel.send(embed=embed, view=view)
                else:
                    await channel.send(f"ไม่พบ Discord ID สำหรับผู้เล่นนี้")
            else:
                await channel.send(f"ไม่พบข้อมูลสำหรับ Player ID: {player_id}")
        else:
            await channel.send(f"ไม่สามารถดึงข้อมูลได้จากเซิร์ฟเวอร์. Status code: {response.status_code}")
    except Exception as e:
        await channel.send(f"เกิดข้อผิดพลาด: {str(e)}")

@bot.command(name='c')
async def check(ctx, player_id: str):
    if not player_id.isdigit():
        await ctx.send("กรุณากรอก Player ID ที่ถูกต้อง (หมายเลข)")
        return

    embed = discord.Embed(
        title="กรุณาเลือกเซิร์ฟเวอร์",
        description="เลือกเซิร์ฟเวอร์ที่คุณต้องการเช็คจากตัวเลือกด้านล่าง",
        color=discord.Color.blue()
    )
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1044685359998574705/1297178095840923698/3FE1D2DC-16D2-4A6F-9771-D9990143A5E9.gif?ex=6714fabe&is=6713a93e&hm=d4204b1f653a54540f8e6cf5d23b96baebdec78ca782190cdb017280f2add491&")
    embed.set_footer(text=f"ค้นหาข้อมูลโดย {ctx.guild.name}", icon_url=ctx.guild.icon.url)

    options = [
        discord.SelectOption(label=server_name, value=server_ip)
        for server_name, server_ip in servers.items()
    ]
    
    select = discord.ui.Select(placeholder="เลือกเซิร์ฟเวอร์ที่ต้องการ", min_values=1, max_values=1, options=options)
    
    async def select_callback(interaction: discord.Interaction):
        server_ip = select.values[0]
        await check_player(ctx.channel, server_ip, player_id)
        
        await interaction.message.delete()

    select.callback = select_callback

    view = discord.ui.View()
    view.add_item(select)

    await ctx.send(embed=embed, view=view)
    await ctx.message.delete()

@bot.command(name='list')
async def list_players(ctx):
    embed = discord.Embed(
        title="กรุณาเลือกเซิร์ฟเวอร์",
        description="เลือกเซิร์ฟเวอร์ที่คุณต้องการเพื่อดูข้อมูลผู้เล่น",
        color=discord.Color.blurple()
    )

    options = [
        discord.SelectOption(label=server_name, value=server_ip)
        for server_name, server_ip in servers.items()
    ]

    select = discord.ui.Select(placeholder="เลือกเซิร์ฟเวอร์ที่ต้องการ", min_values=1, max_values=1, options=options)

    async def select_callback(interaction: discord.Interaction):
        server_ip = select.values[0]

        searching_embed = discord.Embed(
            title="กำลังค้นหา...",
            description="โปรดรอสักครู่ ข้อมูลกำลังถูกดึงจากเซิร์ฟเวอร์",
            color=discord.Color.orange()
        )
        message = await ctx.send(embed=searching_embed)

        await send_player_list(ctx.author, server_ip, ctx)

        await message.delete()
        await interaction.message.delete()

    select.callback = select_callback

    view = discord.ui.View()
    view.add_item(select)

    await ctx.send(embed=embed, view=view)
    await ctx.message.delete()

async def send_player_list(user, server_ip, ctx):
    url = f'http://{server_ip}:{PORT}/players.json'
    info_url = f'http://{server_ip}:{PORT}/info.json'
    
    try:
        info_response = requests.get(info_url)
        server_name = "ไม่พบชื่อเซิร์ฟเวอร์"
        if info_response.status_code == 200:
            server_info = info_response.json()
            server_name = server_info.get('vars', {}).get('sv_projectName', 'ไม่พบชื่อเซิร์ฟเวอร์')

        response = requests.get(url)
        if response.status_code == 200:
            players = response.json()
            sorted_players = sorted(players, key=lambda x: x['name'])

            player_list = ""
            online_count = len(players)
            for player in sorted_players:
                player_list += f"**ID:** {player['id']}\n**Name:** {player['name']}\n\n"

            if player_list:
                max_length = 2048
                await user.send(f"ค้นหาเสร็จสิ้น! ข้อมูลผู้เล่นจากเซิร์ฟเวอร์ **{server_name}** จำนวนผู้เล่นออนไลน์: **{online_count}** กำลังถูกส่ง...")

                for i in range(0, len(player_list), max_length):
                    embed = discord.Embed(
                        title=f"ข้อมูลผู้เล่นจากเซิร์ฟเวอร์ {server_name}",
                        description=player_list[i:i + max_length],
                        color=discord.Color.green()
                    )
                    await user.send(embed=embed)

                response_embed = discord.Embed(
                    title="ข้อมูลผู้เล่น",
                    description="ข้อมูลผู้เล่นได้ถูกส่งไปยัง DM ของคุณแล้ว!",
                    color=discord.Color.green()
                )
                await ctx.send(embed=response_embed)

                view = discord.ui.View()
                button = discord.ui.Button(label="ลบประวัติแชท", style=discord.ButtonStyle.danger)

                async def button_callback(interaction):
                    async for message in user.dm_channel.history(limit=100):
                        if message.author == bot.user:
                            await message.delete()
                    await interaction.response.send_message("ประวัติแชทถูกลบแล้ว!", ephemeral=True)

                button.callback = button_callback
                view.add_item(button)

                await user.send(view=view)
            else:
                await user.send("ไม่พบผู้เล่นในเซิร์ฟเวอร์นี้")
                await ctx.send("ไม่พบผู้เล่นในเซิร์ฟเวอร์นี้")
        else:
            await user.send(f"ไม่สามารถดึงข้อมูลได้จากเซิร์ฟเวอร์. Status code: {response.status_code}")
            await ctx.send(f"ไม่สามารถดึงข้อมูลได้จากเซิร์ฟเวอร์. Status code: {response.status_code}")
    except Exception as e:
        await user.send(f"เกิดข้อผิดพลาด: {str(e)}")
        await ctx.send(f"เกิดข้อผิดพลาด: {str(e)}")

@bot.command(name='cs')
async def check_by_ip(ctx, server_ip: str, player_id: str):
    if not player_id.isdigit():
        await ctx.send("กรุณากรอก Player ID ที่ถูกต้อง (หมายเลข)")
        return

    await check_player(ctx.channel, server_ip, player_id)
    await ctx.message.delete()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} (ID: {bot.user.id})')

server_on

bot.run('MTMwODY2NTYwMTY4OTkxNTQ1Mw.GSXm1S.Xi3ZosDNe06Rw-9vwfbvbqmrDt93n-EMEPRZeE')