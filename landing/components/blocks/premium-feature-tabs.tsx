import { Tabs, TabsContent, TabsList, TabsTrigger } from "@radix-ui/react-tabs";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { motion, AnimatePresence } from "framer-motion";

export interface TabContent {
  badge: string;
  title: string;
  description: string;
  buttonText?: string;
  buttonLink?: string;
  imageSrc: string;
  imageAlt: string;
}

export interface Tab {
  value: string;
  icon: React.ReactNode;
  label: string;
  content: TabContent;
}

export interface PremiumFeatureTabsProps {
  badge?: string;
  heading?: React.ReactNode | string;
  description?: string;
  tabs?: Tab[];
  children?: React.ReactNode;
}

export const PremiumFeatureTabs = ({
  badge = "NL 2026",
  heading = "Gobernanza Pro",
  description = "Plataforma de evaluación automática",
  tabs = [],
  children,
}: PremiumFeatureTabsProps) => {
  if (!tabs.length) return null;

  return (
    <section className="relative py-24 md:py-32 overflow-hidden">
      {/* Premium ambient glows */}
      <div className="pointer-events-none absolute left-1/2 top-0 -z-10 h-[800px] w-[1200px] -translate-x-1/2 opacity-20">
        <div className="absolute inset-0 bg-gradient-to-r from-teal-500/30 to-rose-500/30 blur-3xl mix-blend-screen" />
      </div>

      <div className="container relative z-10 mx-auto px-4 md:px-8">
        <div className="flex flex-col items-center gap-6 text-center mb-12">
          {badge && (
            <Badge variant="outline" className="border-teal-500/30 bg-teal-500/10 text-teal-400 uppercase tracking-widest px-4 py-1">
              {badge}
            </Badge>
          )}
          
          <h1 className="max-w-3xl text-4xl font-serif font-bold md:text-6xl text-foreground">
            {heading}
          </h1>
          
          <p className="text-xl text-muted-foreground max-w-2xl font-light">
            {description}
          </p>
          
          {/* Optional children injected here, like stat cards */}
          {children && (
            <div className="w-full mt-6">
              {children}
            </div>
          )}
        </div>

        <Tabs defaultValue={tabs[0].value} className="mt-12 w-full">
          <TabsList className="flex flex-wrap items-center justify-center gap-2 sm:gap-4 mb-8">
            {tabs.map((tab) => (
              <TabsTrigger
                key={tab.value}
                value={tab.value}
                className="group flex items-center gap-2 rounded-full px-5 py-3 text-sm font-medium transition-all data-[state=active]:bg-primary data-[state=active]:text-primary-foreground data-[state=active]:shadow-lg data-[state=active]:shadow-primary/25 bg-black/5 dark:bg-white/5 text-muted-foreground hover:bg-black/10 dark:hover:bg-white/10 hover:text-foreground outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 focus-visible:ring-offset-background"
              >
                <span className="opacity-70 group-data-[state=active]:opacity-100 transition-opacity">
                  {tab.icon}
                </span>
                {tab.label}
              </TabsTrigger>
            ))}
          </TabsList>
          
          <div className="mx-auto max-w-6xl rounded-[2.5rem] bg-black/5 dark:bg-white/5 border border-black/10 dark:border-white/10 backdrop-blur-xl p-6 sm:p-10 lg:p-16 shadow-2xl overflow-hidden relative">
            {/* Subtle inner reflection */}
            <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/20 to-transparent" />
            
            {tabs.map((tab) => (
              <TabsContent
                key={tab.value}
                value={tab.value}
                className="outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 rounded-xl"
              >
                <div className="grid place-items-center gap-12 lg:grid-cols-2 lg:gap-16">
                  <motion.div 
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.5 }}
                    className="flex flex-col gap-6 w-full"
                  >
                    <Badge variant="outline" className="w-fit bg-background/50 backdrop-blur-md border-border/50 text-xs">
                      {tab.content.badge}
                    </Badge>
                    <h3 className="text-3xl font-serif font-bold lg:text-5xl leading-tight text-foreground">
                      {tab.content.title}
                    </h3>
                    <p className="text-muted-foreground text-lg leading-relaxed">
                      {tab.content.description}
                    </p>
                    
                    {tab.content.buttonText && (
                      <Button 
                        className="mt-4 w-fit rounded-full px-8 bg-gradient-to-r from-primary to-primary/80 hover:to-primary text-primary-foreground shadow-lg shadow-primary/25 border-none transition-transform hover:scale-105" 
                        size="lg"
                        asChild={!!tab.content.buttonLink}
                      >
                        {tab.content.buttonLink ? (
                          <a href={tab.content.buttonLink}>{tab.content.buttonText}</a>
                        ) : (
                          tab.content.buttonText
                        )}
                      </Button>
                    )}
                  </motion.div>
                  
                  <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.5, delay: 0.1 }}
                    className="w-full relative aspect-square lg:aspect-auto lg:h-[500px] rounded-3xl overflow-hidden shadow-2xl border border-white/10 group"
                  >
                    <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent z-10 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                    <img
                      src={tab.content.imageSrc}
                      alt={tab.content.imageAlt}
                      className="w-full h-full object-cover transform transition-transform duration-700 group-hover:scale-105"
                    />
                  </motion.div>
                </div>
              </TabsContent>
            ))}
          </div>
        </Tabs>
      </div>
    </section>
  );
};
