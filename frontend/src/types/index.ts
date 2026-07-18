export interface User {
  id: string;
  email: string;
  full_name: string | null;
  avatar_url: string | null;
  auth_provider: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface Upload {
  id: string;
  filename: string;
  original_filename: string;
  content_type: string;
  size_bytes: number;
  page_count: number;
  status: string;
  storage_provider: string;
  error_message?: string | null;
  created_at: string;
}

export interface Lesson {
  id: string;
  chapter_id: string;
  title: string;
  content?: string | null;
  explanation?: string | null;
  examples?: string | null;
  important_notes?: string | null;
  summary?: string | null;
  key_takeaways?: string[] | null;
  estimated_minutes: number;
  order_index: number;
}

export interface Chapter {
  id: string;
  course_id: string;
  title: string;
  summary?: string | null;
  order_index: number;
  lessons: Lesson[];
}

export interface Course {
  id: string;
  user_id: string;
  upload_id: string;
  title: string;
  description?: string | null;
  difficulty: string;
  estimated_minutes: number;
  learning_objectives?: string[] | null;
  prerequisites?: string[] | null;
  tags?: string[] | null;
  status: string;
  created_at: string;
}

export interface CourseWithProgress extends Course {
  completion_percent: number;
  total_lessons: number;
  completed_lessons: number;
}

export interface CourseDetail extends Course {
  chapters: Chapter[];
}

export interface Source {
  content: string;
  page_number?: number | null;
  chunk_index?: number | null;
  score?: number | null;
}

export interface ChatMessage {
  id: string;
  session_id: string;
  role: "user" | "assistant" | "system";
  content: string;
  sources?: Source[] | null;
  created_at: string;
}

export interface ChatSession {
  id: string;
  course_id: string;
  title: string;
  created_at: string;
  messages?: ChatMessage[];
}

export interface QuizQuestion {
  id: string;
  question_type: "mcq" | "true_false" | "short_answer";
  question: string;
  options?: string[] | null;
  order_index: number;
}

export interface Quiz {
  id: string;
  course_id: string;
  chapter_id?: string | null;
  title: string;
  description?: string | null;
  difficulty: string;
  created_at: string;
  questions?: QuizQuestion[];
}

export interface GradedAnswer {
  question_id: string;
  question: string;
  submitted_answer: string;
  correct_answer: string;
  is_correct: boolean;
  explanation?: string | null;
}

export interface QuizAttemptResult {
  id: string;
  quiz_id: string;
  score: number;
  total_questions: number;
  correct_count: number;
  created_at: string;
  graded: GradedAnswer[];
}

export interface DashboardStats {
  total_courses: number;
  total_uploads: number;
  total_quiz_attempts: number;
  average_quiz_score: number;
  total_time_spent_minutes: number;
  learning_streak_days: number;
  recent_courses: CourseWithProgress[];
  quiz_scores: { quiz_id: string; quiz_title: string; score: number; created_at: string }[];
  activity: { day: string; minutes: number }[];
}

export interface SearchResultItem {
  type: string;
  id: string;
  title: string;
  snippet?: string | null;
  course_id?: string | null;
  score?: number | null;
}

export interface SearchResponse {
  query: string;
  keyword_results: SearchResultItem[];
  semantic_results: SearchResultItem[];
}
