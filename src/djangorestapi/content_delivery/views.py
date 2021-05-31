# all imports are local

# ---------------------COORDINATOR---------------------------------

from content_delivery.view.coordinator import Coordinator_View as cView

# ------------------------SUBJECT------------------------------

from content_delivery.view.subject import Subject_View as sView

# -----------------------FORUM-------------------------------

from content_delivery.view.forum import Forum_View as fView

# -----------------------REPLY-------------------------------

from content_delivery.view.reply_1 import Reply_1_View as r1View
from content_delivery.view.reply_2 import Reply_2_View as r2View

# -----------------------LECTURE-------------------------------

from content_delivery.view.lecture import Lecture_View as lView

# -----------------------ASSIGNMENT-------------------------------

from content_delivery.view.assignment_normal import Assignment_View as a11View
from content_delivery.view.assignment_normal_mark import Assignment_Mark_View as a12View

from content_delivery.view.assignment_mcq import Assignment_View as a21View
from content_delivery.view.assignment_mcq_mark import Assignment_Mark_View as a22View

# -----------------------POST-------------------------------

from content_delivery.view.post import Post_View as pView
from content_delivery.view.votes import Votes_View as vView

# ----------------------------------------------
