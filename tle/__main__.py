import argparse
import asyncio
import distutils.util
import logging
import os
import base64
import discord
from logging.handlers import TimedRotatingFileHandler
from os import environ
from pathlib import Path
from json import loads
from os import environ
import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage

STORAGE_BUCKET = 'gs://tle-bot-ec3bb.appspot.com'
bucket = None
if STORAGE_BUCKET!='None':
    cred = credentials.Certificate(loads(base64.b64decode('ewogICJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCIsCiAgInByb2plY3RfaWQiOiAidGxlLWJvdC1lYzNiYiIsCiAgInByaXZhdGVfa2V5X2lkIjogImQyMDgxMjM1Njk4M2EyNDZmNjhlYTQ3YTgwMWUwNzVhNThlMDRkOTAiLAogICJwcml2YXRlX2tleSI6ICItLS0tLUJFR0lOIFBSSVZBVEUgS0VZLS0tLS1cbk1JSUV2Z0lCQURBTkJna3Foa2lHOXcwQkFRRUZBQVNDQktnd2dnU2tBZ0VBQW9JQkFRQ0w1TkNCS25ZYmFzNWNcbnVnczlsTkZDVUxrOEljR1kxeGxsblFkSEFQOVNPSFgzRnBnNS9uS2N5Z0N3TkVhakNFNDk5SE5lK21OUDJnSm9cblFvSXg4NDdCMWxidlNlMm91Y1cyNG05MHFGUlRmaVpjOVBCdGVCczlTNHZxc2plQjdoTUozM3Ywc29ycFgxQUFcbkd3VU5yOSs0UHZ1MHN1dFFIK3VjWEdYODB4dWdZZklLL0Z0R2hPbTZsQ3YrM1RzbkptSjY1NFBZaXBtcXlDS2ZcbkpiZVZBZjRyOUl2eHNBUUNXblovRnorWm5yc1BBZHcxbE42dC94UEtMT1g4bFdsbXJBZS9XRUhmZTdoSEdXQ2Fcbno0NlRZR1g1TjBSNTZXODlHaVdLZXdUc052L24xU0k5ZXhEdEIxSlEraXZUQ2tmUWt3WlhGQTI3M21WckpDUTBcblRFallEZVYzQWdNQkFBRUNnZ0VBTmpMMWNVV3hNcGdqMFpzbTVibjFoUnJmV1dPK3JPZVJhR1A1UU5JckdZRFVcbmUyR2Vvc0ZwU0VPZkZxVjZSSW5nUG5LcUREODRJT1RYRCt2TW8ydTRnSEw1aFlYLzlPSGNyeWwxZ3g0QVpjUzNcbk9rYVBxK25mcTlUTUphYmNpSk5qZnV5K0NxVHQydExabk9EYkNWMTljTlcrRVZsTWYrT09GaXRhUENUU1RFVnpcbm1TTElQSEF4YlJVZi9JODZJUTVpaUdXWFJyUkVLUmpvVjRpd1FUVmJGN2VIczhYMGtla0E5RnZ0S21VN2VhV0tcbkNOQWFLcDhQNXFHMlhXNHQrNHpCTEJTS1UvUWpZS1pESnRuUnBmKzhzSk01MTJTTWtieW1iL2pYOWdYTG56VFlcblhjS0R0R3hKT29NMi9udjhudFpKVzFJZXQybmh5eXZOYzFXVExhZmtPUUtCZ1FERGN3aU1VaGhUTEtvUmVKcEdcbjAxZnRrZ0o2SGVnRzJJRU9BMEduM0doUGdVWUpZSWM0WmRzUi8vdk5naWFkSEFoUk5jKzgzWFQ3VFQra0RHZkJcbjZ4R3JuZFBrUG1kZHc1RDZLa2lpRVdrZWUvelU2bUxVK0o0M212ZWhRSG4vRk5HdEtUK0NwWG1hMllZSld3Z3JcbnZ1S0FBc3BhMm9Ja1d6Vm5Cc1ZSYnlzRjlRS0JnUUMzTzdTWlFSREtQbHdGNFFwZ0o2UUkwY2ptelFvMkFwSTlcblhnYUdYdXdOUDRmWnA2MDJob2hXUWJKeGRBZnBpRXN1d3piY1hEOXJ1SGQ4Y2NWWk9nVXFKUHovR2tFT0llRVFcbjVtdDVpbmkxZzZsZ21qTHpOZmFlalNDUUxPOTlLMTdFWHMxNDc1WGpDTWtrd3JBbzJGektCcDU0Y0JieVBQbHVcbkZ6NjdTVnV1T3dLQmdCS0YzV0tIQ1QwZ3Q0RnVYNWlrd09tSDgrb2syVytFcHo1dnVwSXhCa1c2cDZ1TjFXTFhcbjdGb1pXNERQZTk5WjM4UHFpS1NLakdLZ29JNW9pcERMT1dKOVU2Nkc1Mzd3WU5ZRW1kdWFNTTh0eXZsV3VVVWJcbnhzcllTZTJqVWF5R0NaVVNtcTFFQjNGUWVpNTZ6Unh3TzhFTUFxZDNtK3ZjSlFSOWxNZXg5RzdkQW9HQkFKRmZcbkdpSjRuN1NGRXdkTENxdE01L1JqVkF2ZzR0Z0U1RGN4ME9Wc2k4VGJBWkhxV1I4b1R5UjREUFc4QThjQTdmMFVcbnZnTElZVHk2Wm5uaDNadXp6NE1uUTEyMVc2VzF0VlZ1S2hpTWhzWWp4ZzZ4Wi9qVGVHMUVOSENPWmhjZGdKczFcblI3bEtBOVhURTVwSnArOVA4UllMZUZDL1JVVThvUHY2RHpnUnRGNGZBb0dCQUtxb1Nhby9nOGtJQWZBMkt3OWZcbkZlTmNDTDlqb3p5Tjk0L2VpcENaVnZZWVM3NnFiajM2TXpnSzhySjFZcTJGOE5KdUgwU0dSSFpHN3BGMnlTRHNcbmJVOUNWL2NmM2RCaTZjRHNDYU9hdXhLeEZwR01xRXF0bCtXN0tsTDBKTi8wc2FJVHRuaUwwaWsxVkdPT3h5SkNcbjJ2M3FpT2JaSitydS9vY0Y4WWduUVhaR1xuLS0tLS1FTkQgUFJJVkFURSBLRVktLS0tLVxuIiwKICAiY2xpZW50X2VtYWlsIjogImZpcmViYXNlLWFkbWluc2RrLWsybWFjQHRsZS1ib3QtZWMzYmIuaWFtLmdzZXJ2aWNlYWNjb3VudC5jb20iLAogICJjbGllbnRfaWQiOiAiMTEwMTQ5OTE5MzA3NzE5MjY3OTA2IiwKICAiYXV0aF91cmkiOiAiaHR0cHM6Ly9hY2NvdW50cy5nb29nbGUuY29tL28vb2F1dGgyL2F1dGgiLAogICJ0b2tlbl91cmkiOiAiaHR0cHM6Ly9vYXV0aDIuZ29vZ2xlYXBpcy5jb20vdG9rZW4iLAogICJhdXRoX3Byb3ZpZGVyX3g1MDlfY2VydF91cmwiOiAiaHR0cHM6Ly93d3cuZ29vZ2xlYXBpcy5jb20vb2F1dGgyL3YxL2NlcnRzIiwKICAiY2xpZW50X3g1MDlfY2VydF91cmwiOiAiaHR0cHM6Ly93d3cuZ29vZ2xlYXBpcy5jb20vcm9ib3QvdjEvbWV0YWRhdGEveDUwOS9maXJlYmFzZS1hZG1pbnNkay1rMm1hYyU0MHRsZS1ib3QtZWMzYmIuaWFtLmdzZXJ2aWNlYWNjb3VudC5jb20iCn0=').decode('UTF-8')))
    firebase_admin.initialize_app(cred, {
        'storageBucket': STORAGE_BUCKET
    })
    bucket = storage.bucket()

import seaborn as sns
from discord.ext import commands
from matplotlib import pyplot as plt

import constants
from util import codeforces_common as cf_common
from util import discord_common, font_downloader
from util import clist_api


def setup():
    # Make required directories.
    for path in constants.ALL_DIRS:
        os.makedirs(path, exist_ok=True)
    
    # Update the user.db file from firebase
    if bucket!=None:
        try:
            blob = bucket.blob('tle.db')
            blob.download_to_filename(constants.USER_DB_FILE_PATH)
        except:
            # File is not present in Firebase Storage
            pass

    # logging to console and file on daily interval
    logging.basicConfig(format='{asctime}:{levelname}:{name}:{message}', style='{',
                        datefmt='%d-%m-%Y %H:%M:%S', level=logging.INFO,
                        handlers=[logging.StreamHandler(),
                                  TimedRotatingFileHandler(constants.LOG_FILE_PATH, when='D',
                                                           backupCount=3, utc=True)])

    # matplotlib and seaborn
    plt.rcParams['figure.figsize'] = 7.0, 3.5
    sns.set()
    options = {
        'axes.edgecolor': '#A0A0C5',
        'axes.spines.top': False,
        'axes.spines.right': False,
    }
    sns.set_style('darkgrid', options)

    # Download fonts if necessary
    font_downloader.maybe_download()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--nodb', action='store_true')
    args = parser.parse_args()

    token = "Enter your token here"
    if not token:
        logging.error('Token required')
        return

    allow_self_register = 'True'
    if allow_self_register:
        constants.ALLOW_DUEL_SELF_REGISTER = bool(distutils.util.strtobool(allow_self_register))

    setup()
    
    intents = discord.Intents.all()
    # intents.members = True

    bot = commands.Bot(command_prefix=commands.when_mentioned_or(';'), intents=intents)
    cogs = [file.stem for file in Path('tle', 'cogs').glob('*.py')]
    for extension in cogs:
        bot.load_extension(f'tle.cogs.{extension}')
    logging.info(f'Cogs loaded: {", ".join(bot.cogs)}')

    def no_dm_check(ctx):
        if ctx.guild is None:
            raise commands.NoPrivateMessage('Private messages not permitted.')
        return True
    
    def ban_check(ctx):
        # banned = cf_common.user_db.get_banned_user(ctx.author.id)
        # if banned is None:
        #     return True
        # return False
        return True

    # Restrict bot usage to inside guild channels only.
    bot.add_check(no_dm_check)
    bot.add_check(ban_check)

    # cf_common.initialize needs to run first, so it must be set as the bot's
    # on_ready event handler rather than an on_ready listener.
    @discord_common.on_ready_event_once(bot)
    async def init():
        clist_api.cache()
        await cf_common.initialize(args.nodb)
        asyncio.create_task(discord_common.presence(bot))

    bot.add_listener(discord_common.bot_error_handler, name='on_command_error')
    bot.run(token)


if __name__ == '__main__':
    main()
