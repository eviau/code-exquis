# See readme.md for instructions on running this code.

import random

from typing import Any, Dict, List

from zulip_bots.lib import BotHandler, use_storage


class CodeExquisHandler:

    def initialize(self, bot_handler: BotHandler) -> None:
        storage = bot_handler.storage
        if not storage.contains("line") or not storage.contains("message_id") or not storage.contains("players") or not storage.contains("code") or not storage.contains("turn") or not storage.contains("start"):
            storage.put("line", "")
            storage.put("message_id", None)
            storage.put("players", [])
            storage.put("code", list())
            storage.put("turn", "")
            storage.put("start", False)
            
            
        self.commands = [
            "help",
            "list-commands",
            "subscribe",
            "unsubscribe",
            "nextline",
            "howto"
        ]

        self.descriptions = [
            "Display bot info",
            "Display the list of available commands",
            "Subscribe to the bot to play in the future",
            "Unsubscribe to the bot. You will stop playing the game.",
            "Enter the next line of code, if it is your turn!",
            "Explains how to play."
        ]

    def usage(self) -> str:
        return """
        This is a gamebot! Play Code Exquis in Zulip with others.
        
        Code Exquis is a game where everyone works together on a piece of code... one line at a time.
        
        To learn how to play, enter `code_exquis howto`.
        
        To see all commands, enter `list-commands`.
        """

    def handle_message(self, message: Dict[str, str], bot_handler: BotHandler) -> None:
        content = message["content"].strip().split()
        sender = message["sender_email"]

        if content == []:
            bot_handler.send_reply(message, "No Command Specified")
            return

        content[0] = content[0].lower()

        if content == ["help"]:
            bot_handler.send_reply(message, self.usage())
            return

        if content == ["list-commands"]:
            response = "**Available Commands:** \n"
            for command, description in zip(self.commands, self.descriptions):
                response += f" - {command} : {description}\n"

            bot_handler.send_reply(message, response)
            return

        response = self.generate_response(content,sender, bot_handler)
        bot_handler.send_reply(message, response)

    def generate_response(self, commands: List[str], sender: str, bot_handler: BotHandler) -> str:
        try:
            instruction = commands[0]

            if instruction == "subscribe":
                return self.subscribe(sender, bot_handler)

            if instruction == "unsubscribe":
                return self.unsubscribe(sender, bot_handler)
                
            if instruction == "nextline":
                return self.nextline(sender, bot_handler, commands)

            if instruction == "howto":
                return self.howto()
                
        except KeyError:
            return "Please try again ?"

        return "Invalid Command."

    def howto(self):
        return """
               The goal of Code Exquis is to write a short, fun program together.
               
               To play, subscribe by sending `subscribe` to the code_exquis bot.
               
               Next player is picked at random among the list of current players.
               When it's your turn, enter a line of code with `nextline`:
                    `nextline "a=5*x"`
               
               The game ends when the current player send `nextline "return 0"`.
               
               Send `unsuscribe` to unsuscribe.
               """
                

    def subscribe(self, sender: str, bot_handler: BotHandler) -> str:
        storage = bot_handler.storage
        players = storage.get("players")
        current_status = storage.get("start")
        
        if not ( sender in players ) :
            players.append(sender)
            storage.put("players", players)
            
        # start a game if there are at least two players
        if len(players) > 2 and not current_status:
            pick = self.pick_next_player(bot_handler,sender)
            
            bot_handler.send_message(dict(
                type="private",
                to='followup',
                subject=pick,
                content="It's your turn to play Code Exquis! Enter `nextline` followed by a line of code to play."
            ))
            
            storage.put("start", True)
        
        return "You have been subscribed!"

    def unsubscribe (self, sender: str, bot_handler: BotHandler) -> str:
        storage = bot_handler.storage
        players = storage.get("players")
        
        if sender in players:
            players.remove(sender)
            storage.put("players", players)
            
        if len(players) <2:
            storage.put("start", False)

        return "Sorry to see you go."

    def nextline (self, sender: str, bot_handler: BotHandler, commands: List[str]) -> str:
        storage = bot_handler.storage
        
        # check if it is your turn
        whose_turn_is_it_anyway = storage.get("turn")
        
        if sender == whose_turn_is_it_anyway:
            # if it is you turn, accept the answer 
            code = storage.get("code")
            storage.put("line", commands[1]) 
            code.append(commands[1])
            storage.put("code", code)

            if code == "return 0":
                # the game has ended
                bot_handler.send_message(dict(
                type="private",
                to='followup',
                subject=pick,
                content="A new game is starting! Enter `nextline` followed by a line of code to play."
            ))
                
                bot_handler.send_message(dict(
                type="private",
                to='followup',
                subject=sender,
                content="You have ended the game. Here is the final code:" + str(code)
            ))

            # pick next person to write a line of code
            pick = pick_next_player(bot_handler,sender)
        
            # send them the current line of code
            
            bot_handler.send_message(dict(
                type="private",
                to='followup',
                subject=pick,
                content="It's your turn to play Code Exquis! Enter `nextline` followed by a line of code to play. Here is the last line of code received:" + str(commands[1])
            ))

            # tell the current player their turn is done !
            return ("Thank you for playing! we have received" + str(code))

        return "It's not your turn!"

    def pick_next_player(self, bot_handler: BotHandler, sender: str) -> str:
        storage = bot_handler.storage     
        players = storage.get("players")
            
        pick = random.choice(players)
            
        if len(players) > 1 :
            while pick == sender:
                pick = random.choice(players)
            
        storage.put("turn", pick)       
        
        return pick
        
handler_class = CodeExquisHandler
