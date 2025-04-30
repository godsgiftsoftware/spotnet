import { Link } from "@tanstack/react-router";

const AdminNavigation = () => {
  return (
    <div className="bg-pageBg text-white p-4 border-b border-grayborder">
      <div className="container mx-auto">
        <div className="flex space-x-6">
          <Link 
            to="/admin/dashboard"
            className="text-navLinkColor hover:text-white transition-colors px-2 py-1"
            activeProps={{ className: "text-white font-semibold bg-gray-900 rounded-md" }}
          >
            Dashboard
          </Link>
          <Link 
            to="/admin/pools"
            className="text-navLinkColor hover:text-white transition-colors px-2 py-1"
            activeProps={{ className: "text-white font-semibold bg-gray-900 rounded-md" }}
          >
            Pools
          </Link>
        </div>
      </div>
    </div>
  );
};

export default AdminNavigation; 