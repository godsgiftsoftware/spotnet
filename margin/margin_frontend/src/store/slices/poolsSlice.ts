import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import { Pool, getPools } from "../../api/pools";

export interface PoolsState {
  loading: boolean;
  data: Pool[];
  totalCount: number;
  error: string | null;
  pageIndex: number;
  pageSize: number;
}

const initialState: PoolsState = {
  loading: false,
  data: [],
  totalCount: 0,
  error: null,
  pageIndex: 1,
  pageSize: 10,
};

export const fetchPools = createAsyncThunk(
  "pools/fetchPools",
  async ({ pageIndex, pageSize }: { pageIndex: number; pageSize: number }) => {
    const offset = (pageIndex - 1) * pageSize;
    const response = await getPools(pageSize, offset);
    return response;
  }
);

const poolsSlice = createSlice({
  name: "pools",
  initialState,
  reducers: {
    setPageIndex: (state, action) => {
      state.pageIndex = action.payload;
    },
    setPageSize: (state, action) => {
      state.pageSize = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchPools.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchPools.fulfilled, (state, action) => {
        state.loading = false;
        state.data = action.payload.items;
        state.totalCount = action.payload.total;
      })
      .addCase(fetchPools.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || "Failed to fetch pools";
      });
  },
});

export const { setPageIndex, setPageSize } = poolsSlice.actions;

export default poolsSlice.reducer; 