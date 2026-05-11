"use client";

import { useEffect, useRef, useState } from "react";
import { useInView, useReducedMotion } from "framer-motion";

interface CountUpProps {
  end: number;
  suffix?: string;
  decimals?: number;
  duration?: number;
  className?: string;
}

export function CountUp({
  end,
  suffix = "",
  decimals = 0,
  duration = 1.4,
  className,
}: CountUpProps) {
  const ref = useRef<HTMLSpanElement>(null);
  const isInView = useInView(ref, { once: true, amount: 0.4 });
  const reduced = useReducedMotion();
  const [count, setCount] = useState(reduced ? end : 0);

  useEffect(() => {
    if (reduced) {
      setCount(end);
      return;
    }
    if (!isInView) return;

    const factor = Math.pow(10, decimals);
    let startTime: number | null = null;
    let raf: number;

    function step(ts: number) {
      if (startTime === null) startTime = ts;
      const progress = Math.min((ts - startTime) / (duration * 1000), 1);
      const eased = 1 - Math.pow(1 - progress, 4); // ease-out-quart
      setCount(Math.round(eased * end * factor) / factor);
      if (progress < 1) raf = requestAnimationFrame(step);
      else setCount(end);
    }

    raf = requestAnimationFrame(step);
    return () => cancelAnimationFrame(raf);
  }, [isInView, end, duration, decimals, reduced]);

  const formatted =
    decimals > 0 ? count.toFixed(decimals) : String(Math.round(count));

  return (
    <span ref={ref} className={className}>
      {formatted}
      {suffix}
    </span>
  );
}
