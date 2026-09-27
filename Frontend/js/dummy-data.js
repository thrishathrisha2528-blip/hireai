/* ============================================
   HireAI — Dummy Data (replace with real API calls later)
   ============================================ */

const DUMMY_USER = {
  name: "Priya Sharma",
  role: "HR Recruiter",
  company: "NovaTech Solutions",
};

const DUMMY_JOBS = [
  {
    id: "job1",
    title: "Frontend Developer (React)",
    department: "Engineering",
    postedOn: "2026-08-20",
    candidatesScreened: 24,
    status: "Active",
    skills: ["React", "JavaScript", "CSS", "REST APIs", "Git"],
  },
  {
    id: "job2",
    title: "Data Analyst",
    department: "Analytics",
    postedOn: "2026-08-18",
    candidatesScreened: 15,
    status: "Active",
    skills: ["SQL", "Python", "Power BI", "Excel", "Statistics"],
  },
  {
    id: "job3",
    title: "DevOps Engineer",
    department: "Infrastructure",
    postedOn: "2026-08-10",
    candidatesScreened: 9,
    status: "Closed",
    skills: ["AWS", "Docker", "Kubernetes", "CI/CD", "Linux"],
  },
];

const DUMMY_CANDIDATES = [
  {
    id: "c1",
    jobId: "job1",
    name: "Arjun Mehta",
    email: "arjun.mehta@example.com",
    matchScore: 92,
    skillsMatched: ["React", "JavaScript", "CSS", "Git"],
    skillsMissing: ["REST APIs"],
    experience: "3 years",
    status: "Shortlisted",
  },
  {
    id: "c2",
    jobId: "job1",
    name: "Sneha Iyer",
    email: "sneha.iyer@example.com",
    matchScore: 85,
    skillsMatched: ["React", "JavaScript", "REST APIs"],
    skillsMissing: ["CSS", "Git"],
    experience: "2 years",
    status: "Shortlisted",
  },
  {
    id: "c3",
    jobId: "job1",
    name: "Rahul Verma",
    email: "rahul.verma@example.com",
    matchScore: 67,
    skillsMatched: ["JavaScript", "Git"],
    skillsMissing: ["React", "CSS", "REST APIs"],
    experience: "1 year",
    status: "Under Review",
  },
  {
    id: "c4",
    jobId: "job1",
    name: "Divya Nair",
    email: "divya.nair@example.com",
    matchScore: 45,
    skillsMatched: ["CSS"],
    skillsMissing: ["React", "JavaScript", "REST APIs", "Git"],
    experience: "0.6 years",
    status: "Rejected",
  },
];

const DUMMY_INTERVIEW_QUESTIONS = [
  "Can you explain the difference between controlled and uncontrolled components in React?",
  "How would you optimize a React app that re-renders too often?",
  "Describe a time you integrated a REST API into a frontend project — what challenges did you face?",
  "What's your approach to writing reusable, maintainable CSS at scale?",
];

const DUMMY_RESUME_SUGGESTIONS = [
  "Add measurable outcomes to your project descriptions (e.g. 'reduced load time by 30%').",
  "Include REST API integration experience explicitly — it's a key requirement for this role.",
  "List version control tools (Git/GitHub) under a dedicated Skills section for easier scanning.",
];

const DUMMY_STATS = {
  totalJobs: DUMMY_JOBS.length,
  totalCandidates: DUMMY_CANDIDATES.length,
  shortlisted: DUMMY_CANDIDATES.filter(c => c.status === "Shortlisted").length,
  avgMatchScore: Math.round(
    DUMMY_CANDIDATES.reduce((sum, c) => sum + c.matchScore, 0) / DUMMY_CANDIDATES.length
  ),
};