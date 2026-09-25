/**
 * Shared API response types mirroring backend Pydantic schemas.
 *
 * These are hand-written from backend/app/schemas/ until `npm run gen:api`
 * can be run against a live backend. Do not hand-edit if generated types exist.
 */

// ---------------------------------------------------------------------------
// Pagination
// ---------------------------------------------------------------------------

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
}

// ---------------------------------------------------------------------------
// Media
// ---------------------------------------------------------------------------

export interface MediaResponse {
  id: number;
  url: string;
  width: number | null;
  height: number | null;
}

// ---------------------------------------------------------------------------
// Symptom Categories
// ---------------------------------------------------------------------------

export interface SymptomCategory {
  id: number;
  code: string;
  sort_order: number;
  label: string;
}

// ---------------------------------------------------------------------------
// Symptoms
// ---------------------------------------------------------------------------

export interface SymptomItem {
  id: number;
  code: string;
  label: string;
  is_environmental: boolean;
}

export interface CategoryGroupedSymptoms {
  category: SymptomCategory;
  symptoms: SymptomItem[];
}

// ---------------------------------------------------------------------------
// Disease
// ---------------------------------------------------------------------------

export type PathogenType = "fungal" | "bacterial" | "viral" | "abiotic" | "other";

export interface DiseaseListItem {
  id: number;
  slug: string;
  pathogen_type: PathogenType;
  is_published: boolean;
  image_url: string | null;
  name: string;
  description: string | null;
}

export type DiseaseListResponse = PaginatedResponse<DiseaseListItem>;

export interface DiseaseSymptomGroupedItem {
  symptom_id: number;
  code: string;
  label: string;
  weight: number;
  is_required: boolean;
  is_pathognomonic: boolean;
}

export interface DiseaseSymptomCategoryGroup {
  category: SymptomCategory;
  symptoms: DiseaseSymptomGroupedItem[];
}

export interface DiseaseDetail {
  id: number;
  slug: string;
  pathogen_type: PathogenType;
  is_published: boolean;
  image_url: string | null;
  name: string;
  description: string | null;
  cause: string | null;
  treatment: string | null;
  prevention: string | null;
  translations: Record<string, Record<string, string>>;
  symptom_groups: DiseaseSymptomCategoryGroup[];
}

// ---------------------------------------------------------------------------
// Diagnosis
// ---------------------------------------------------------------------------

export type Answer = "yes" | "no" | "unknown";
export type DiagnosisOutcome = "matched" | "no_match";

export interface DiagnosisRequest {
  locale: string;
  answers: Record<number, Answer>;
}

export interface DiseaseRef {
  id: number | null;
  slug: string;
  name: string;
}

export interface EvidenceSymptom {
  symptom: string;
  weight: number;
}

export interface Evidence {
  supporting: EvidenceSymptom[];
  against: EvidenceSymptom[];
  missing_key: EvidenceSymptom[];
}

export interface DiagnosisResult {
  rank: number;
  disease: DiseaseRef;
  score: number;
  confidence: number;
  evidence: Evidence;
}

export interface NextQuestion {
  symptom: string;
  information_gain: number;
}

export interface DiagnosisResponse {
  session_id: string | null;
  ruleset_version: string;
  outcome: DiagnosisOutcome;
  results: DiagnosisResult[];
  next_best_questions: NextQuestion[];
  feedback_prompt: string | null;
}

// ---------------------------------------------------------------------------
// Diagnosis Session History
// ---------------------------------------------------------------------------

export interface DiagnosisSessionSummary {
  id: string;
  created_at: string;
  locale: string;
  symptom_count: number;
  outcome: DiagnosisOutcome;
  top_disease: DiseaseRef | null;
  top_confidence: number | null;
}

export type DiagnosisSessionListResponse = PaginatedResponse<DiagnosisSessionSummary>;

export interface SelectedSymptom {
  symptom_id: number;
  symptom_code: string;
  answer: Answer;
}

export interface DiagnosisSessionDetail {
  session_id: string;
  ruleset_version: string;
  outcome: DiagnosisOutcome;
  locale: string;
  created_at: string;
  symptom_count: number;
  selected_symptoms: SelectedSymptom[];
  results: DiagnosisResult[];
  next_best_questions: NextQuestion[];
  feedback_prompt: string | null;
}

// ---------------------------------------------------------------------------
// Analytics
// ---------------------------------------------------------------------------

export interface DailyChecksTrend {
  date: string;
  count: number;
}

export interface TopSymptom {
  symptom_id: number;
  code: string;
  label: string;
  count: number;
}

export interface NoMatchPattern {
  symptoms: string[];
  count: number;
}

export interface AnalyticsOverview {
  checks_today: number;
  checks_total: number;
  checks_trend_30d: DailyChecksTrend[];
  top_symptoms: TopSymptom[];
  no_match_patterns: NoMatchPattern[];
  pending_feedback_count: number;
}

// ---------------------------------------------------------------------------
// Feedback
// ---------------------------------------------------------------------------

export type FeedbackStatus = "open" | "in_review" | "resolved";

export interface FeedbackItem {
  id: number;
  subject: string;
  message: string;
  status: FeedbackStatus;
  created_at: string;
  user_id: number | null;
  user_name: string | null;
  diagnosis_session_id: string | null;
  media_url: string | null;
}

export type FeedbackListResponse = PaginatedResponse<FeedbackItem>;

// ---------------------------------------------------------------------------
// Admin: Roles & Permissions
// ---------------------------------------------------------------------------

export interface PermissionItem {
  id: number;
  code: string;
  description: string | null;
}

export interface RoleItem {
  id: number;
  name: string;
  description: string | null;
  permissions: string[];
}

export interface RoleListResponse {
  items: RoleItem[];
  permissions: PermissionItem[];
}

// ---------------------------------------------------------------------------
// Admin: Users
// ---------------------------------------------------------------------------

export interface AdminUserItem {
  id: number;
  username: string;
  email: string;
  role: string;
  role_id: number;
  is_active: boolean;
  created_at: string;
}

export type AdminUserListResponse = PaginatedResponse<AdminUserItem>;

// ---------------------------------------------------------------------------
// Admin: Rulesets
// ---------------------------------------------------------------------------

export interface RulesetItem {
  id: number;
  version: string;
  algorithm: string;
  params: Record<string, unknown>;
  is_active: boolean;
  published_at: string | null;
  published_by: string | null;
}

export interface RulesetListResponse {
  items: RulesetItem[];
}

export interface RulesetActivateResponse {
  id: number;
  version: string;
  is_active: boolean;
}
