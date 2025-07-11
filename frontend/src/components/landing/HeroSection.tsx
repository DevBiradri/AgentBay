'use client'
import { Button } from "../ui/button";
import { Badge } from "../ui/badge";
import { Sparkles, Upload, Search } from "lucide-react";
import { useRouter } from "next/navigation";
// import marketplaceHero from "@/assets/marketplace-hero.jpg";

const HeroSection = () => {
  const router = useRouter()

  return (
    <section className="relative overflow-hidden py-24 md:py-32">
      <div className="absolute inset-0 bg-gradient-hero opacity-90" />
      <div className="absolute inset-0">
        {/* <img 
          src={marketplaceHero} 
          alt="AI Marketplace Hero" 
          className="w-full h-full object-cover mix-blend-overlay"
        /> */}
        {/* image here */}
      </div>
      <div className="relative container max-w-5xl text-center">
        <Badge className="mb-6 bg-primary/10 text-primary border-primary/20" variant="outline">
          <Sparkles className="w-3 h-3 mr-1" />
          AI-Powered Marketplace
        </Badge>
        <h1 className="text-4xl md:text-6xl font-bold text-white mb-6 animate-slide-up">
          Buy & Sell with
          <span className="bg-gradient-to-r from-blue-200 to-green-200 bg-clip-text text-transparent block">
            AI Intelligence
          </span>
        </h1>
        <p className="text-xl text-white/90 mb-8 max-w-2xl mx-auto animate-slide-up">
          Upload photos, get AI descriptions, and discover products with voice search. 
          Experience the future of online marketplace today.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center animate-slide-up">
          <Button 
            size="lg" 
            variant="hero"
            onClick={() => router.push('/chat')}
            className="text-lg"
          >
            <Upload className="w-5 h-5 mr-2" />
            Start Selling
          </Button>
          <Button 
            size="lg" 
            variant="marketplace"
            onClick={() => router.push('/chat')}
            className="text-lg"
          >
            <Search className="w-5 h-5 mr-2" />
            Shop Now
          </Button>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;