# Model Relationships

# روابط بین مدل‌ها

این فایل روابط اصلی بین مدل‌های سامانه مدرسه و آموزش آنلاین را مشخص می‌کند.

This document defines the main relationships between the models of the school and online learning platform.

---

# 1. Accounts

## User → Role

**Relationship:** Many-to-Many

**فارسی:**
هر کاربر می‌تواند یک یا چند نقش داشته باشد و هر نقش می‌تواند به چند کاربر اختصاص داده شود.

**English:**
A user can have one or more roles, and each role can be assigned to multiple users.

```text
User * ──── * Role
```

---

## Role → Permission

**Relationship:** Many-to-Many

**فارسی:**
هر نقش می‌تواند چند مجوز داشته باشد و هر مجوز می‌تواند در چند نقش استفاده شود.

**English:**
A role can have multiple permissions, and a permission can belong to multiple roles.

```text
Role * ──── * Permission
```

> در Django بهتر است برای این بخش تا حد امکان از `Group` و `Permission` داخلی Django استفاده شود.

---

# 2. Schools

## School → AcademicYear

**Relationship:** One-to-Many

**فارسی:**
هر مدرسه می‌تواند چند سال تحصیلی داشته باشد، اما هر سال تحصیلی متعلق به یک مدرسه است.

**English:**
A school can have multiple academic years, while each academic year belongs to one school.

```text
School 1 ──── * AcademicYear
```

---

## AcademicYear → Term

**Relationship:** One-to-Many

**فارسی:**
هر سال تحصیلی می‌تواند شامل چند ترم یا نیم‌سال باشد.

**English:**
An academic year can contain multiple terms.

```text
AcademicYear 1 ──── * Term
```

---

## AcademicYear → Grade

**Relationship:** One-to-Many

**فارسی:**
هر سال تحصیلی می‌تواند برای پایه‌های مختلف تحصیلی ساختار داشته باشد.

**English:**
An academic year can contain grade-level structures.

```text
AcademicYear 1 ──── * Grade
```

---

## Grade → Classroom

**Relationship:** One-to-Many

**فارسی:**
هر پایه می‌تواند چند کلاس داشته باشد.

**English:**
A grade can contain multiple classrooms.

```text
Grade 1 ──── * Classroom
```

---

## AcademicYear → Classroom

**Relationship:** One-to-Many

**فارسی:**
هر کلاس به یک سال تحصیلی مشخص تعلق دارد.

**English:**
Each classroom belongs to a specific academic year.

```text
AcademicYear 1 ──── * Classroom
```

---

# 3. Students

## User → StudentProfile

**Relationship:** One-to-One

**فارسی:**
هر دانش‌آموز یک حساب کاربری دارد و اطلاعات تخصصی دانش‌آموز در `StudentProfile` نگهداری می‌شود.

**English:**
Each student has one user account, while student-specific information is stored in `StudentProfile`.

```text
User 1 ──── 1 StudentProfile
```

---

## StudentProfile → Enrollment

**Relationship:** One-to-Many

**فارسی:**
یک دانش‌آموز می‌تواند در طول سال‌های مختلف چند سابقه ثبت‌نام داشته باشد.

**English:**
A student can have multiple enrollment records across different academic years or classes.

```text
StudentProfile 1 ──── * Enrollment
```

---

## Classroom → Enrollment

**Relationship:** One-to-Many

**فارسی:**
هر کلاس می‌تواند دانش‌آموزان زیادی داشته باشد.

**English:**
A classroom can have many enrolled students.

```text
Classroom 1 ──── * Enrollment
```

---

## Parent → Student

**Relationship:** Many-to-Many through `ParentStudent`

**فارسی:**
یک والد می‌تواند چند فرزند داشته باشد و یک دانش‌آموز نیز می‌تواند چند والد یا سرپرست داشته باشد.

**English:**
A parent can have multiple children, and a student can have multiple parents or guardians.

```text
Parent * ──── * Student
          │
          └── ParentStudent
```

> در پیاده‌سازی، `ParentStudent` می‌تواند اطلاعاتی مانند نوع رابطه، سرپرست اصلی بودن و وضعیت فعال بودن رابطه را نیز نگهداری کند.

---

# 4. Teachers

## User → TeacherProfile

**Relationship:** One-to-One

**فارسی:**
هر معلم دارای یک حساب کاربری و یک پروفایل تخصصی معلم است.

**English:**
Each teacher has one user account and one teacher profile.

```text
User 1 ──── 1 TeacherProfile
```

---

# 5. Subjects & Courses

## Subject → Course

**Relationship:** One-to-Many

**فارسی:**
یک درس مانند «ریاضی» می‌تواند در قالب چند دوره یا ارائه آموزشی مختلف ارائه شود.

**English:**
A subject such as Mathematics can have multiple course offerings.

```text
Subject 1 ──── * Course
```

---

## Course → Section

**Relationship:** One-to-Many

**فارسی:**
هر دوره می‌تواند چند بخش آموزشی داشته باشد.

**English:**
A course can contain multiple sections.

```text
Course 1 ──── * Section
```

---

## Section → Lesson

**Relationship:** One-to-Many

**فارسی:**
هر بخش شامل چند جلسه یا درس آموزشی است.

**English:**
A section contains multiple lessons.

```text
Section 1 ──── * Lesson
```

---

# 6. Course / Classroom / Teacher

برای یک سیستم واقعی مدرسه، بهتر است ارتباط مستقیم و ساده‌ی `Course → Teacher` کافی نباشد.

بهتر است در آینده یک مدل واسط مانند:

```text
TeachingAssignment
```

داشته باشیم.

این مدل می‌تواند مشخص کند:

* چه معلمی
* چه درسی
* برای چه کلاسی
* در چه سال تحصیلی
* و در چه ترمی

تدریس می‌کند.

**English:**

A real school system should usually introduce a `TeachingAssignment` entity to represent which teacher teaches which course to which classroom during a specific academic year and term.

```text
Teacher
   │
   │
TeachingAssignment
   │
   ├──── Course
   ├──── Classroom
   ├──── AcademicYear
   └──── Term
```

---

# 7. Content

## Lesson → Article

**Relationship:** One-to-Many

**فارسی:**
یک درس می‌تواند چند محتوای متنی داشته باشد.

**English:**
A lesson can contain multiple article/text resources.

```text
Lesson 1 ──── * Article
```

---

## Lesson → Video

**Relationship:** One-to-Many

**فارسی:**
هر درس می‌تواند چند ویدئوی آموزشی داشته باشد.

**English:**
A lesson can contain multiple educational videos.

```text
Lesson 1 ──── * Video
```

---

## Lesson → EducationalFile

**Relationship:** One-to-Many

**فارسی:**
هر درس می‌تواند چند فایل آموزشی مانند PDF، PowerPoint یا فایل تمرین داشته باشد.

**English:**
A lesson can contain multiple educational files such as PDFs, presentations, or worksheets.

```text
Lesson 1 ──── * EducationalFile
```

---

## پیشنهاد معماری محتوا

برای توسعه‌پذیری بیشتر، می‌توان این ساختار را در آینده به یک مدل عمومی‌تر مانند `LessonResource` یا `ContentBlock` تبدیل کرد.

**English:**

For better extensibility, the content architecture can later be replaced by a generic `LessonResource` or `ContentBlock` model.

```text
Lesson 1 ──── * LessonResource
                    │
                    ├── Text
                    ├── Video
                    ├── Audio
                    ├── PDF
                    ├── Image
                    ├── Presentation
                    ├── Embed
                    └── ExternalLink
```

---

# 8. Questions

## QuestionBank → Question

**Relationship:** One-to-Many

**فارسی:**
هر بانک سؤال می‌تواند شامل تعداد زیادی سؤال باشد.

**English:**
A question bank can contain many questions.

```text
QuestionBank 1 ──── * Question
```

---

## Question → Choice

**Relationship:** One-to-Many

**فارسی:**
هر سؤال چندگزینه‌ای می‌تواند چند گزینه داشته باشد.

**English:**
A multiple-choice question can have multiple choices.

```text
Question 1 ──── * Choice
```

---

## Question → Tag

**Relationship:** Many-to-Many

**فارسی:**
یک سؤال می‌تواند چند برچسب داشته باشد و یک برچسب می‌تواند روی چند سؤال استفاده شود.

**English:**
A question can have multiple tags, and a tag can be assigned to multiple questions.

```text
Question * ──── * Tag
```

---

## Question → Category

**Relationship:** Many-to-Many

**فارسی:**
سؤال‌ها می‌توانند در چند دسته‌بندی قرار بگیرند.

**English:**
Questions can belong to multiple categories.

```text
Question * ──── * Category
```

---

# 9. Exams

## Exam → ExamQuestion

**Relationship:** One-to-Many

**فارسی:**
هر آزمون می‌تواند شامل چند سؤال باشد.

**English:**
An exam can contain multiple exam-question records.

```text
Exam 1 ──── * ExamQuestion
```

---

## Question → ExamQuestion

**Relationship:** One-to-Many

**فارسی:**
یک سؤال موجود در بانک سؤال می‌تواند در آزمون‌های مختلف استفاده شود.

**English:**
A reusable question can be used in multiple exams.

```text
Question 1 ──── * ExamQuestion
```

بنابراین:

```text
Exam * ──── * Question
          │
          └── ExamQuestion
```

---

## Student → ExamAttempt

**Relationship:** One-to-Many

**فارسی:**
یک دانش‌آموز می‌تواند برای آزمون‌های مختلف چند تلاش یا Attempt داشته باشد.

**English:**
A student can have multiple exam attempts across different exams.

```text
Student 1 ──── * ExamAttempt
```

---

## Exam → ExamAttempt

**Relationship:** One-to-Many

**فارسی:**
هر آزمون می‌تواند توسط دانش‌آموزان مختلف چندین بار مورد تلاش قرار گیرد.

**English:**
An exam can have multiple attempts from different students.

```text
Exam 1 ──── * ExamAttempt
```

---

## ExamAttempt → ExamAnswer

**Relationship:** One-to-Many

**فارسی:**
هر تلاش آزمون شامل پاسخ‌های مربوط به سؤال‌های مختلف است.

**English:**
Each exam attempt contains answers for individual questions.

```text
ExamAttempt 1 ──── * ExamAnswer
```

---

## ExamQuestion → ExamAnswer

**Relationship:** One-to-Many

**فارسی:**
هر سؤال آزمون می‌تواند در تلاش‌های مختلف دانش‌آموزان پاسخ داده شود.

**English:**
An exam question can have answers from multiple student attempts.

```text
ExamQuestion 1 ──── * ExamAnswer
```

---

# 10. Assignments

## Course → Assignment

**Relationship:** One-to-Many

**فارسی:**
هر دوره می‌تواند چند تکلیف داشته باشد.

**English:**
A course can contain multiple assignments.

```text
Course 1 ──── * Assignment
```

---

## Assignment → Submission

**Relationship:** One-to-Many

**فارسی:**
هر تکلیف می‌تواند توسط دانش‌آموزان مختلف چندین ارسال داشته باشد.

**English:**
An assignment can have multiple submissions from students.

```text
Assignment 1 ──── * Submission
```

---

## Student → Submission

**Relationship:** One-to-Many

**فارسی:**
هر دانش‌آموز می‌تواند تکالیف مختلفی ارسال کند.

**English:**
A student can create multiple assignment submissions.

```text
Student 1 ──── * Submission
```

---

# 11. Live Classes

## Course → LiveClass

**Relationship:** One-to-Many

**فارسی:**
یک دوره می‌تواند چند کلاس آنلاین یا Live Class داشته باشد.

**English:**
A course can contain multiple live classes.

```text
Course 1 ──── * LiveClass
```

---

## LiveClass → Recording

**Relationship:** One-to-Many

**فارسی:**
یک کلاس آنلاین می‌تواند یک یا چند فایل ضبط‌شده داشته باشد.

**English:**
A live class can have one or multiple recordings.

```text
LiveClass 1 ──── * Recording
```

---

# 12. Progress

## Student → LessonProgress

**Relationship:** One-to-Many

**فارسی:**
برای هر دانش‌آموز می‌توان وضعیت پیشرفت او در درس‌های مختلف را ذخیره کرد.

**English:**
A student's progress can be tracked across multiple lessons.

```text
Student 1 ──── * LessonProgress
```

---

## Lesson → LessonProgress

**Relationship:** One-to-Many

**فارسی:**
یک درس می‌تواند برای دانش‌آموزان مختلف رکورد پیشرفت داشته باشد.

**English:**
A lesson can have progress records for multiple students.

```text
Lesson 1 ──── * LessonProgress
```

---

## Student → CourseProgress

**Relationship:** One-to-Many

**فارسی:**
یک دانش‌آموز می‌تواند پیشرفت خود را در دوره‌های مختلف داشته باشد.

**English:**
A student can have progress records for multiple courses.

```text
Student 1 ──── * CourseProgress
```

---

## Course → CourseProgress

**Relationship:** One-to-Many

**فارسی:**
یک دوره می‌تواند برای دانش‌آموزان مختلف رکورد پیشرفت داشته باشد.

**English:**
A course can have progress records for multiple students.

```text
Course 1 ──── * CourseProgress
```

---

## Student → VideoProgress

**Relationship:** One-to-Many

**فارسی:**
وضعیت مشاهده و پیشرفت ویدئوهای مختلف توسط دانش‌آموز ذخیره می‌شود.

**English:**
A student's viewing progress can be tracked across multiple videos.

```text
Student 1 ──── * VideoProgress
```

---

## Video → VideoProgress

**Relationship:** One-to-Many

**فارسی:**
هر ویدئو می‌تواند برای دانش‌آموزان مختلف رکورد پیشرفت داشته باشد.

**English:**
A video can have progress records for multiple students.

```text
Video 1 ──── * VideoProgress
```

---

# 13. Grading

## Course → Grade

**Relationship:** One-to-Many

**فارسی:**
هر دوره می‌تواند چند نمره یا ارزیابی داشته باشد.

**English:**
A course can have multiple grade records.

```text
Course 1 ──── * Grade
```

---

## Student → Grade

**Relationship:** One-to-Many

**فارسی:**
هر دانش‌آموز می‌تواند برای دوره‌ها و فعالیت‌های مختلف چندین نمره داشته باشد.

**English:**
A student can have multiple grades across courses and assessments.

```text
Student 1 ──── * Grade
```

---

## GradeCategory → Grade

**Relationship:** One-to-Many

**فارسی:**
هر دسته‌بندی نمره می‌تواند شامل چند رکورد نمره باشد.

**English:**
A grade category can contain multiple grade records.

```text
GradeCategory 1 ──── * Grade
```

---

## Student → ReportCard

**Relationship:** One-to-Many

**فارسی:**
یک دانش‌آموز می‌تواند در سال‌ها و ترم‌های مختلف چند کارنامه داشته باشد.

**English:**
A student can have multiple report cards across academic years and terms.

```text
Student 1 ──── * ReportCard
```

---

## AcademicYear → ReportCard

**Relationship:** One-to-Many

**فارسی:**
هر کارنامه به یک سال تحصیلی مشخص مربوط است.

**English:**
Each report card belongs to a specific academic year.

```text
AcademicYear 1 ──── * ReportCard
```

---

## Term → ReportCard

**Relationship:** One-to-Many

**فارسی:**
هر کارنامه می‌تواند مربوط به یک ترم مشخص باشد.

**English:**
A report card can belong to a specific term.

```text
Term 1 ──── * ReportCard
```

---

# 14. Communication

## Conversation → Message

**Relationship:** One-to-Many

**فارسی:**
هر گفتگو شامل چند پیام است.

**English:**
A conversation contains multiple messages.

```text
Conversation 1 ──── * Message
```

---

## User → Message

**Relationship:** One-to-Many

**فارسی:**
هر کاربر می‌تواند پیام‌های مختلفی ارسال یا دریافت کند.

**English:**
A user can send and receive multiple messages.

```text
User 1 ──── * Message
```

---

## User → Notification

**Relationship:** One-to-Many

**فارسی:**
هر کاربر می‌تواند اعلان‌های متعددی دریافت کند.

**English:**
A user can receive multiple notifications.

```text
User 1 ──── * Notification
```

---

# 15. Payments

## User → Order

**Relationship:** One-to-Many

**فارسی:**
یک کاربر می‌تواند چند سفارش داشته باشد.

**English:**
A user can have multiple orders.

```text
User 1 ──── * Order
```

---

## Order → Payment

**Relationship:** One-to-Many

**فارسی:**
یک سفارش می‌تواند شامل چند تلاش پرداخت باشد.

**English:**
An order can have multiple payment attempts.

```text
Order 1 ──── * Payment
```

---

## Payment → Transaction

**Relationship:** One-to-Many

**فارسی:**
هر پرداخت می‌تواند شامل چند تراکنش یا رویداد مالی باشد.

**English:**
A payment can have multiple financial transaction records.

```text
Payment 1 ──── * Transaction
```

---

# 16. Subscriptions

## Plan → Subscription

**Relationship:** One-to-Many

**فارسی:**
هر پلن اشتراک می‌تواند توسط کاربران مختلف خریداری شود.

**English:**
A subscription plan can be used by multiple users.

```text
Plan 1 ──── * Subscription
```

---

## User → Subscription

**Relationship:** One-to-Many

**فارسی:**
یک کاربر می‌تواند در طول زمان چند اشتراک داشته باشد.

**English:**
A user can have multiple subscriptions over time.

```text
User 1 ──── * Subscription
```

---

## Order → Subscription

**Relationship:** One-to-One / One-to-Many

**فارسی:**
بسته به منطق پرداخت، یک سفارش می‌تواند یک اشتراک ایجاد کند یا در آینده از یک سفارش برای چند محصول/اشتراک استفاده شود.

**English:**
Depending on the business model, an order may create one subscription or support multiple subscription items.

```text
Order 1 ──── 1 Subscription
```

> برای نسخه ساده، `One-to-One` مناسب است. برای فروش چند محصول در یک سفارش، بهتر است بعداً `OrderItem` اضافه شود.

---

# 17. Audit

## User → AuditLog

**Relationship:** One-to-Many

**فارسی:**
هر کاربر می‌تواند چندین عملیات ثبت‌شده در سیستم داشته باشد.

**English:**
A user can have multiple audit log records.

```text
User 1 ──── * AuditLog
```

---

## AuditLog → Target Object

**Relationship:** Generic Relation

**فارسی:**
لاگ حسابرسی باید بتواند به مدل‌های مختلف سیستم اشاره کند؛ برای مثال:

* User
* Student
* Exam
* Grade
* Payment
* Course
* Assignment

بنابراین بهتر است به‌جای ForeignKey مستقیم، از `ContentType + object_id` استفاده شود.

**English:**
An audit log should be able to reference different objects across the system, such as users, exams, grades, payments, courses, and assignments.

A generic relation using `ContentType + object_id` is therefore recommended.

```text
AuditLog ──── GenericRelation ──── Any Model
```

---

# 18. Main Relationship Overview

نمای کلی روابط اصلی سیستم:

```text
User
│
├── StudentProfile
│      └── Enrollment ─── Classroom
│
├── TeacherProfile
│      └── TeachingAssignment
│               ├── Course
│               ├── Classroom
│               ├── AcademicYear
│               └── Term
│
├── Role
│      └── Permission
│
├── Order
│      └── Payment
│             └── Transaction
│
├── Subscription
│      └── Plan
│
├── Notification
├── Message
└── AuditLog


School
│
└── AcademicYear
       ├── Term
       ├── Grade
       │    └── Classroom
       └── ReportCard


Subject
└── Course
     ├── Section
     │    └── Lesson
     │         ├── Article
     │         ├── Video
     │         └── EducationalFile
     │
     ├── Assignment
     │    └── Submission
     │
     ├── LiveClass
     │    └── Recording
     │
     └── Grade


QuestionBank
└── Question
     ├── Choice
     ├── Tag
     ├── Category
     │
     └── ExamQuestion
            └── Exam
                 └── ExamAttempt
                      └── ExamAnswer


Student
├── LessonProgress
├── CourseProgress
├── VideoProgress
├── Submission
├── ExamAttempt
├── Grade
└── ReportCard
```

---

# 19. Important Architectural Relationships

## Student ↔ Course

در یک سیستم آموزش آنلاین واقعی، بهتر است ارتباط دانش‌آموز و دوره مستقیماً از طریق `Enrollment` عمومی مدیریت نشود.

**English:**

In a real online learning platform, student-to-course enrollment should usually be represented explicitly.

پیشنهاد:

```text
Student
   │
   └── CourseEnrollment
           ├── Course
           ├── EnrollmentDate
           ├── Status
           └── CompletionDate
```

این موضوع اجازه می‌دهد یک دانش‌آموز بدون وابستگی به کلاس فیزیکی مدرسه، در دوره‌های آنلاین نیز ثبت‌نام کند.

---

# 20. Recommended Future Relationship Models

برای اینکه سیستم در آینده محدود نشود، مدل‌های زیر نیز می‌توانند اضافه شوند:

```text
TeachingAssignment
CourseEnrollment
OrderItem
ExamSection
QuestionVersion
LessonResource
Discussion
DiscussionReply
Certificate
Badge
StudentAchievement
Attendance
AttendanceRecord
StudyPlan
LearningPath
```

**English:**

The following entities may be introduced later to improve scalability and support additional educational features:

* `TeachingAssignment`
* `CourseEnrollment`
* `OrderItem`
* `ExamSection`
* `QuestionVersion`
* `LessonResource`
* `Discussion`
* `DiscussionReply`
* `Certificate`
* `Badge`
* `StudentAchievement`
* `Attendance`
* `AttendanceRecord`
* `StudyPlan`
* `LearningPath`

---

# 21. Relationship Design Principles

## اصل اول — مسئولیت مشخص

هر مدل باید یک مسئولیت مشخص داشته باشد.

**English:**
Each model should have a clear and focused responsibility.

---

## اصل دوم — وابستگی کم

روابط بین Domainها باید تا حد امکان کنترل‌شده و قابل توسعه باشند.

**English:**
Relationships between domains should remain controlled and loosely coupled.

---

## اصل سوم — تاریخچه اطلاعات

اطلاعات مهم مانند ثبت‌نام، نمره، پرداخت، آزمون و اشتراک نباید با تغییر وضعیت فعلی از بین بروند.

**English:**
Important historical information such as enrollments, grades, payments, exams, and subscriptions should be preserved.

---

## اصل چهارم — روابط واسط

هر زمان که رابطه Many-to-Many دارای اطلاعات اضافی است، باید از مدل واسط استفاده شود.

**English:**
Whenever a Many-to-Many relationship contains additional attributes, an explicit intermediate model should be used.

Examples:

```text
ParentStudent
ExamQuestion
TeachingAssignment
CourseEnrollment
OrderItem
```

---

## اصل پنجم — جلوگیری از وابستگی مستقیم غیرضروری

نباید هر مدل مستقیماً به تعداد زیادی مدل دیگر وابسته شود.

**English:**
Models should avoid unnecessary direct dependencies on many other models.

---

## اصل ششم — آماده بودن برای توسعه

ساختار روابط باید امکان اضافه شدن API، اپلیکیشن موبایل، هوش مصنوعی، کلاس آنلاین، سیستم اشتراک، چند مدرسه و امکانات آینده را بدون بازطراحی کامل فراهم کند.

**English:**
The relationship architecture should support future extensions such as APIs, mobile applications, AI features, live classes, subscriptions, multi-school support, and other future capabilities without requiring a complete redesign.
