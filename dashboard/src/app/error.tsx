"use client";

export default function Error({
  error,
  reset,
}: {
  error: Error;
  reset: () => void;
}) {
  return (
    <div className="flex flex-col items-center justify-center h-64 gap-4 text-[var(--text-2)]">
      <p className="text-sm">發生錯誤：{error.message}</p>
      <button
        onClick={reset}
        className="px-4 py-2 text-[13px] rounded-lg bg-[var(--bg-2)] border border-[var(--border)] hover:bg-[var(--border)] text-[var(--text-2)]"
      >
        重試
      </button>
    </div>
  );
}
