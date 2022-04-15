def validate_message(message, errorModel):
    if message.channel is None and message.turn_when_received is not None:
        raise errorModel("You have to choose a channel!")

    if not message.is_lost and message.turn_when_received is None and message.approved:
        raise errorModel("You cannot approve that! Either put it as lost or add a turn when it is received")

    if message.turn_when_received and message.turn_when_received<=message.game.turn:
        raise errorModel("You cannot send a message to the past or for this turn, you can only send for next turn or after!")

def validate_game(game, errorModel):
    games = type(game).objects.filter(name=game.name, has_ended=False)
    if len(games)>0:
        raise errorModel("This name already exists, please choose another one!")