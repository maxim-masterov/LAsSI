def print_msg_with_header(msg_header, msg):
    """
    Print a message with a header to terminal
    :param msg_header: Header of the message
    :param msg: Message body
    :return: None
    """
    print(msg_header, end=' ')
    print(msg)


def print_info(msg, indentation='    '):
    """
    Print a regular message to terminal
    :param msg: Message body
    :param indentation: Message indentation
    :return: None
    """
    print(indentation + msg)


def print_dbg_info(msg):
    """
    Print a debug message to terminal
    :param msg: Message body
    :return: None
    """
    msg_header = "== DEBUG =="
    if __debug__:
        print_msg_with_header(msg_header, msg)


def print_err_info(msg):
    """
    Print an error message to terminal
    :param msg: Message body
    :return: None
    """
    msg_header = "== ERROR =="
    print_msg_with_header(msg_header, msg)