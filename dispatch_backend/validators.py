def validate_message(message, errorModel):
    if message.channel is None and message.approved:
        raise errorModel("You have to choose a channel!")

    if not message.is_lost and message.turn_when_received is None and message.approved:
        raise errorModel("You cannot approve that! Either put it as lost or add a turn when it is received")

    if message.turn_when_received and message.turn_when_received<=message.game.turn and message.approved:
        raise errorModel("You cannot send a message to the past or for this turn, you can only send for next turn or after!")

def validate_game(game, errorModel):
    games = type(game).objects.filter(name=game.name, has_ended=False).exclude(id=game.id)
    if len(games)>0:
        raise errorModel("This name already exists, please choose another one!")

def validate_category(category, errorModel):
    categories = type(category).objects.filter(number=category.number, game__has_ended=False).exclude(id=category.id)
    if len(categories)>0:
        raise errorModel("This category is already used in a current game, please choose another one!")