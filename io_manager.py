def print_msg_with_header(msg_header, msg1, msg2=''):
    """
    Print a message with a header to terminal
    :param msg_header: Header of the message
    :param msg1: Message body #1
    :param msg2: Message body #2
    :return: None
    """
    print(msg_header, end=' ')
    print(msg1, msg2)


def print_prefix(msg, indentation='    '):
    """
    Print a prefix message to terminal
    :param msg: Message body
    :param indentation: Message indentation
    :return: None
    """
    print(indentation + msg, end = ' ')


def print_info(msg, indentation='    '):
    """
    Print a regular message to terminal
    :param msg: Message body
    :param indentation: Message indentation
    :return: None
    """
    print(indentation + '\t' + msg)


def print_dbg_info(msg1, msg2=''):
    """
    Print a debug message to terminal
    :param msg1: Message body #1
    :param msg2: Message body #2
    :return: None
    """
    msg_header = "== DEBUG =="
    if __debug__:
        print_msg_with_header(msg_header, msg1, msg2)


def print_err_info(msg1, msg2=''):
    """
    Print an error message to terminal
    :param msg1: Message body #1
    :param msg2: Message body #2
    :return: None
    """
    msg_header = "== ERROR =="
    print_msg_with_header(msg_header, msg1, msg2)