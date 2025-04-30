import React from "react";
import AdminNavigation from "./AdminNavigation";

interface AdminLayoutProps {
  children: React.ReactNode;
}

const AdminLayout: React.FC<AdminLayoutProps> = ({ children }) => {
  return (
    <div className="min-h-screen bg-pageBg">
      <AdminNavigation />
      <div className="container mx-auto py-6">
        {children}
      </div>
    </div>
  );
};

export default AdminLayout; 