import { api } from "./api";

export interface Pool {
  id: string;
  token: string;
  risk_status: string;
  amount?: string | null;
}

export interface PoolListResponse {
  items: Pool[];
  total: number;
}

export const getPools = async (limit = 25, offset = 0) => {
  const response = await api.get(`pool/pools?limit=${limit}&offset=${offset}`);
  return response.json<PoolListResponse>();
}; 