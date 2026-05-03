import { LangProvider } from "@/components/LangProvider";
import { Navbar } from "@/components/Navbar";
import { Hero } from "@/components/Hero";
import { SaludInstitucionalSection } from "@/components/SaludInstitucionalSection";
import { DimensionsSection } from "@/components/DimensionsSection";
import { RankingsSection } from "@/components/RankingsSection";
import { MethodologySection } from "@/components/MethodologySection";
import { CreditsSection } from "@/components/CreditsSection";

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
        <Hero />
        <SaludInstitucionalSection />
        <DimensionsSection />
        <RankingsSection />
        <MethodologySection />
      </main>
      <CreditsSection />
    </LangProvider>
  );
}
