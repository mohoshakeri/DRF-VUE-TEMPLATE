export function normalizeDigits(value: string): string {
  const persianDigits = "۰۱۲۳۴۵۶۷۸۹";
  const arabicDigits = "٠١٢٣٤٥٦٧٨٩";
  return value.replace(/[۰-۹٠-٩]/g, (digit) => {
    const persianIndex = persianDigits.indexOf(digit);
    if (persianIndex >= 0) {
      return String(persianIndex);
    }
    return String(arabicDigits.indexOf(digit));
  });
}

export function formatNumber(value: number | string): string {
  const normalized = Number(normalizeDigits(String(value || 0)));
  return normalized.toLocaleString("en-US");
}
