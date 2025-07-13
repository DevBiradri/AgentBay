import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";

const CTASection = () => {
  const navigate = useNavigate();

  return (
    <section className="py-24 bg-muted/30 relative overflow-hidden">
      <div className="relative container max-w-3xl text-center">
        <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
          Ready to Experience the Future?
        </h2>
        <p className="text-xl text-white/90 mb-8">
          Join thousands of smart sellers and buyers who've already discovered the power of AI-driven commerce.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Button size="lg" variant="hero" className="text-lg" onClick={() => navigate('/chat')}>
            Get Started Free
          </Button>
        </div>
      </div>
    </section>
  );
};

export default CTASection;