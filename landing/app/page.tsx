import { LangProvider } from "@/components/LangProvider";
import { Navbar } from "@/components/Navbar";
import { Hero } from "@/components/Hero";
import { HallazgosSection } from "@/components/HallazgosSection";
import { DimensionsSection } from "@/components/DimensionsSection";
import { MethodologySection } from "@/components/MethodologySection";
import { RankingsSection } from "@/components/RankingsSection";
import { GallerySection } from "@/components/GallerySection";
import { CTASection } from "@/components/CTASection";
import { CreditsSection } from "@/components/CreditsSection";
import { ScrollToTopFAB } from "@/components/ScrollToTopFAB";

export default function Home() {
  return (
    <LangProvider>
      <a
        href="#hero"
        className="sr-only focus:not-sr-only focus:fixed focus:top-4 focus:left-4 focus:z-[100] focus:rounded focus:bg-primary focus:px-4 focus:py-2 focus:text-sm focus:font-medium focus:text-primary-foreground"
      >
        Saltar al contenido / Skip to content
      </a>
      <Navbar />
      <main id="main-content">
        {/* 1. Propuesta */}
        <Hero />
        {/* 2. Muestra la herramienta — el producto primero */}
        <GallerySection />
        <CTASection />
        {/* 3. ¿Qué encontramos? — establece credibilidad */}
        <HallazgosSection />
        {/* 4. ¿Cómo medimos? — explica las dimensiones ISO */}
        <DimensionsSection />
        {/* 5. ¿Cómo calificamos? — Bronze / Silver / Gold */}
        <MethodologySection />
        {/* 6. ¿Quién salió cómo? — datos completos por dependencia */}
        <RankingsSection />
      </main>
      <CreditsSection />
      <ScrollToTopFAB />
    </LangProvider>
  );
}
