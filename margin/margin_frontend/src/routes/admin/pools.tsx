import { createFileRoute } from '@tanstack/react-router';
import PoolsPage from '../../ui/admin/pools/PoolsPage';

export const Route = createFileRoute('/admin/pools')({
  component: PoolsPage,
}); 