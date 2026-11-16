import type { Product, ProductCreatePayload, ProductSource, SourceText } from "@/types";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const API_PREFIX = "/api/v1";

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE_URL}${API_PREFIX}${path}`, {
    ...init,
    headers: {
      "content-type": "application/json",
      ...(init?.headers ?? {}),
    },
  });

  if (!response.ok) {
    const detail = await response.text().catch(() => "");
    throw new ApiError(response.status, detail || `请求失败（${response.status}）`);
  }
  if (response.status === 204) return undefined as T;
  return (await response.json()) as T;
}

export const productApi = {
  list: () => request<Product[]>("/products"),
  get: (id: string) => request<Product>(`/products/${id}`),
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
};

export async function uploadProductSource(
  productId: string,
  file: File,
): Promise<ProductSource> {
  const form = new FormData();
  form.append("file", file);
  const response = await fetch(
    `${BASE_URL}${API_PREFIX}/products/${productId}/sources`,
    { method: "POST", body: form },
  );
  if (!response.ok) {
    const detail = await response.text().catch(() => "");
    throw new ApiError(response.status, detail || "上传失败");
  }
  return (await response.json()) as ProductSource;
}

export function getSourceText(id: string) {
  return request<SourceText>(`/sources/${id}`);
}
