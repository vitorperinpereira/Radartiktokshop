import { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { MobileMenu } from "./MobileMenu";

const navItems = [
  { name: "Radar Semanal", path: "/", icon: "radar" },
  {
    name: "Raio-X do Produto",
    path: "/product",
    icon: "document_scanner",
    hideFromMenu: true,
  },
  { name: "Laboratorio de Angulos", path: "/ideas", icon: "science" },
  { name: "Historico", path: "/history", icon: "history" },
  { name: "Minha Garagem", path: "/garage", icon: "warehouse" },
];

export function AppShell({ children }) {
  const location = useLocation();
  const currentPath = location.pathname;
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <div className="bg-background-light dark:bg-background-dark text-text-main font-display antialiased min-h-screen flex">
      {/* Sidebar (Desktop) */}
      <aside className="hidden md:flex flex-col w-64 h-screen sticky top-0 bg-surface border-r border-outline dark:border-outline/20 dark:bg-surface-dark flex-shrink-0 z-10">
        <div className="p-6 flex items-center gap-3">
          <div className="bg-primary/10 rounded-xl p-2 text-primary flex items-center justify-center">
            <span
              className="material-symbols-outlined"
              style={{ fontSize: "24px" }}
            >
              movie_edit
            </span>
          </div>
          <div>
            <h1 className="text-text-main dark:text-white text-base font-bold leading-tight tracking-tight">
              Estudio do Criador
            </h1>
          </div>
        </div>

        <nav className="flex-1 px-4 py-4 space-y-2">
          {navItems
            .filter(
              (item) => !item.hideFromMenu || currentPath.startsWith(item.path),
            )
            .map((item) => {
              const isActive =
                item.path === "/"
                  ? currentPath === "/"
                  : currentPath.startsWith(item.path);
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center gap-3 px-3 py-2.5 rounded-lg font-medium transition-colors ${
                    isActive
                      ? "bg-primary/10 text-primary"
                      : "text-muted hover:bg-outline/30 dark:hover:bg-surface-dark/80 hover:text-text-main dark:hover:text-white"
                  }`}
                >
                  <span className="material-symbols-outlined">{item.icon}</span>
                  <span>{item.name}</span>
                </Link>
              );
            })}
        </nav>

        <div className="p-4 border-t border-outline dark:border-outline/20">
          <div className="flex items-center gap-3 px-3 py-2">
            <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-primary to-accent"></div>
            <div className="flex-1 overflow-hidden">
              <p className="text-sm font-medium text-text-main dark:text-white truncate">
                Criador Pro
              </p>
              <p className="text-xs text-muted truncate">Plano Ativo</p>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col min-h-screen overflow-x-hidden relative w-full">
        {/* Mobile Header */}
        <header className="md:hidden flex items-center justify-between p-4 bg-surface dark:bg-surface-dark border-b border-outline dark:border-outline/20 sticky top-0 z-20">
          <div className="flex items-center gap-2">
            <div className="bg-primary/10 rounded-lg p-1.5 text-primary">
              <span
                className="material-symbols-outlined"
                style={{ fontSize: "20px" }}
              >
                movie_edit
              </span>
            </div>
            <h1 className="font-bold text-text-main dark:text-white">
              Estudio do Criador
            </h1>
          </div>
          <button
            onClick={() => setMobileMenuOpen(true)}
            className="text-text-main dark:text-white p-2"
          >
            <span className="material-symbols-outlined">menu</span>
          </button>
        </header>

        {children}
      </main>

      {/* Mobile Menu */}
      <MobileMenu
        isOpen={mobileMenuOpen}
        onClose={() => setMobileMenuOpen(false)}
        navItems={navItems}
      />
    </div>
  );
}
