# Hello baidbot!
<img src="https://github.com/Git-baid/Microwave-PC-LCD/blob/main/baidbot800x.png" width="320">
A multi-functional bot for Discord that provides utility to myself and a couple of Discord servers

## 🤖 Features:
- **Manipulate data on a specific user's favorite everything using CRUD operations**
![](https://raw.githubusercontent.com/CVScholtisek/baidbotDiscord/master/findfavDemonstration.gif)
- **Modify input images/gifs to add text or a preset speechbubble as a reaction image**
![](https://raw.githubusercontent.com/CVScholtisek/baidbotDiscord/master/memeDemonstration.gif)
- **Display an image on baid's [Microwave PC Display](https://github.com/Git-baid/Microwave-PC-LCD/tree/main)**
<img src="https://github.com/Git-baid/Microwave-PC-LCD/blob/main/20230725_235057.jpg" width="300">

- **Miscellaneous features such as an insurance timer for Tarkov, return bot ping, and /help**


# Command Help:
## **Folden favorites:**
Folden's favorites data is synchronized between all servers the bot is in. Any entry from one server can be read or modified from any other server.

**/findfav**

- *Find folden's favorite everything*

**/addfav**

- *Add a new category to favorites*
- Adds a new empty favorites category to query Foldenpaper with. Only Foldenpaper may change the value of this category with /updatefav, however, anyone may add a category.

**/updatefav**

- *Update a category's favorite item*
- Can only be executed by Foldenpaper to update his favorite item

**/deletefav** 

- *Delete a favorite category*
- Can only be executed by Foldenpaper to delete an item from data

**/findemptyfavs**

- *List all favorites categories which are empty*
- Returns a list of all favorites categories which are marked as "None". Foldenpaper will need to use /updatefav to populate these entries.

## **Meme:**

**/meme** 

- *Add top text and/or bottom text to an image*
- Text size scales with image width, long strings will be split into multiple lines

**/gifmeme** 

- *Add text above a gif in a margin in the classic meme gif style*
- Long captions will be split into multiple lines and scale the margin procedurally

**/speechbubble** 

- *Add a speech bubble to the top of your image for meme responses*

## **Misc:**

**/insurance** 

- *Used for Tarkov players to get notified when their insurance is ready to claim (from Prapor)*
- Users will get notified by DM, will only work if you allow DMs from non-friends!

**/ping** 

- *Returns bot latency*

**/help** 

- *List command help*

**/Display_Image**

- Displays an image on baid's Microwave PC display. Does not require baid's PC to be on.

~~**/toggleled**~~ *Removed*

~~- *Toggles IRL desklamp on baid's desk (only while pc is running)*~~
