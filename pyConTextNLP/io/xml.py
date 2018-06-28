"""
module for creating XML files
"""
import re

rlt = re.compile(r"""<""", re.UNICODE)
ramp = re.compile(r"""&""", re.UNICODE)


def xmlScrub(tmp):
    return rlt.sub(r"&lt;",ramp.sub(r"&amp;",u"{0}".format(tmp)))

