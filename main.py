import os
import json
import calendar
import discord

from datetime import datetime
from zoneinfo import ZoneInfo

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0"))

TZ = ZoneInfo("Europe/Warsaw")

intents = discord.Intents.none()
intents.guilds = True

client = discord.Client(intents=intents)


def load_events():
    try:
        with open("events.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except:
        return []


def make_calendar():
    now = datetime.now(TZ)

    cal = calendar.monthcalendar(now.year, now.month)

    lines = [
        "```",
        "PN  WT  ŚR  CZ  PT  SB  ND"
    ]

    events = load_events()

    event_days = {
        int(e["date"].split("-")[2])
        for e in events
        if e["date"].startswith(now.strftime("%Y-%m"))
    }

    for week in cal:
        row = []

        for day in week:
            if day == 0:
                row.append("  ")
            elif day in event_days:
                row.append(f"{day:02d}*")
            else:
                row.append(f"{day:02d} ")

        lines.append(" ".join(row))

    lines.append("```")

    return "\n".join(lines)


def make_embed():
    now = datetime.now(TZ)

    embed = discord.Embed(
        title="🏁 SRS CALENDAR",
        description=(
            f"📅 **{now.strftime('%m/%Y')}**\n\n"
            f"{make_calendar()}\n\n"
            "🔴 Wyścig  🟢 Trening  🔵 LIVE"
        ),
        color=0xD71920
    )

    events = sorted(load_events(), key=lambda e: e["date"])

    upcoming = [
        e for e in events
        if e["date"] >= now.strftime("%Y-%m-%d")
    ][:8]

    if upcoming:
        text = ""

        for event in upcoming:
            text += (
                f"\n**{event['emoji']} {event['name']}**\n"
                f"📅 {event['date']} | 🕒 {event['time']}\n"
                f"🏁 {event.get('track', 'Do ustalenia')}\n"
            )

        embed.add_field(
            name="🏎️ NADCHODZĄCE WYDARZENIA",
            value=text,
            inline=False
        )
    else:
        embed.add_field(
            name="📅 NADCHODZĄCE WYDARZENIA",
            value="Brak zaplanowanych wydarzeń.",
            inline=False
        )

    embed.set_footer(
        text="SRS • Sim Racing Squad | Automatyczny kalendarz"
    )

    return embed


@client.event
async def on_ready():
    print("SRS CALENDAR BOT uruchomiony!")

    channel = await client.fetch_channel(CHANNEL_ID)

    message = None

    async for msg in channel.history(limit=100):
        if (
            msg.author.id == client.user.id
            and msg.embeds
            and msg.embeds[0].title == "🏁 SRS CALENDAR"
        ):
            message = msg
            break

    embed = make_embed()

    if message:
        await message.edit(embed=embed)
        print("Kalendarz zaktualizowany!")
    else:
        await channel.send(embed=embed)
        print("Utworzono nowy kalendarz!")

    await client.close()


if not TOKEN or not CHANNEL_ID:
    raise RuntimeError("Brakuje DISCORD_TOKEN lub CHANNEL_ID")

client.run(TOKEN)
