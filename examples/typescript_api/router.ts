import { healthy } from './health';

export function route(path: string): string {
  return path === '/health' && healthy() ? 'ok' : 'missing';
}
