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
    const handleProductSubmit = (data: ProductData) => {
    console.log('Product form submitted:', data);
    // TODO: send data to your backend or AI generation endpoint
  };
  return (
    <div className="min-h-screen bg-background">
      
      <Navigation />
      <HeroSection />
      <FeaturesSection />
      {/* temporary added for preview */}
      <FeaturedProducts  products={products}/>
      {/* product form */}

       <section className="py-16 bg-background">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-2xl font-bold text-foreground mb-6">
            Add Your Own Product
          </h2>
          <ProductForm onSubmit={handleProductSubmit} />
        </div>
      </section>
      {/* temporary added for preview */}
      <HowItWorksSection />
      <CTASection />
      <Footer />
    </div>
  );
};

export default Index;