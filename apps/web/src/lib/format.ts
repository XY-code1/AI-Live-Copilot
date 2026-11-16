export function formatDate(input: string): string {
  const date = new Date(input);
  if (Number.isNaN(date.getTime())) return input;
  return new Intl.DateTimeFormat("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(date);
}

export function formatPrice(value: number, currency = "CNY"): string {
  const symbol = currency === "CNY" ? "¥" : currency;
  return `${symbol}${value.toLocaleString("zh-CN")}`;
}
