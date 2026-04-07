import { Link, useLocation } from "react-router-dom";

export function MobileMenu({ isOpen, onClose, navItems }) {
  const location = useLocation();
  const currentPath = location.pathname;

  if (!isOpen) return null;

  return (
    <>
      <div className="fixed inset-0 bg-black/50 z-40" onClick={onClose} />
      <div className="fixed top-0 right-0 h-full w-72 bg-surface dark:bg-surface-dark z-50 shadow-xl flex flex-col animate-in slide-in-from-right duration-200">
        <div className="flex items-center justify-between p-4 border-b border-outline dark:border-outline/20">
          <div className="flex items-center gap-2">
            <div className="bg-primary/10 rounded-lg p-1.5 text-primary">
              <span
                className="material-symbols-outlined"
                style={{ fontSize: "20px" }}
              >
                movie_edit
              </span>
            </div>
            <h2 className="font-bold text-text-main dark:text-white">Menu</h2>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-text-muted hover:text-text-main dark:hover:text-white"
          >
            <span className="material-symbols-outlined">close</span>
          </button>
        </div>

        <nav className="flex-1 p-4 space-y-1">
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
                  onClick={onClose}
                  className={`flex items-center gap-3 px-3 py-3 rounded-lg font-medium transition-colors ${
                    isActive
                      ? "bg-primary/10 text-primary"
                      : "text-text-muted hover:bg-outline/30 dark:hover:bg-surface-dark/80 hover:text-text-main dark:hover:text-white"
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
            <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-primary to-accent" />
            <div className="flex-1 overflow-hidden">
              <p className="text-sm font-medium text-text-main dark:text-white truncate">
                Criador Pro
              </p>
              <p className="text-xs text-text-muted truncate">Plano Ativo</p>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
