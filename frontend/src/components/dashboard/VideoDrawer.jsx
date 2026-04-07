import { useEffect, useState } from "react";
import VideoFeed from "../VideoFeed";

export function VideoDrawer({
  productId,
  productName,
  keyword,
  isOpen,
  onClose,
}) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setMounted(true);
    } else {
      const timer = setTimeout(() => setMounted(false), 350);
      return () => clearTimeout(timer);
    }
  }, [isOpen]);

  return (
    <div
      className={`overflow-hidden transition-all duration-300 ease-in-out bg-gray-900 ${isOpen ? "max-h-[800px] border-t border-gray-800" : "max-h-0"}`}
    >
      {mounted && (
        <div className="p-4 md:p-6 relative">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-base font-semibold text-white flex items-center gap-2">
              <span className="material-symbols-outlined text-primary">
                smart_display
              </span>
              Top Videos que estao vendendo
              <span className="text-primary">· {productName}</span>
            </h3>
            <button
              onClick={onClose}
              className="p-1 text-muted hover:text-white transition-colors"
              title="Fechar videos"
            >
              <span className="material-symbols-outlined">close</span>
            </button>
          </div>
          <div className="min-h-[200px]">
            <VideoFeed productId={productId} keyword={keyword || productName} />
          </div>
        </div>
      )}
    </div>
  );
}
