import { Outlet } from "react-router-dom";

import Navigation from "./Navigation";
import RoleSelector from "./RoleSelector";

export default function Layout() {
  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="brand">
          <span className="brand-mark">Д</span>
          <div>
            <div className="brand-title">Учет деталей</div>
            <div className="brand-caption">Склад предприятия</div>
          </div>
        </div>
        <div className="header-tools">
          <Navigation />
          <RoleSelector />
        </div>
      </header>
      <main className="app-main">
        <Outlet />
      </main>
    </div>
  );
}
