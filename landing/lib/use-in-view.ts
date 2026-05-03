import { RefObject, useEffect, useState } from "react";

export function useInView(ref: RefObject<Element | null>, threshold = 0.15) {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    const obs = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setVisible(true);
          obs.disconnect();
        }
      },
      { threshold }
    );

    obs.observe(el);
    return () => obs.disconnect();
  }, [ref, threshold]);

  return visible;
}
