import Navigation from "@/components/landing/Navigation";
import HeroSection from "@/components/landing/HeroSection";
import FeaturesSection from "@/components/landing/FeaturesSection";
import HowItWorksSection from "@/components/landing/HowItWorksSection";
import CTASection from "@/components/landing/CTASection";
import Footer from "@/components/landing/Footer";
import FeaturedProducts from "@/components/landing/FeaturedProducts";
import {products} from "@/data/products.js"
import ProductForm, {ProductData} from "@/components/landing/ProductForm";
const Index = () => {
  
  return (
    <div className="min-h-screen bg-background">
      
      <Navigation />
      <HeroSection />
      <FeaturesSection />
      {/* temporary added for preview */}
      <FeaturedProducts  products={products}/>
      {/* product form */}

      
      {/* temporary added for preview */}
      <HowItWorksSection />
      <CTASection />
      <Footer />
    </div>
  );
};

export default Index;