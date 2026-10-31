from .dashboard import ManagerDashboardView, ManagerEditAccountView
from .users import (
    StudentListView,
    StudentCreateView,
    StudentUpdateView,
    StudentToggleActiveView,
    StudentExcelTemplateDownloadView,
    StudentBulkImportView,
    TeacherListView,
    TeacherCreateView,
    TeacherUpdateView,
    TeacherPermissionsUpdateView,
    TeacherToggleActiveView,
    AdviserListView,
    AdviserCreateView,
    AdviserUpdateView,
    AdviserPermissionsUpdateView,
    AdviserToggleActiveView,
)
from .school import SchoolInfoUpdateView
from .classes import (
    ClassListView,
    ClassCreateView,
    ClassUpdateView,
    ClassToggleActiveView,
    SectionManageView,
    SectionToggleActiveView,
    SectionContentToggleActiveView,
)
from .exams import (
    ExamListView,
    ExamCreateView,
    ExamUpdateView,
    ExamStatusActionView,
    ExamAnalyticalDetailView,
    PracticeListView,
    PracticeCreateView,
    PracticeUpdateView,
    PracticeToggleActiveView,
)
from .live_classes import (
    LiveClassListView,
    LiveClassCreateView,
    LiveClassUpdateView,
    LiveClassToggleActiveView,
    AdviserLiveSessionCreateView,
    StreamServerMonitorView,
    LiveRequestReviewView,
)
from .tickets import (
    TicketListView,
    TicketDetailView,
    TicketToggleActiveView,
)
from .reports import (
    ManagerExamReportView,
    ManagerTeacherReportView,
    ManagerAdviserReportView,
    ManagerStudentReportView,
    ManagerStudentReportCardView,
)
from .settings import (
    SchoolSettingsUpdateView,
    SchoolAnnouncementToggleActiveView,
)
from .articles import (
    ManagerArticleListView,
    ManagerArticleCreateView,
    ManagerArticleUpdateView,
    ManagerArticleToggleActiveView,
)
