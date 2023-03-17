# Hello baidbot
A bot for Discord that provides specific utility to a select few servers

## 🤖 Features:
- **Manipulate data on a specific user's favorite everything using CRUD operations**
- **Modify input images/gifs to add text or a preset speechbubble as a reaction image**
  - ![](https://raw.githubusercontent.com/CVScholtisek/baidbotDiscord/master/memeDemonstration.gif)
- **Miscellaneous features such as an insurance timer for Tarkov, return bot ping, and /help**

# Command Help:
## **Folden favorites:**

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

- *List all favorites categories which are empty *
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
