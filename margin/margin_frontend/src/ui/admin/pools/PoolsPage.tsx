import { useEffect } from "react";
import { useAppDispatch, useAppSelector } from "../../../store/hooks";
import { fetchPools, setPageIndex, setPageSize } from "../../../store/slices/poolsSlice";
import Table from "../../components/Table";
import Card from "../../components/Card";
import Badge from "../../components/Badge";
import Pagination from "../../components/Pagination";
import AdminLayout from "../AdminLayout";

const getRiskBadgeColor = (status: string) => {
  switch (status.toLowerCase()) {
    case "low":
      return "green";
    case "medium":
      return "yellow";
    case "high":
      return "red";
    default:
      return "gray";
  }
};

const PoolsPage = () => {
  const dispatch = useAppDispatch();
  const { data, loading, totalCount, pageIndex, pageSize } = useAppSelector((state) => state.pools);

  useEffect(() => {
    dispatch(fetchPools({ pageIndex, pageSize }));
  }, [dispatch, pageIndex, pageSize]);

  const handlePageChange = (page: number) => {
    dispatch(setPageIndex(page));
  };

  const handlePageSizeChange = (size: number) => {
    dispatch(setPageSize(size));
    dispatch(setPageIndex(1)); 
  };

  const columns = [
    {
      header: "Token",
      accessor: "token",
    },
    {
      header: "Risk Status",
      accessor: "risk_status",
      cell: (row: any) => (
        <Badge color={getRiskBadgeColor(row.risk_status)}>{row.risk_status}</Badge>
      ),
    },
    {
      header: "Amount",
      accessor: "amount",
      cell: (row: any) => (row.amount ? row.amount : "-"),
    },
  ];

  return (
    <AdminLayout>
      <div className="container mx-auto p-4 bg-pageBg">
        <h1 className="text-2xl font-bold mb-6 text-white">Pools Management</h1>
        <Card className="overflow-hidden">
          <div className="p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold text-white">All Pools</h2>
            </div>
            <Table
              data={data}
              columns={columns}
              loading={loading}
            />
            <div className="mt-6 flex justify-between items-center">
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-400">Show</span>
                <select
                  className="bg-black border border-grayborder text-gray-300 rounded-md px-2 py-1 text-sm"
                  value={pageSize}
                  onChange={(e) => handlePageSizeChange(Number(e.target.value))}
                >
                  <option value="10">10</option>
                  <option value="25">25</option>
                  <option value="50">50</option>
                </select>
                <span className="text-sm text-gray-400">entries</span>
              </div>
              <Pagination
                currentPage={pageIndex}
                totalItems={totalCount}
                pageSize={pageSize}
                onPageChange={handlePageChange}
              />
            </div>
          </div>
        </Card>
      </div>
    </AdminLayout>
  );
};

export default PoolsPage; 