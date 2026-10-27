# DIA LMS - Roles, Features, Navigation, and Login Guide

Prepared for: MGIT review/demo  
Purpose: This document explains the LMS in simple language so a first-time user can understand the platform, log in, and navigate through the website without needing technical help.

---

## 1. What This Platform Is

DIA LMS is a multi-tenant Learning Management System for institutes, coaching centers, colleges, and training organizations.

It is not meant to replace an existing college ERP. An ERP usually handles admissions, roll numbers, fee records, transport, payroll, attendance administration, and official student records. This platform focuses on the learning side:

- Creating exams, subjects, topics, and learning content
- Creating and managing mock tests
- Allowing students to practice topic-wise questions
- Tracking student performance
- Creating study plans
- Managing assignments and grading
- Conducting live classes
- Sending notifications
- Providing AI tools for students and admins
- Supporting multiple organizations/institutes on the same platform

In short: the ERP manages administration; this LMS manages learning, testing, practice, and academic progress.

---

## 2. Important Login Details

> Fill these details before submitting the document to madam.

| Role | Login URL | Email / Username | Password | Notes |
|---|---|---|---|---|
| Super Admin | `https://your-domain.com/login` | `ADD_EMAIL_HERE` | `ADD_PASSWORD_HERE` | Platform owner access |
| Main Co-Admin / Institute Admin | `https://your-domain.com/login` | `ADD_EMAIL_HERE` | `ADD_PASSWORD_HERE` | Manages one organization |
| Co-Admin / Faculty | `https://your-domain.com/login` | `ADD_EMAIL_HERE` | `ADD_PASSWORD_HERE` | Helps manage content, tests, assignments |
| Student | `https://your-domain.com/login` | `ADD_EMAIL_HERE` | `ADD_PASSWORD_HERE` | Learner access |

If an organization has its own subdomain, the login URL may look like:

```text
https://organization-name.your-domain.com/login
```

If the user forgets the password, they can use:

```text
/password/request
```

---

## 3. User Roles At A Glance

The platform has four major roles.

| Role | Simple Meaning | Main Responsibility |
|---|---|---|
| Super Admin | Platform owner | Controls all organizations, plans, users, approvals, reports, and platform-level settings |
| Main Co-Admin | Institute/admin head | Manages one organization, creates exams/content/users, checks analytics, controls organization settings |
| Co-Admin | Faculty/admin helper | Helps manage learning content, questions, mock tests, assignments, grading, calendar, and reports |
| Student | Learner | Studies content, practices questions, attempts mock tests, joins classes, submits assignments, uses AI tutor |

---

## 4. First-Time Website Navigation

### Step 1: Open The Website

Go to the main website URL or organization subdomain.

Common public pages:

- Home page: `/`
- Login: `/login`
- Register: `/register`
- Browse exams: `/browse-exams`
- Pricing: `/pricing`
- About: `/about`
- Contact: `/contact`
- FAQ: `/faq`
- Terms: `/terms`
- Privacy: `/privacy`

### Step 2: Log In

1. Click **Login**.
2. Enter email and password.
3. Click **Sign In**.
4. The system redirects the user to the correct dashboard based on role.

Dashboard routes:

| Role | Dashboard |
|---|---|
| Super Admin | `/super-admin/dashboard` |
| Main Co-Admin | `/main-co-admin/dashboard` |
| Co-Admin | `/co-admin/dashboard` |
| Student | `/student/dashboard` |

### Step 3: Use The Top Navigation

After login, users can use the top navigation bar to access:

- Dashboard
- Exams or My Exams
- Mock Tests
- Assignments
- Notifications
- Forum
- Profile
- Logout

The exact menu changes depending on the role.

---

## 5. Super Admin Guide

### Who Is The Super Admin?

The Super Admin is the platform-level owner. This user can see and control all organizations using the LMS.

### Main Pages For Super Admin

| Page | URL | Purpose |
|---|---|---|
| Dashboard | `/super-admin/dashboard` | View platform-wide statistics |
| Organizations and Users | `/super-admin/organizations-users` | Manage all organizations and users |
| Organization Details | `/super-admin/organization/<org_id>/details` | View/manage one organization |
| Plans | `/super-admin/plans` | Create/edit LMS subscription plans |
| Approval Queue | `/super-admin/approvals` | Approve or reject new organizations |
| Archived Content | `/super-admin/archive` | Restore or permanently delete archived items |
| Organization Reports | `/super-admin/organization-reports` | View complaints/reports against organizations |

### What Super Admin Can Do

- Create, view, edit, and delete organizations
- Approve or reject pending organizations
- Manage subscription plans
- Manage users across organizations
- Change user status and role
- View archived exams, subjects, topics, questions, and mock tests
- Restore archived content
- Permanently delete archived content
- View organization complaints/reports
- Suspend organizations if required
- View platform-wide dashboard metrics

### Suggested Super Admin Demo Flow

1. Log in as Super Admin.
2. Open `/super-admin/dashboard`.
3. Show total organizations, users, plans, and question statistics.
4. Open `/super-admin/organizations-users`.
5. Show how organizations and users are managed.
6. Open `/super-admin/plans`.
7. Show plan creation/editing.
8. Open `/super-admin/approvals`.
9. Explain how new institutes can be approved.
10. Open `/super-admin/archive`.
11. Explain soft delete and restore.

---

## 6. Main Co-Admin / Institute Admin Guide

### Who Is The Main Co-Admin?

The Main Co-Admin is the main administrator of one institute/organization. In a college or coaching center, this role can be given to the person responsible for managing the LMS for that organization.

### Main Pages For Main Co-Admin

| Page | URL | Purpose |
|---|---|---|
| Dashboard | `/main-co-admin/dashboard` | Organization-level dashboard |
| Exams | `/admin/exams` | Create and manage exams/courses |
| Select Exam For Content | `/admin/content/select-exam` | Choose exam before managing subjects/topics |
| Subjects | `/admin/exams/<exam_id>/subjects` | Manage subjects inside an exam |
| Topics | `/admin/subjects/<subject_id>/topics` | Manage topics inside a subject |
| Topic Content Editor | `/admin/topics/<topic_id>/content-editor` | Add text, video, PDF, or link content |
| Question Management | `/admin/topics/<topic_id>/questions` | Add and edit questions |
| Mock Tests | `/admin/mock-tests` | Create and manage mock tests |
| Assignments | `/admin/assignments` | Create assignments |
| Grade Submissions | `/admin/grade-submissions` | Review and grade submissions |
| Learning Intelligence | `/admin/learning-intelligence` | View learning analytics |
| Calendar | `/admin/calendar` | Schedule/manage classes |
| Locked Attempts | `/admin/locked-attempts` | Unlock locked student test attempts |
| Reported Content | `/admin/reported-content` | Review student-reported questions |
| Organization Users | `/main-co-admin/users` | Manage users in the organization |
| Organization Settings | `/organization/settings` | Update branding and organization pages |
| AI Assistant | `/admin/ai-assistant` | Use AI for content/question assistance |
| Notifications | `/my-notifications` | View notifications |
| Forum | `/forum` | Community discussion |

### What Main Co-Admin Can Do

- Manage organization dashboard
- Create and manage exams
- Add subjects under exams
- Add topics under subjects
- Add learning content under topics
- Upload or link PDFs, images, and videos
- Create MCQ, open-ended, and comprehension-style questions
- Import questions in bulk
- Create mock tests
- Add questions to mock tests
- Export topic/mock test content
- Generate mock test reports
- Create assignments
- Grade assignment submissions
- Use AI grading suggestions where enabled
- Create organization study plans
- Schedule live classes
- Import class schedules
- Send notifications
- Invite students and co-admins
- Import users
- Configure organization branding, public pages, FAQ, contact details, logo, and images
- Review reported questions
- Unlock locked mock test attempts

### Main Co-Admin Recommended Workflow

This is the best order for setting up an institute LMS:

1. Open **Organization Settings** and add branding.
2. Create an **Exam**.
3. Add **Subjects** inside the exam.
4. Add **Topics** inside each subject.
5. Add **Topic Content** such as notes, videos, PDFs, and links.
6. Add **Questions** for each topic.
7. Create **Mock Tests**.
8. Add questions to mock tests.
9. Invite or import students.
10. Create assignments or study plans.
11. Schedule live classes if required.
12. Track progress using dashboards and reports.

### Example: Creating Learning Content

1. Go to `/admin/exams`.
2. Create an exam, for example `Data Structures`.
3. Open subjects for that exam.
4. Add subject, for example `Algorithms`.
5. Open topics for that subject.
6. Add topic, for example `Sorting Algorithms`.
7. Open content editor.
8. Add notes, video, PDF, or useful links.
9. Save content.
10. Student can now study this topic from their dashboard.

### Example: Creating A Mock Test

1. Go to `/admin/mock-tests`.
2. Click create/add mock test.
3. Select exam.
4. Enter test name, duration, status, marks, and settings.
5. Add questions from the question bank.
6. Reorder questions if required.
7. Publish/activate the mock test.
8. Students can start the mock test from their student panel.

---

## 7. Co-Admin / Faculty Guide

### Who Is The Co-Admin?

The Co-Admin is usually a faculty member, trainer, or assistant admin. This role helps manage academic content and learning activities inside an organization.

### Main Pages For Co-Admin

| Page | URL | Purpose |
|---|---|---|
| Dashboard | `/co-admin/dashboard` | Faculty/admin helper dashboard |
| Exams | `/admin/exams` | View/manage allowed exams |
| Content Selection | `/admin/content/select-exam` | Select exam before content work |
| Subjects | `/admin/exams/<exam_id>/subjects` | Manage subjects |
| Topics | `/admin/subjects/<subject_id>/topics` | Manage topics |
| Content Editor | `/admin/topics/<topic_id>/content-editor` | Add learning material |
| Question Management | `/admin/topics/<topic_id>/questions` | Add/edit questions |
| Mock Tests | `/admin/mock-tests` | Manage mock tests |
| Assignments | `/admin/assignments` | Create assignments |
| Grade Submissions | `/admin/grade-submissions` | Grade submissions |
| Learning Intelligence | `/admin/learning-intelligence` | View analytics |
| Calendar | `/admin/calendar` | Schedule/manage classes |
| Reported Content | `/admin/reported-content` | Review reports |
| AI Assistant | `/admin/ai-assistant` | AI content helper |
| Forum | `/forum` | Discussion forum |

### What Co-Admin Can Do

- Help manage exams, subjects, topics, and content
- Add and edit questions
- Create or manage mock tests
- Upload learning files where allowed
- Create assignments
- Grade assignment submissions
- View learning analytics
- Manage calendar/live classes where allowed
- Review reported content
- Send or receive notifications
- Use AI assistant if enabled for the organization

### Simple Faculty Demo Flow

1. Log in as Co-Admin.
2. Open dashboard.
3. Open exam/content section.
4. Select one exam.
5. Open subjects and topics.
6. Add or edit content.
7. Add a few questions.
8. Open mock tests.
9. Show test creation/management.
10. Open assignments and show submission grading.

---

## 8. Student Guide

### Who Is The Student?

The Student is the learner. Students use the platform to access learning content, practice questions, attempt mock tests, attend live classes, submit assignments, and track their progress.

### Main Pages For Students

| Page | URL | Purpose |
|---|---|---|
| Dashboard | `/student/dashboard` | Student learning overview |
| My Exams | `/student/my-exams` | View enrolled exams |
| Browse Exams | `/browse-exams` | Search and enroll/purchase available exams |
| My Organizations | `/student/my-organizations` | View organizations joined by the student |
| Organization Dashboard | `/student/organization/<org_id>/exams` | View exams from one organization |
| Subjects | `/student/exams/<exam_id>/subjects` | View subjects inside an exam |
| Topics | `/student/topics/<subject_id>` | View topics inside a subject |
| Topic Content | `/student/topics/<topic_id>/content` | Read/watch learning content |
| Practice Questions | `/student/questions/<topic_id>` | Practice topic-wise questions |
| Mock Tests | `/student/mock-tests` | View available mock tests |
| Take Mock Test | `/student/mock-test/take/<attempt_id>` | Attempt a mock test |
| Test Result | `/student/mock-test/result/<attempt_id>` | View result after test |
| Leaderboard | `/student/mock-test/<mock_test_id>/leaderboard` | View rank/score comparison |
| Start Practice Test | `/student/start-practice-test` | Generate/start practice test |
| Review List | `/student/my-review-list` | View saved questions for revision |
| Study Plan | `/student/study-plan` | View AI/organization study plan |
| Learn With AI | `/learn-with-ai` | AI learning tools |
| AI Chat | `/student/ai-chat` | Chat with AI tutor |
| Assignments | `/student/assignments` | View and submit assignments |
| Transactions | `/student/transactions` | View purchases/subscriptions |
| Notifications | `/my-notifications` | Read notifications |
| Forum | `/forum` | Participate in community forum |

### What Students Can Do

- Register and verify email
- Join an organization using organization code
- Browse available exams
- Enroll in free exams
- Purchase paid exams where enabled
- View subjects and topics
- Read topic content
- Watch videos and open PDFs/links
- Practice topic-wise questions
- Mark questions for review
- Attempt mock tests
- Save responses during mock tests
- Submit mock tests
- View test results and leaderboard
- Report incorrect/inappropriate questions
- Report an organization if required
- Use AI tutor and AI explanations if enabled
- Generate or follow study plans
- Submit assignments
- View transactions
- Join live classes
- Use forum discussions
- Read and reply to notifications

### Student Learning Flow

1. Log in as Student.
2. Open dashboard.
3. Go to **My Exams** or **Browse Exams**.
4. Select an exam.
5. Open subjects.
6. Open topics.
7. Study the topic content.
8. Practice questions.
9. Attempt mock tests.
10. View result and identify weak areas.
11. Use study plan or AI tutor for improvement.

### Example: Practicing A Topic

1. Go to `/student/my-exams`.
2. Select an exam.
3. Select a subject.
4. Select a topic.
5. Click practice/questions.
6. Attempt questions one by one.
7. Review answer feedback.
8. Mark difficult questions for review.
9. Later open `/student/my-review-list` for revision.

### Example: Taking A Mock Test

1. Go to `/student/mock-tests`.
2. Select an available test.
3. Start or resume the attempt.
4. Answer questions within the time limit.
5. Submit the test.
6. View result page.
7. Check score, correct answers, wrong answers, and feedback.
8. Use the leaderboard if enabled.

---

## 9. Public User Guide

Users who are not logged in can still access public parts of the website.

### Public Pages

| Page | URL | Purpose |
|---|---|---|
| Home | `/` | Landing/home page |
| Register | `/register` | Student or organization registration |
| Login | `/login` | User login |
| Browse Exams | `/browse-exams` | Search public exams |
| Pricing | `/pricing` | View plans/pricing |
| About | `/about` | About the platform/organization |
| Contact | `/contact` | Contact form |
| FAQ | `/faq` | Frequently asked questions |
| Terms | `/terms` | Terms of service |
| Privacy | `/privacy` | Privacy policy |

### Public Registration

Students can register from `/register`.

Organization registration can also be started from `/register`, depending on plan/payment setup.

---

## 10. Core LMS Modules

### Exams

An exam is the highest academic container. Examples:

- GATE CSE
- JEE Physics
- Data Structures
- Python Programming
- Semester 1 Mathematics

Admins create exams and attach subjects, topics, content, questions, and mock tests to them.

### Subjects

A subject belongs to an exam. Example:

Exam: `GATE CSE`  
Subjects: `Algorithms`, `Operating Systems`, `DBMS`

### Topics

A topic belongs to a subject. Example:

Subject: `Algorithms`  
Topics: `Sorting`, `Graphs`, `Dynamic Programming`

### Topic Content

Topic content may include:

- Text notes
- Images
- PDFs
- Videos
- External links

### Questions

Questions are used for practice and mock tests.

Supported question style includes:

- MCQ questions
- Open-ended questions
- Comprehension/passage-based questions
- Questions with explanations
- Questions with difficulty levels

### Mock Tests

Mock tests allow students to attempt a full test with timing, scoring, and result analysis.

### Assignments

Admins/faculty can create assignments. Students can submit them. Admins can grade submissions.

### Study Plan

The study plan helps students organize learning tasks. Admins can create organization-level study plans, and AI-assisted plans may be available depending on subscription.

### Live Classes

Admins can schedule live classes. Students can view class schedule and join classes.

### Notifications

Notifications support announcements, direct messages, replies, and read/unread status.

### Forum

The forum allows students/admins inside an organization to discuss topics, ask questions, and reply to posts.

### AI Features

AI features may include:

- AI tutor chat
- AI question generation
- AI answer validation
- AI question explanations
- AI current affairs content
- AI study insights
- AI grading support

AI features may require separate premium subscription or organization-level AI access.

---

## 11. Organization Settings And Branding

The Main Co-Admin can configure organization-level branding from:

```text
/organization/settings
```

Possible settings:

- Organization logo
- Login image
- Register image
- Favicon
- Contact email
- Footer text
- Social links
- Terms of service content
- Privacy policy content
- About page content
- Contact page data
- FAQ data
- Class creation settings
- Default class duration

This helps each institute have a customized LMS experience.

---

## 12. Payments And Subscriptions

The platform supports Razorpay-based payments.

### Payment Use Cases

- Organization subscription
- Student exam purchase
- Student AI tutor subscription
- Organization AI assistant subscription

### Student Transactions

Students can view their transaction history at:

```text
/student/transactions
```

### Important Note

Payment credentials, Razorpay plan IDs, and webhook secrets are configured by the developer/admin in the backend environment. Normal users do not need to handle this.

---

## 13. Notifications And Communication

Users can view notifications at:

```text
/my-notifications
```

Notification features:

- View unread notifications
- Mark notifications as read
- Receive direct messages
- Reply to notification threads
- Receive broadcast announcements
- Tag users where supported

Admins can send notifications to students or organization users.

---

## 14. Common First-Time Questions

### Q1. Is this an ERP?

No. This is mainly an LMS. It focuses on learning content, practice, tests, assignments, live classes, AI support, and analytics.

### Q2. Do students need roll numbers?

No. Roll numbers are not required for the LMS. Institutes that already use ERP can keep roll numbers in ERP. In this LMS, students can be managed using email, name, organization membership, and exam enrollment.

### Q3. Can students belong to multiple organizations?

Yes, a student can have organization memberships. The system can show the student's organizations and exams.

### Q4. Can an institute have its own branded pages?

Yes. The organization can configure logo, public pages, FAQ, contact details, and images.

### Q5. Can admins upload content?

Yes. Admins can upload or add content such as text, images, PDFs, videos, and links.

### Q6. Can students buy exams?

Yes, if paid exams are enabled and Razorpay is configured.

### Q7. Can students take mock tests?

Yes. Students can start, save responses, submit tests, and view results.

### Q8. Can the platform create AI questions?

Yes, AI-assisted question generation exists, depending on AI configuration and subscription access.

### Q9. Can students ask AI doubts?

Yes, students can use AI chat/tutor features if enabled.

### Q10. Can admins see student performance?

Yes. Admin dashboards and learning intelligence pages provide performance-related insights.

---

## 15. Beginner Navigation Tips

- Use **Dashboard** as the starting point after login.
- Use **My Exams** if you are a student.
- Use **Exams** if you are an admin/faculty.
- Content is arranged in this order: `Exam -> Subject -> Topic -> Content/Questions`.
- Mock tests are separate from topic practice.
- Assignments are separate from mock tests.
- Use the notification bell or `/my-notifications` to check messages.
- Use Profile to update personal information or change password.
- Use Logout after finishing work.

---

## 16. Recommended Demo Script For MGIT

### Part 1: Public Website

1. Open home page.
2. Show register and login.
3. Show browse exams.
4. Show pricing/contact/FAQ pages.

### Part 2: Super Admin

1. Log in as Super Admin.
2. Show platform dashboard.
3. Show organizations/users.
4. Show plans.
5. Show approval queue.
6. Show archived content and reports.

### Part 3: Institute Admin

1. Log in as Main Co-Admin.
2. Show organization dashboard.
3. Create or open an exam.
4. Open subjects.
5. Open topics.
6. Open content editor.
7. Open question management.
8. Open mock tests.
9. Open assignments.
10. Open organization settings.

### Part 4: Student

1. Log in as Student.
2. Show student dashboard.
3. Open My Exams.
4. Open subjects and topics.
5. View content.
6. Practice questions.
7. Attempt a mock test.
8. View result.
9. Open study plan.
10. Open AI tutor.
11. Open assignments and notifications.

---

## 17. What To Tell A New User In One Paragraph

DIA LMS is a learning platform where admins create exams, subjects, topics, study material, questions, mock tests, assignments, and live classes. Students log in to study content, practice questions, attempt mock tests, view results, follow study plans, submit assignments, and use AI learning tools. Super Admin manages the entire platform, Main Co-Admin manages one institute, Co-Admin helps with academic content and grading, and Students use the learning features.

---

## 18. Final Notes

- This document is written for first-time users and demo reviewers.
- Replace the placeholder login credentials before sharing.
- Keep ERP-related details separate because this platform is best presented as a pure LMS.
- The strongest features to highlight are: multi-tenant organization support, exam/topic structure, mock tests, AI learning tools, assignments, live classes, analytics, and organization branding.
