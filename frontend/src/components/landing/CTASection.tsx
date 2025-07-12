import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";

const CTASection = () => {
  const navigate = useNavigate();

  return (
    <section className="py-24 bg-gradient-hero relative overflow-hidden">
      <div className="absolute inset-0 bg-black/20" />
      <div className="relative container max-w-3xl text-center">
        <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
          Ready to Transform Your Marketplace Experience?
        </h2>
        <p className="text-xl text-white/90 mb-8">
          Join thousands of users already enjoying smarter buying and selling
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Button size="lg" variant="hero" className="text-lg" onClick={() => navigate('/chat')}>
            Start Selling Today
          </Button>
          <Button size="lg" variant="marketplace" className="text-lg" onClick={() => navigate('/chat')}>
            Browse Products
          </Button>
        </div>
      </div>
    </section>
  );
};

export default CTASection;