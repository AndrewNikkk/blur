import { isAxiosError } from 'axios';

export function getApiErrorDetail(error: unknown): string | undefined {
  if (!isAxiosError(error)) return undefined;
  const data = error.response?.data;
  if (data && typeof data === 'object' && data !== null && 'detail' in data) {
    const detail = (data as { detail?: unknown }).detail;
    if (typeof detail === 'string') return detail;
  }
  return undefined;
}
