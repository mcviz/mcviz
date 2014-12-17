"""Help utils"""
from mcviz.logger import LOG
LOG = LOG.getChild(__name__)

def did_you_mean(topic, available):
    """Report the closest match"""
    from difflib import get_close_matches
    close = get_close_matches(topic, available)

    if close:
        bits = ", ".join(sorted(close))
        left, lastcomma, right = bits.rpartition(", ")
        if lastcomma:
            bits = "{0} or {1}".format(left, right)
        LOG.error("Did you mean {0}?".format(bits))

        if len(close) == 1:
            return close[0]
