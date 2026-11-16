/**
 * Front-end data contracts.
 *
 * These types mirror the future API / database schema (P2+). Keep field names
 * stable so mock data in P1 becomes real data without a rewrite.
 */

export type ID = string;

/** Whether an AI-extracted value is backed by source material. */
export type ConfirmationStatus = "unconfirmed" | "confirmed" | "doubtful";

/** How an advantage or claim is supported. */
export type EvidenceType = "source" | "inferred" | "speculative";

export type ProductSourceType = "pdf" | "image" | "url" | "manual";

export type ProductStatus = "draft" | "ready" | "archived";

export interface ProductSource {
  id: ID;
  type: ProductSourceType;
  name: string;
  /** Page or fragment reference for traceability. */
  reference?: string;
  /** Number of pages, when extracted. */
  page_count?: number | null;
  status: "ready" | "processing" | "failed";
  createdAt: string;
}

export interface ProductAttribute {
  id: ID;
  label: string;
  value: string;
  status: ConfirmationStatus;
  origin?: string;
  /** Source this attribute was extracted from, if any. */
  sourceId?: ID;
  sourceReference?: string | null;
}

export interface Product {
  id: ID;
  name: string;
  category: string;
  summary: string;
  price?: number;
  currency?: string;
  attributes: ProductAttribute[];
  sources: ProductSource[];
  status: ProductStatus;
  createdAt: string;
  updatedAt: string;
}

export interface Competitor {
  id: ID;
  productName: string;
  brand: string;
  price?: number;
  notes?: string;
  material?: string;
}

export type AdvantageSide = "ours" | "theirs" | "neutral";

export interface ComparisonDifference {
  id: ID;
  field: string;
  ours: string;
  theirs: string;
  evidenceType: EvidenceType;
  side: AdvantageSide;
  origin?: string;
  sourceReference?: string | null;
}

export interface Comparison {
  id: ID;
  productId: ID;
  competitorId: ID;
  status: string;
  competitor?: Competitor;
  differences: ComparisonDifference[];
  missingInfo: string[];
  createdAt: string;
  updatedAt?: string;
}

export type ScriptSectionKind =
  | "opening"
  | "intro"
  | "selling_points"
  | "differentiation"
  | "interaction"
  | "closing"
  | "risk";

export interface ScriptSection {
  id: ID;
  scriptId: ID;
  kind: ScriptSectionKind;
  title: string;
  content: string;
  position: number;
  origin: string;
}

export type ScriptStatus = "draft" | "verified" | "issue";

export interface Script {
  id: ID;
  seriesId: ID;
  productId: ID;
  comparisonId?: ID | null;
  title: string;
  scenario: string;
  audience: string;
  style: string;
  sections: ScriptSection[];
  version: number;
  status: ScriptStatus;
  createdAt: string;
  updatedAt: string;
}

export type AssetKind = "analysis" | "script" | "source";

export interface Asset {
  id: ID;
  kind: AssetKind;
  name: string;
  productName: string;
  updatedAt: string;
}

export type TaskStatus = "pending" | "running" | "done" | "failed";

export interface Task {
  id: ID;
  name: string;
  status: TaskStatus;
  createdAt: string;
}

export interface Workspace {
  id: ID;
  name: string;
  plan: string;
}

export interface ProductCreatePayload {
  name: string;
  category?: string;
  summary?: string;
  price?: number;
  currency?: string;
}

export interface SourceText {
  id: ID;
  product_id: ID;
  name: string;
  reference?: string | null;
  page_count?: number | null;
  text: string;
  created_at?: string;
}
