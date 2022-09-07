# Bot constructor
Application for constructing Telegrams`s bots using .yml files 
## How to use
### Build
- To start using bot you should make some preparatory work
At first you shuld set up ```.env``` file.
```
BOT_TOKEN=YOR_BOT_TOKEN
DATABASE=PATH_TO_DATABASE_FILE
```
- Then you can build docker images using

```sh
docker build -t dialog-bot . 
```
OR
```sh
docker compose up --build
```

# Yml documentation
### Main concept of bot is programming bots whithout programming skils. Example of yml configuartion in ```dialog.yml```

- All messages divided by blocks in dialog list 
``` yml
dialogs:
    hello:           <---- first message block
        message: "Hello world"
        next: bye
        ...
 ```
 - Dialog vectors sets using option of message block  - here next block is ```bye```
 ```yml
next: bye
 ```


 - Message that bot will reply is defined in ```message``` argument 
 ```yml
next: bye
 ```
 - If you whant to attach image to reply message you should use block ```attachment``` - argument is path to file on disk
 ```yml
attachment: img/cat.img
 ```
 - To send keyboard to user use ```buttons```
 block. User by pressing one of button will jump to block that whote in ```next ``` block. **Keyborad will disapper after answer.**
 ```yml
 buttons:
      - text: "Yes"
        next: capitan
      - text: "No"
        next: user
 ```
 - To save user`s answer on block user defenition ```write``` it will save in database file - argument in name of virable where to store answer
 ```yml
capitan:
    message: "Enter your team name"
    write: entity
    next: default_user
 ```
- Lets imaginate situation:
You whant for user check data that his
inputs. No problems: use tag ```format```. When ypu are using this tag you should use ```{}``` in message. Braces will replace positionally that you indicated in ```format``` tag

 ```yml
ending:
    message: "your name is {}, entity {}, group {} "
    format:
      - name
      - entity
      - group
 ```
