import { route } from './router';

export function createServer(): string {
  return route('/health');
}
