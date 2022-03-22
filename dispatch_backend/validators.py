def validate_message(message, errorModel):
    """ checks that the is_lost is True or if turn_when_received is not None """
    if message.channel is None and message.turn_when_received is not None:
        raise errorModel("You have to choose a channel!")

    if not message.is_lost and message.turn_when_received is None:
        raise errorModel("You cannot approve that! Either put it as lost or add a turn when it is received")
