<div>
<p align="center"><a href="https://github.com/Zseni051/Outages">
  <img src="https://raw.githubusercontent.com/Zseni051/Outages/main/Warning.png" align="center" alt="Counter.ico" style="width:256px;height:256px;"></a></p>
<p align="center">
    <a href="https://www.youtube.com/channel/UCsIaU94p647veKr7sy12wmA">
        <img src="https://img.shields.io/badge/YouTube-FF0000?style=for-the-badge&logo=youtube&logoColor=white" alt="Youtube"></a>
    <a href="https://dsc.gg/zseni">
        <img src="https://img.shields.io/badge/Discord-7289DA?style=for-the-badge&logo=discord&logoColor=white" alt="Discord"></a> 
    <a href="https://twitter.com/zseni10">
        <img src="https://img.shields.io/badge/Twitter-55ADEE?style=for-the-badge&logo=Twitter&logoColor=white" alt="Twitter"></a> 
</div>

## Features
Monitors multiple bots/users status, and notifies when its up or down.
<br>Note: Designed to only function in 1 guild

### Online message
<img src="https://i.imgur.com/1U3fceR.png">

### Offline message
<img src="https://i.imgur.com/yQjAt4P.png">

### Custom notification message
- Bot will send a message then delete it, include who to ping here.
<img src="https://i.imgur.com/aQ0Pkpf.png">

### Per bot specific channel
<img src="https://i.imgur.com/N7eYrkr.png">

### Add bot to be monitored
<img src="https://i.imgur.com/oaVlXru.png">

### Remove bot from being monitored
<img src="https://i.imgur.com/5NwpFSG.png">

### View bot's system statisics
<img src="https://i.imgur.com/jSjYqXA.png">

## Setup
1. Create a mongodb database named ["Outages"]["Users"]
2. Create bot with all intents enabled
3. Invite the bot with all permisions
3. Fill out bots Secrets
4. In main.py change these variables: 
```python
debug_guilds = [your guild id]
self.owner_id = your id
```

# 

Note: You will need to make slight changes depending where you host it.
<br>I have it set up to run either on my desktop or on replit.

BTW You can view the bot in action in my discord
