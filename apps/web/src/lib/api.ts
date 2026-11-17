import type {
  Comparison,
  Competitor,
  Product,
  ProductAttribute,
  ProductCreatePayload,
  ComparisonDifference,
  ProductSource,
  Script,
  ScriptSection,
  ScriptSectionKind,
  ScriptVerification,
  SourceSegment,
  SourceText,
  VerificationIssue,
} from "@/types";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const API_PREFIX = "/api/v1";
let accessTokenProvider: () => Promise<string | null> = async () => null;

export function setAccessTokenProvider(provider: () => Promise<string | null>) {
  accessTokenProvider = provider;
}

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function errorFrom(response: Response): Promise<string> {
  const text = await response.text().catch(() => "");
  if (!text) return `请求失败（${response.status}）`;
  try {
    const data = JSON.parse(text);
    if (typeof data.detail === "string") return data.detail;
    if (Array.isArray(data.detail) && data.detail[0]?.msg) {
      return String(data.detail[0].msg);
    }
  } catch {
    /* not JSON */
  }
  return text;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const token = await accessTokenProvider();
  const response = await fetch(`${BASE_URL}${API_PREFIX}${path}`, {
    ...init,
    headers: {
      "content-type": "application/json",
      ...(token ? { authorization: `Bearer ${token}` } : {}),
      ...(init?.headers ?? {}),
    },
  });

  if (!response.ok) {
    throw new ApiError(response.status, await errorFrom(response));
  }
  if (response.status === 204) return undefined as T;
  return (await response.json()) as T;
}

type RawProduct = {
  id: string;
  workspace_id?: string | null;
  name: string;
  category: string;
  summary: string;
  price?: number | null;
  currency: string;
  status: string;
  sources: RawProductSource[];
  attributes: RawProductAttribute[];
  created_at: string;
  updated_at: string;
};

type RawProductSource = {
  id: string;
  type: "pdf" | "image" | "url" | "manual";
  name: string;
  reference?: string | null;
  status: string;
  page_count?: number | null;
  content_hash?: string | null;
  parser?: string | null;
  sufficiency?: string;
  run_id?: string | null;
  created_at: string;
};

type RawProductAttribute = {
  id: string;
  label: string;
  value: string;
  status: "unconfirmed" | "confirmed" | "doubtful";
  origin?: string;
  source_id?: string | null;
  source_reference?: string | null;
};

function mapProduct(raw: RawProduct): Product {
  return {
    id: raw.id,
    name: raw.name,
    category: raw.category,
    summary: raw.summary,
    price: raw.price ?? undefined,
    currency: raw.currency,
    status: raw.status as Product["status"],
    createdAt: raw.created_at,
    updatedAt: raw.updated_at,
    sources: raw.sources.map((source) => ({
      id: source.id,
      type: source.type,
      name: source.name,
      reference: source.reference ?? undefined,
      status: source.status as "ready" | "processing" | "failed",
      page_count: source.page_count ?? null,
      contentHash: source.content_hash ?? null,
      parser: source.parser ?? null,
      sufficiency: source.sufficiency ?? "sufficient",
      runId: source.run_id ?? null,
      createdAt: source.created_at,
    })),
    attributes: raw.attributes.map((attribute) => ({
      id: attribute.id,
      label: attribute.label,
      value: attribute.value,
      status: attribute.status,
      origin: attribute.origin ?? "manual",
      sourceId: attribute.source_id ?? undefined,
      sourceReference: attribute.source_reference ?? undefined,
    })),
  };
}

export const productApi = {
  list: async () => (await request<RawProduct[]>("/products")).map(mapProduct),
  get: async (id: string) =>
    mapProduct(await request<RawProduct>(`/products/${id}`)),
  create: (payload: ProductCreatePayload) =>
    request<Product>("/products", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  update: (id: string, payload: Partial<ProductCreatePayload>) =>
    request<Product>(`/products/${id}`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    }),
  remove: (id: string) => request<void>(`/products/${id}`, { method: "DELETE" }),
  extract: (id: string) =>
    request<Product>(`/products/${id}/extract`, { method: "POST" }),
  createUrlSource: (id: string, url: string) =>
    request<ProductSource>(`/products/${id}/sources/url`, {
      method: "POST",
      body: JSON.stringify({ url }),
    }),
  previewUrl: (url: string) =>
    request<{ url: string; name: string; category: string; summary: string; price?: number | null }>(
      "/sources/url/preview",
      { method: "POST", body: JSON.stringify({ url }) },
    ),
  addAttribute: (id: string, payload: { label: string; value: string }) =>
    request<ProductAttribute>(`/products/${id}/attributes`, {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  deleteAttribute: (id: string) =>
    request<void>(`/attributes/${id}`, { method: "DELETE" }),
};

export async function uploadProductSource(
  productId: string,
  file: File,
): Promise<ProductSource> {
  const form = new FormData();
  form.append("file", file);
  const token = await accessTokenProvider();
  const response = await fetch(
    `${BASE_URL}${API_PREFIX}/products/${productId}/sources`,
    { method: "POST", body: form, headers: token ? { authorization: `Bearer ${token}` } : undefined },
  );
  if (!response.ok) {
    throw new ApiError(response.status, await errorFrom(response));
  }
  return (await response.json()) as ProductSource;
}

export function getSourceText(id: string) {
  return request<SourceText>(`/sources/${id}`);
}

/* ---------- competitive analysis ---------- */

type RawCompetitor = {
  id: string;
  name: string;
  brand: string;
  price?: number | null;
  notes: string;
  created_at: string;
};

type RawDifference = {
  id: string;
  comparison_id: string;
  field: string;
  ours: string;
  theirs: string;
  evidence_type: "source" | "inferred" | "speculative";
  side: "ours" | "theirs" | "neutral";
  note?: string | null;
  source_reference?: string | null;
  created_at: string;
};

type RawComparison = {
  id: string;
  product_id: string;
  competitor_id: string;
  status: string;
  competitor: RawCompetitor;
  missing_info: string[];
  differences: RawDifference[];
  created_at: string;
  updated_at: string;
};

function mapCompetitor(raw: RawCompetitor): Competitor {
  return {
    id: raw.id,
    productName: raw.name,
    brand: raw.brand,
    price: raw.price ?? undefined,
    notes: raw.notes,
  };
}

function mapDifference(raw: RawDifference): ComparisonDifference {
  return {
    id: raw.id,
    field: raw.field,
    ours: raw.ours,
    theirs: raw.theirs,
    evidenceType: raw.evidence_type,
    side: raw.side,
    sourceReference: raw.source_reference ?? null,
  };
}

function mapComparison(raw: RawComparison): Comparison {
  return {
    id: raw.id,
    productId: raw.product_id,
    competitorId: raw.competitor_id,
    status: raw.status,
    competitor: mapCompetitor(raw.competitor),
    differences: raw.differences.map(mapDifference),
    missingInfo: raw.missing_info ?? [],
    createdAt: raw.created_at,
    updatedAt: raw.updated_at,
  };
}

export const competitorApi = {
  list: async () =>
    (await request<RawCompetitor[]>("/competitors")).map(mapCompetitor),
  create: async (payload: { name: string; brand?: string; price?: number; notes?: string; material?: string }) =>
    mapCompetitor(
      await request<RawCompetitor>("/competitors", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    ),
  remove: (id: string) => request<void>(`/competitors/${id}`, { method: "DELETE" }),
};

export const comparisonApi = {
  listAll: async () =>
    (await request<RawComparison[]>("/comparisons")).map(mapComparison),
  listForProduct: async (productId: string) =>
    (await request<RawComparison[]>(`/products/${productId}/comparisons`)).map(
      mapComparison,
    ),
  create: (productId: string, competitorId: string) =>
    request<RawComparison>("/comparisons", {
      method: "POST",
      body: JSON.stringify({ product_id: productId, competitor_id: competitorId }),
    }).then(mapComparison),
  addDifference: (
    comparisonId: string,
    payload: { field: string; ours?: string; theirs?: string; evidence_type?: string; side?: string },
  ) =>
    request<RawDifference>(`/comparisons/${comparisonId}/differences`, {
      method: "POST",
      body: JSON.stringify(payload),
    }).then(mapDifference),
  removeDifference: (differenceId: string) =>
    request<void>(`/comparisons/differences/${differenceId}`, { method: "DELETE" }),
  generate: async (id: string) =>
    mapComparison(
      await request<RawComparison>(`/comparisons/${id}/generate`, { method: "POST" }),
    ),
  remove: (id: string) => request<void>(`/comparisons/${id}`, { method: "DELETE" }),
};

/* ---------- scripts ---------- */

type RawSection = {
  id: string;
  script_id: string;
  kind: ScriptSectionKind;
  title: string;
  content: string;
  position: number;
  origin: string;
};

type RawScript = {
  id: string;
  series_id: string;
  product_id: string;
  comparison_id?: string | null;
  version: number;
  title: string;
  scenario: string;
  audience: string;
  style: string;
  status: string;
  verification_status?: string;
  sections: RawSection[];
  created_at: string;
  updated_at: string;
};

function mapSection(raw: RawSection): ScriptSection {
  return {
    id: raw.id,
    scriptId: raw.script_id,
    kind: raw.kind,
    title: raw.title,
    content: raw.content,
    position: raw.position,
    origin: raw.origin,
  };
}

function mapScript(raw: RawScript): Script {
  return {
    id: raw.id,
    seriesId: raw.series_id,
    productId: raw.product_id,
    comparisonId: raw.comparison_id ?? null,
    version: raw.version,
    title: raw.title,
    scenario: raw.scenario,
    audience: raw.audience,
    style: raw.style,
    status: raw.status as Script["status"],
    verificationStatus: raw.verification_status ?? "unverified",
    sections: raw.sections.map(mapSection),
    createdAt: raw.created_at,
    updatedAt: raw.updated_at,
  };
}

export const scriptApi = {
  list: async () => (await request<RawScript[]>("/scripts")).map(mapScript),
  get: async (id: string) =>
    mapScript(await request<RawScript>(`/scripts/${id}`)),
  versions: async (id: string) =>
    (await request<RawScript[]>(`/scripts/${id}/versions`)).map(mapScript),
  generate: async (
    productId: string,
    payload: { title?: string; scenario?: string; audience?: string; style?: string; comparison_id?: string },
  ) =>
    mapScript(
      await request<RawScript>(`/products/${productId}/scripts/generate`, {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    ),
  saveVersion: async (
    id: string,
    payload: { title?: string; sections: { kind: ScriptSectionKind; title: string; content: string }[] },
  ) =>
    mapScript(
      await request<RawScript>(`/scripts/${id}/versions`, {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    ),
  rewriteSection: async (scriptId: string, sectionId: string, instruction?: string) =>
    request<{ content: string }>(
      `/scripts/${scriptId}/sections/${sectionId}/rewrite`,
      {
        method: "POST",
        body: JSON.stringify({
          instruction: instruction ?? "更口语、更有感染力，但不得夸大或绝对化",
        }),
      },
    ),
  remove: (id: string) => request<void>(`/scripts/${id}`, { method: "DELETE" }),
};

/* ---------- verification ---------- */

type RawIssue = {
  id: string;
  verification_id: string;
  section_id?: string | null;
  type: VerificationIssue["type"];
  severity: VerificationIssue["severity"];
  message: string;
  quote?: string | null;
  suggestion?: string | null;
  origin: string;
};

type RawVerification = {
  id: string;
  script_id: string;
  status: "unverified" | "pass" | "issue";
  summary: string;
  issues: RawIssue[];
  created_at: string;
};

function mapIssue(raw: RawIssue): VerificationIssue {
  return {
    id: raw.id,
    verificationId: raw.verification_id,
    sectionId: raw.section_id ?? null,
    type: raw.type,
    severity: raw.severity,
    message: raw.message,
    quote: raw.quote ?? null,
    suggestion: raw.suggestion ?? null,
    origin: raw.origin,
  };
}

function mapVerification(raw: RawVerification): ScriptVerification {
  return {
    id: raw.id,
    scriptId: raw.script_id,
    status: raw.status,
    summary: raw.summary,
    issues: raw.issues.map(mapIssue),
    createdAt: raw.created_at,
  };
}

export const verificationApi = {
  verify: async (scriptId: string) =>
    mapVerification(
      await request<RawVerification>(`/scripts/${scriptId}/verify`, { method: "POST" }),
    ),
  list: async (scriptId: string) =>
    (await request<RawVerification[]>(`/scripts/${scriptId}/verifications`)).map(
      mapVerification,
    ),
};

export interface AuthUser {
  id: string;
  workspace_id: string;
  email: string;
  name: string;
  created_at: string;
}

export const authApi = {
  register: async (payload: { email: string; password: string; name?: string }) => {
    const data = await request<{ token: string; user: AuthUser }>("/auth/register", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    return data;
  },
  login: async (payload: { email: string; password: string }) => {
    const data = await request<{ token: string; user: AuthUser }>("/auth/login", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    return data;
  },
  me: () => request<AuthUser>("/auth/me"),
};

export const sourceApi = {
  segments: (id: string) =>
    request<SourceSegment[]>(`/sources/${id}/segments`),
};
