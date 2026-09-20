# School Online Platform — Database Schema

## مقدمه | Introduction

این سند ساختار اولیه مدل‌های دیتابیس برای یک پلتفرم مدرسه آنلاین و سیستم مدیریت یادگیری (LMS) را تعریف می‌کند.

This document defines the initial database model structure for an online school and Learning Management System (LMS).

هدف اصلی این معماری، ایجاد یک سیستم **ماژولار، قابل توسعه، قابل نگهداری و مبتنی بر Django SSR** است.

The main goal of this architecture is to create a **modular, scalable, maintainable, and Django SSR-based system**.

---

# 1. Accounts — حساب‌های کاربری و دسترسی

مسئول مدیریت هویت کاربران، نقش‌ها و مجوزهای سیستم.

Responsible for user identity, roles, and system permissions.

```text
accounts/
├── User
├── Role
└── Permission
```

### User

**فارسی:**
مدل اصلی کاربران سیستم است. تمام کاربران، از جمله مدیر، معلم، دانش‌آموز، والد و سایر کاربران از این مدل ایجاد می‌شوند.

**English:**
The main user model of the system. All users, including administrators, teachers, students, parents, and other staff members, are based on this model.

نمونه نقش‌ها:

```text
Administrator
Teacher
Student
Parent
Content Manager
Support
```

---

### Role

**فارسی:**
نقش یک کاربر را در سیستم مشخص می‌کند.

**English:**
Defines the role of a user within the system.

Examples:

```text
School Admin
Teacher
Student
Parent
Content Manager
Support
```

---

### Permission

**فارسی:**
مجوز انجام یک عملیات مشخص در سیستم.

**English:**
Defines a specific permission or action that a user is allowed to perform.

Examples:

```text
course.create
course.update
course.delete

exam.create
exam.publish
exam.correct

student.view
student.update
```

---

# 2. Schools — مدرسه و ساختار آموزشی

مسئول ساختار مدرسه، سال تحصیلی، ترم، پایه و کلاس‌ها.

Responsible for schools, academic years, terms, grades, and classrooms.

```text
schools/
├── School
├── AcademicYear
├── Term
├── Grade
└── Classroom
```

### School

**فارسی:**
اطلاعات اصلی مدرسه یا آموزشگاه را نگهداری می‌کند.

**English:**
Stores the main information about a school or educational organization.

Examples:

```text
Name
Logo
Address
Phone
Description
```

---

### AcademicYear

**فارسی:**
سال تحصیلی که کلاس‌ها، ثبت‌نام‌ها، نمرات و فعالیت‌های آموزشی به آن وابسته هستند.

**English:**
Represents an academic year to which classes, enrollments, grades, and educational activities belong.

Example:

```text
1405-1406
```

---

### Term

**فارسی:**
یک دوره یا نیم‌سال آموزشی در یک سال تحصیلی.

**English:**
Represents a term or semester within an academic year.

Examples:

```text
First Semester
Second Semester
Summer Term
```

---

### Grade

**فارسی:**
پایه تحصیلی دانش‌آموزان.

**English:**
Represents an educational grade or level.

Examples:

```text
Grade 7
Grade 8
Grade 9
Grade 10
Grade 11
Grade 12
```

---

### Classroom

**فارسی:**
یک کلاس مشخص در مدرسه و سال تحصیلی.

**English:**
Represents a specific classroom within a school and academic year.

Example:

```text
Grade 10 - Experimental Sciences - Class 1
```

---

# 3. Students — دانش‌آموزان

مسئول اطلاعات و وضعیت آموزشی دانش‌آموزان.

Responsible for student profiles, enrollments, and parent relationships.

```text
students/
├── StudentProfile
├── Enrollment
└── ParentStudent
```

### StudentProfile

**فارسی:**
اطلاعات اختصاصی یک دانش‌آموز را نگهداری می‌کند و به User متصل است.

**English:**
Stores student-specific information and is connected to the main User model.

Relationship:

```text
User
  ↓
StudentProfile
```

---

### Enrollment

**فارسی:**
ثبت می‌کند که یک دانش‌آموز در چه کلاس، پایه و سال تحصیلی قرار دارد.

**English:**
Defines the enrollment of a student in a classroom, grade, and academic year.

Example:

```text
Student
    ↓
Classroom
    ↓
AcademicYear
```

---

### ParentStudent

**فارسی:**
رابطه بین والد و دانش‌آموز را مدیریت می‌کند.

**English:**
Defines the relationship between parents and students.

این رابطه باید بتواند چند به چند باشد.

The relationship should support multiple parents and multiple students.

```text
Parent
 ├── Student A
 ├── Student B
 └── Student C
```

---

# 4. Teachers — معلمان

اطلاعات تخصصی معلمان را مدیریت می‌کند.

Manages teacher-specific information.

```text
teachers/
└── TeacherProfile
```

### TeacherProfile

**فارسی:**
اطلاعات حرفه‌ای و آموزشی معلم را نگهداری می‌کند.

**English:**
Stores professional and educational information about a teacher.

Examples:

```text
Employee Code
Education
Experience
Specializations
Biography
```

Relationship:

```text
User
  ↓
TeacherProfile
```

---

# 5. Subjects — دروس و دوره‌ها

تعریف درس و ارائه‌های مختلف آن.

Defines subjects and their course offerings.

```text
subjects/
├── Subject
└── Course
```

### Subject

**فارسی:**
مفهوم اصلی یک درس را تعریف می‌کند.

**English:**
Defines the base concept of an educational subject.

Examples:

```text
Mathematics
Physics
Chemistry
English
Literature
```

---

### Course

**فارسی:**
یک ارائه مشخص از یک درس برای یک پایه، مدرس، کلاس یا دوره آموزشی است.

**English:**
Represents a specific offering of a subject for a particular grade, teacher, classroom, or educational period.

Example:

```text
Subject:
Mathematics

Course:
Grade 10 Mathematics - 1405
```

---

# 6. Content — محتوای آموزشی

هسته محتوای آموزشی سیستم.

The core educational content domain.

```text
content/
├── Section
├── Lesson
├── Article
├── Video
└── EducationalFile
```

### Section

**فارسی:**
یک فصل یا بخش اصلی از یک Course.

**English:**
Represents a major section or chapter of a course.

Example:

```text
Mathematics
├── Chapter 1: Sets
├── Chapter 2: Probability
└── Chapter 3: Algebra
```

---

### Lesson

**فارسی:**
یک درس مشخص داخل یک Section.

**English:**
Represents a specific lesson inside a section.

Example:

```text
Chapter 1
    ↓
Introduction to Sets
```

---

### Article

**فارسی:**
محتوای متنی یک درس، معمولاً به صورت Rich Text/HTML.

**English:**
Represents textual lesson content, usually stored as Rich Text or HTML.

Can contain:

```text
Text
Images
Tables
Formulas
Code
Links
```

---

### Video

**فارسی:**
ویدئوی آموزشی مرتبط با یک درس.

**English:**
Represents an educational video associated with a lesson.

Possible providers:

```text
Local Storage
Object Storage
CDN
External Video Provider
```

---

### EducationalFile

**فارسی:**
فایل‌های آموزشی مرتبط با درس.

**English:**
Represents educational files attached to lessons.

Examples:

```text
PDF
DOCX
PPTX
ZIP
Image
Worksheet
```

---

# 7. Questions — بانک سؤال

مدیریت بانک سؤال و ساختار سؤال‌ها.

Manages question banks and reusable questions.

```text
questions/
├── QuestionBank
├── Question
├── Choice
├── Tag
└── Category
```

### QuestionBank

**فارسی:**
مجموعه‌ای از سؤال‌های قابل استفاده مجدد.

**English:**
A reusable collection of questions.

Example:

```text
Grade 10 Mathematics Question Bank
```

---

### Question

**فارسی:**
مدل اصلی سؤال.

**English:**
The main question model.

Possible properties:

```text
Question Type
Difficulty
Score
Negative Score
Explanation
Subject
Section
Lesson
```

Possible types:

```text
Multiple Choice
Multiple Select
True / False
Short Answer
Long Answer
Numeric
Fill in the Blank
Matching
Ordering
```

---

### Choice

**فارسی:**
گزینه‌های یک سؤال، مخصوصاً برای سؤال‌های چندگزینه‌ای.

**English:**
Represents answer choices for questions such as multiple-choice questions.

Example:

```text
A → 10
B → 20
C → 30
D → 40
```

---

### Tag

**فارسی:**
برچسب برای دسته‌بندی و جستجوی بهتر سؤال‌ها.

**English:**
A label used for question classification and searching.

Examples:

```text
Algebra
Hard
Exam
Conceptual
Calculation
```

---

### Category

**فارسی:**
دسته‌بندی سلسله‌مراتبی سؤال‌ها.

**English:**
Provides hierarchical categorization for questions.

Example:

```text
Mathematics
└── Algebra
    └── Quadratic Equations
```

---

# 8. Exams — آزمون‌ها

مدیریت آزمون، شرکت در آزمون و پاسخ‌ها.

Manages exams, attempts, and answers.

```text
exams/
├── Exam
├── ExamQuestion
├── ExamAttempt
└── ExamAnswer
```

### Exam

**فارسی:**
تعریف یک آزمون.

**English:**
Defines an examination.

Examples:

```text
Title
Duration
Start Time
End Time
Total Score
Attempts Limit
Status
```

---

### ExamQuestion

**فارسی:**
رابط بین آزمون و سؤال است و مشخص می‌کند چه سؤال‌هایی در آزمون قرار گرفته‌اند.

**English:**
Connects an exam to its questions and defines how each question behaves inside the exam.

Can contain:

```text
Order
Score
Negative Score
```

---

### ExamAttempt

**فارسی:**
یک بار شرکت یک دانش‌آموز در یک آزمون.

**English:**
Represents one attempt of a student taking an exam.

Contains:

```text
Student
Exam
Started At
Submitted At
Status
Score
Percentage
```

---

### ExamAnswer

**فارسی:**
پاسخ دانش‌آموز به یک سؤال در یک Attempt.

**English:**
Stores a student's answer to a question during an exam attempt.

Contains:

```text
Selected Choice
Text Answer
Is Correct
Score
```

---

# 9. Assignments — تکالیف

مدیریت تکالیف و تحویل آن‌ها.

Manages assignments and student submissions.

```text
assignments/
├── Assignment
└── Submission
```

### Assignment

**فارسی:**
تکلیفی که توسط معلم برای دانش‌آموزان تعریف می‌شود.

**English:**
An assignment created by a teacher for students.

Contains:

```text
Title
Description
Course
Teacher
Deadline
Maximum Score
```

---

### Submission

**فارسی:**
پاسخ یا فایل تحویل داده‌شده توسط دانش‌آموز.

**English:**
Represents a student's submission for an assignment.

Contains:

```text
Answer
File
Submitted At
Score
Teacher Feedback
```

---

# 10. Live Classes — کلاس‌های آنلاین

مدیریت کلاس‌های زنده و ضبط آن‌ها.

Manages live online classes and recordings.

```text
live_classes/
├── LiveClass
└── Recording
```

### LiveClass

**فارسی:**
یک جلسه کلاس آنلاین زنده.

**English:**
Represents a live online class session.

Contains:

```text
Teacher
Course
Start Time
End Time
Meeting URL
Status
```

---

### Recording

**فارسی:**
ضبط یک کلاس آنلاین که پس از پایان جلسه قابل مشاهده است.

**English:**
Stores the recording of a live class for later viewing.

---

# 11. Progress — پیشرفت آموزشی

پیگیری میزان پیشرفت دانش‌آموز.

Tracks student learning progress.

```text
progress/
├── LessonProgress
├── CourseProgress
└── VideoProgress
```

### LessonProgress

**فارسی:**
مشخص می‌کند دانش‌آموز یک درس را شروع یا تکمیل کرده و چه میزان پیشرفت داشته است.

**English:**
Tracks whether a student has started or completed a lesson and how much progress has been made.

---

### CourseProgress

**فارسی:**
درصد پیشرفت دانش‌آموز در کل دوره.

**English:**
Tracks the overall progress of a student within a course.

Example:

```text
Mathematics
████████████░░ 80%
```

---

### VideoProgress

**فارسی:**
موقعیت مشاهده ویدئو را ذخیره می‌کند تا دانش‌آموز بتواند از همان نقطه ادامه دهد.

**English:**
Stores the student's video playback position so they can continue watching from where they stopped.

Example:

```text
Duration: 3600 seconds
Last Position: 2180 seconds
```

---

# 12. Grading — نمرات و کارنامه

مدیریت نمرات، انواع ارزیابی و کارنامه.

Manages grades, grading categories, and report cards.

```text
grading/
├── Grade
├── GradeCategory
└── ReportCard
```

### Grade

**فارسی:**
یک نمره ثبت‌شده برای یک دانش‌آموز.

**English:**
Represents a grade assigned to a student.

Examples:

```text
Exam: 18.5
Assignment: 19
Quiz: 17
```

---

### GradeCategory

**فارسی:**
نوع فعالیتی که باعث ایجاد نمره شده است.

**English:**
Defines the category or source of a grade.

Examples:

```text
Exam
Quiz
Assignment
Project
Participation
Homework
```

---

### ReportCard

**فارسی:**
کارنامه یک دانش‌آموز در یک دوره یا ترم.

**English:**
Represents a student's report card for an academic period.

Example:

```text
Mathematics    18
Physics        17
Chemistry      19
```

---

# 13. Communication — ارتباطات

مدیریت پیام‌ها، گفتگوها و اعلان‌ها.

Manages conversations, messages, and notifications.

```text
communication/
├── Conversation
├── Message
└── Notification
```

### Conversation

**فارسی:**
یک گفتگوی بین دو یا چند کاربر.

**English:**
Represents a conversation between two or more users.

Examples:

```text
Teacher ↔ Student
Teacher ↔ Parent
Admin ↔ Teacher
```

---

### Message

**فارسی:**
یک پیام داخل یک Conversation.

**English:**
Represents an individual message inside a conversation.

---

### Notification

**فارسی:**
اعلان‌های سیستمی برای اطلاع‌رسانی به کاربران.

**English:**
System notifications sent to users.

Examples:

```text
New Assignment
Upcoming Exam
New Grade
New Message
Live Class Reminder
```

---

# 14. Payments — پرداخت‌ها

مدیریت سفارش و تراکنش‌های مالی.

Manages orders and financial transactions.

```text
payments/
├── Order
├── Payment
└── Transaction
```

### Order

**فارسی:**
سفارش ایجادشده توسط کاربر.

**English:**
Represents an order created by a user.

Example:

```text
Purchase Mathematics Course
```

---

### Payment

**فارسی:**
اطلاعات مربوط به پرداخت یک سفارش.

**English:**
Stores payment information associated with an order.

Contains:

```text
Amount
Gateway
Status
Reference Number
Paid At
```

---

### Transaction

**فارسی:**
ثبت دقیق عملیات مالی در سیستم.

**English:**
Represents a financial transaction in the system.

این مدل برای ثبت سوابق مالی و جلوگیری از وابستگی مستقیم به Payment استفاده می‌شود.

---

# 15. Subscriptions — اشتراک‌ها

مدیریت پلن‌های اشتراکی سیستم.

Manages subscription plans and user subscriptions.

```text
subscriptions/
├── Plan
└── Subscription
```

### Plan

**فارسی:**
تعریف یک پلن اشتراک و امکانات آن.

**English:**
Defines a subscription plan and its available features.

Examples:

```text
Free
Basic
Professional
School
Enterprise
```

---

### Subscription

**فارسی:**
اشتراک فعال یک کاربر یا سازمان.

**English:**
Represents an active subscription belonging to a user or organization.

Contains:

```text
Plan
Start Date
End Date
Status
Auto Renewal
```

---

# 16. Audit — ثبت فعالیت‌های سیستم

ثبت فعالیت‌های حساس و مهم سیستم.

Tracks important and security-sensitive system activities.

```text
audit/
└── AuditLog
```

### AuditLog

**فارسی:**
ثبت می‌کند چه کاربری چه عملیاتی را روی چه داده‌ای انجام داده است.

**English:**
Records which user performed which action on which object.

Examples:

```text
Admin changed a student's grade.

Teacher deleted a question.

Admin disabled a user.
```

Possible fields:

```text
User
Action
Object Type
Object ID
Timestamp
IP Address
Old Value
New Value
```

---

# Overall Domain Architecture — معماری کلی

```text
User
│
├── StudentProfile
├── TeacherProfile
└── Parent
     │
     └── ParentStudent
             │
             ↓
         Student
             │
             ↓
        Enrollment
             │
             ↓
         Classroom
             │
             ↓
           Course
             │
       ┌─────┴─────┐
       ↓           ↓
    Section      Teacher
       │
       ↓
     Lesson
       │
   ┌───┼────────────┐
   ↓   ↓            ↓
Article Video   EducationalFile
   │
   ↓
Progress


Course
│
├── Assignment
│      └── Submission
│
└── Exam
       │
       ├── ExamQuestion
       │       ↓
       │    Question
       │       ↓
       │     Choice
       │
       └── ExamAttempt
               ↓
           ExamAnswer
               ↓
             Grade
               ↓
          ReportCard
```

---

# Recommended Future Extension — توسعه آینده

این معماری باید از ابتدا به شکلی طراحی شود که بتوان قابلیت‌های زیر را بدون تغییر اساسی در هسته سیستم اضافه کرد:

```text
AI Assistant
AI Question Generator
Adaptive Learning
Online Whiteboard
Discussion Forum
Gamification
Badges
Certificates
Leaderboard
Advanced Analytics
Mobile Application
REST API
GraphQL API
WebSocket
Push Notifications
Multiple Schools
Multi-Tenant Architecture
```

همچنین برای Content بهتر است در نسخه نهایی معماری، به جای وابستگی شدید به `Article`، `Video` و `EducationalFile`، یک مفهوم عمومی مانند `LessonResource` یا `ContentBlock` در نظر گرفته شود.

This allows the system to support additional content types such as:

```text
Text
Video
Audio
PDF
Image
Presentation
Embed
External Link
Interactive Content
Quiz
```

بدون اینکه ساختار اصلی `Lesson` نیاز به تغییر اساسی داشته باشد.

---

# Architecture Principles — اصول معماری

این پروژه باید بر اساس اصول زیر توسعه داده شود:

1. **Modular Architecture — معماری ماژولار**
2. **Domain Separation — جداسازی حوزه‌های کسب‌وکار**
3. **Django SSR First — استفاده از SSR به عنوان معماری اصلی**
4. **Reusable Components — اجزای قابل استفاده مجدد**
5. **Loose Coupling — وابستگی کم بین Appها**
6. **Clear Model Responsibilities — مسئولیت مشخص برای هر Model**
7. **Scalability — قابلیت توسعه و مقیاس‌پذیری**
8. **Security by Design — امنیت از مرحله طراحی**
9. **Auditability — قابلیت ثبت و پیگیری فعالیت‌ها**
10. **API Ready — آمادگی برای ارائه API در آینده**
11. **Testability — قابلیت تست آسان**
12. **Maintainability — نگهداری و توسعه آسان**
