"use client";

import { useEffect, useState } from "react";
import { ArrowUp } from "lucide-react";
import { useLang } from "./LangProvider";

export function ScrollToTopFAB() {
  const { t } = useLang();
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const onScroll = () => setVisible(window.scrollY > 400);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <button
      onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
      aria-label={t("Volver al inicio", "Back to top")}
      className={`fixed bottom-6 right-6 z-50 flex size-12 items-center justify-center rounded-full bg-teal text-white shadow-lg shadow-teal/30 transition-all duration-300 hover:scale-110 hover:bg-teal-light hover:shadow-xl hover:shadow-teal/40 focus-visible:outline focus-visible:outline-2 focus-visible:outline-teal focus-visible:outline-offset-2 active:scale-[0.96] ${
        visible
          ? "pointer-events-auto opacity-100"
          : "pointer-events-none opacity-0"
      }`}
    >
      <ArrowUp className="size-5" aria-hidden="true" />
    </button>
  );
}
