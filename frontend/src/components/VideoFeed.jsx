import { useProductVideos } from "../hooks/useProductVideos";
import { formatNumber } from "../utils/formatters";

export default function VideoFeed({ productId, keyword }) {
  const { videos, loading, error } = useProductVideos(productId);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-48">
        <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-primary" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center text-red-400 p-6">
        <p className="text-sm">{error}</p>
      </div>
    );
  }

  if (videos.length === 0) {
    return (
      <div className="text-center text-muted p-6">
        <span className="material-symbols-outlined text-3xl mb-2 block">
          videocam_off
        </span>
        <p className="text-sm mb-3">
          Nenhum video encontrado{keyword ? ` para "${keyword}"` : ""}
        </p>
        <a
          href={`https://www.tiktok.com/search?q=${encodeURIComponent(keyword || "")}`}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1 text-sm text-primary hover:underline"
        >
          Buscar no TikTok{" "}
          <span
            className="material-symbols-outlined"
            style={{ fontSize: "14px" }}
          >
            open_in_new
          </span>
        </a>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
      {videos.slice(0, 6).map((video, i) => (
        <a
          key={i}
          href={video.video_url}
          target="_blank"
          rel="noopener noreferrer"
          className="block rounded-lg overflow-hidden border border-gray-700 hover:border-primary/50 transition-colors group"
        >
          <div className="aspect-video bg-gray-800 flex items-center justify-center relative">
            {video.thumbnail_url ? (
              <img
                src={`https://wsrv.nl/?url=${encodeURIComponent(video.thumbnail_url)}&default=${encodeURIComponent("https://placehold.co/320x180")}`}
                alt=""
                className="w-full h-full object-cover"
              />
            ) : (
              <span className="material-symbols-outlined text-4xl text-gray-600">
                smart_display
              </span>
            )}
            <div className="absolute inset-0 bg-black/30 opacity-0 group-hover:opacity-100 flex items-center justify-center transition-opacity">
              <span className="material-symbols-outlined text-white text-4xl">
                play_arrow
              </span>
            </div>
          </div>
          <div className="p-2 bg-gray-900">
            <p className="text-xs text-white truncate">
              {video.title || `Video ${i + 1}`}
            </p>
            {video.views != null && (
              <p className="text-xs text-muted mt-0.5">
                {formatNumber(video.views)} views
              </p>
            )}
          </div>
        </a>
      ))}
    </div>
  );
}
