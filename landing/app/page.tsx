import { LangProvider } from "@/components/LangProvider";
import { Navbar } from "@/components/Navbar";
import { Hero } from "@/components/Hero";
import { Illustration } from "@/components/ui/Illustration";
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
        
        <section className="py-20 bg-background overflow-hidden">
          <div className="editorial-container flex flex-col md:flex-row items-center gap-12 px-6">
            <div className="flex-1 text-left">
              <span className="eyebrow">Diagnóstico</span>
              <h2 className="text-4xl font-serif font-bold mb-6">Salud Institucional</h2>
              <p className="text-muted-foreground text-lg">
                Visualizamos la madurez de los datos en toda la administración pública, identificando líderes en transparencia y áreas que requieren remediación técnica.
              </p>
            </div>
            <div className="flex-1 w-full max-w-[300px]">
              <Illustration type="organizaciones" className="w-full h-auto animate-float" />
            </div>
          </div>
        </section>

        <DimensionsSection />
        <RankingsSection />
        <MethodologySection />
      </main>
      <CreditsSection />
    </LangProvider>
  );
}
