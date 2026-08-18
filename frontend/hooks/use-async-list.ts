"use client";

import { useCallback, useEffect, useRef, useState } from "react";

export function useAsyncList<T>(loader: () => Promise<T[]>) {
  const loaderRef = useRef(loader);
  loaderRef.current = loader;

  const [items, setItems] = useState<T[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const reload = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setItems(await loaderRef.current());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load data");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void reload();
  }, [reload]);

  return { items, loading, error, reload, setItems };
}
