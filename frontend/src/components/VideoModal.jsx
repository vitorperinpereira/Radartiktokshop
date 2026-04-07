import { useProductVideos } from "../hooks/useProductVideos";
import { formatNumber } from "../utils/formatters";

export function VideoModal({ productId, productName, isOpen, onClose }) {
  const { videos, loading, error } = useProductVideos(
    isOpen ? productId : null,
  );

  if (!isOpen) return null;

  return (
    <>
      <div className="fixed inset-0 bg-black/60 z-50" onClick={onClose} />
      <div className="fixed inset-4 md:inset-auto md:top-1/2 md:left-1/2 md:-translate-x-1/2 md:-translate-y-1/2 md:w-full md:max-w-2xl md:max-h-[80vh] bg-surface dark:bg-surface-dark rounded-xl shadow-xl z-50 flex flex-col overflow-hidden">
        <div className="flex items-center justify-between p-4 border-b border-outline dark:border-outline/20">
          <h3 className="font-bold text-text-main dark:text-white flex items-center gap-2">
            <span className="material-symbols-outlined text-primary">
              play_circle
            </span>
            Videos - {productName}
          </h3>
          <button
            onClick={onClose}
            className="p-2 text-text-muted hover:text-text-main dark:hover:text-white"
          >
            <span className="material-symbols-outlined">close</span>
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4">
          {loading ? (
            <div className="flex items-center justify-center h-48">
              <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-primary" />
            </div>
          ) : error ? (
            <div className="text-center text-danger p-8">
              <span className="material-symbols-outlined text-3xl mb-2 block">
                error
              </span>
              <p className="text-sm">{error}</p>
            </div>
          ) : videos.length === 0 ? (
            <div className="text-center text-text-muted p-8">
              <span className="material-symbols-outlined text-4xl mb-3 block">
                videocam_off
              </span>
              <p className="font-medium mb-2">Nenhum video encontrado</p>
              <p className="text-sm mb-4">
                Os dados de video ainda nao estao disponiveis para este produto.
              </p>
              <a
                href={`https://www.tiktok.com/search?q=${encodeURIComponent(productName || "")}`}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-4 py-2 bg-primary/10 text-primary rounded-lg font-medium text-sm hover:bg-primary/20 transition-colors"
              >
                <span
                  className="material-symbols-outlined"
                  style={{ fontSize: "18px" }}
                >
                  open_in_new
                </span>
                Buscar no TikTok
              </a>
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-3">
              {videos.slice(0, 3).map((video, i) => (
                <a
                  key={i}
                  href={video.video_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-4 p-3 rounded-lg border border-outline dark:border-outline/20 hover:border-primary/30 hover:bg-primary/5 transition-colors group"
                >
                  <div className="w-20 h-20 rounded-lg bg-outline/30 dark:bg-surface-dark flex-shrink-0 overflow-hidden flex items-center justify-center">
                    {video.thumbnail_url ? (
                      <img
                        src={video.thumbnail_url}
                        alt=""
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <span className="material-symbols-outlined text-3xl text-muted">
                        smart_display
                      </span>
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-text-main dark:text-white truncate group-hover:text-primary transition-colors">
                      {video.title || `Video ${i + 1}`}
                    </p>
                    {video.views != null && (
                      <p className="text-sm text-text-muted mt-1">
                        <span
                          className="material-symbols-outlined align-middle"
                          style={{ fontSize: "14px" }}
                        >
                          visibility
                        </span>{" "}
                        {formatNumber(video.views)} views
                      </p>
                    )}
                  </div>
                  <span className="material-symbols-outlined text-text-muted group-hover:text-primary">
                    open_in_new
                  </span>
                </a>
              ))}
            </div>
          )}
        </div>
      </div>
    </>
  );
}
