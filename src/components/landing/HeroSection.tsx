import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Sparkles, Upload, Search } from "lucide-react";
import { useNavigate } from "react-router-dom";
import marketplaceHero from "@/assets/marketplace-hero.jpg";

const HeroSection = () => {
  const navigate = useNavigate();

  return (

        <section>


    <div className="relative py-12 bg-gray-900 sm:py-16 lg:py-20 xl:pt-32 xl:pb-44">
        <div className="absolute inset-0 hidden lg:block">
            <img className="object-cover object-right-bottom w-full h-full" src="https://cdn.rareblocks.xyz/collection/clarity-ecommerce/images/hero/1/background.png" alt="" />
        </div>

        <div className="relative px-4 mx-auto sm:px-6 lg:px-8 max-w-7xl">
            <div className="max-w-xl mx-auto text-center lg:max-w-md xl:max-w-lg lg:text-left lg:mx-0">
                <h1 className="text-3xl font-bold text-white sm:text-4xl xl:text-5xl xl:leading-tight">Find What You Need — Just Say It.</h1>
                <p className="mt-8 text-base font-normal leading-7 text-gray-400 lg:max-w-md xl:pr-0 lg:pr-16">Shop smarter with voice and text. Discover products effortlessly with your words.</p>

                <div className="flex items-center justify-center mt-8 space-x-5 xl:mt-16 lg:justify-start">
                    <button
                        onClick={()=>navigate('/chat')}
                        title=""
                        className="
                            inline-flex
                            items-center
                            justify-center
                            px-3
                            py-3
                            text-base
                            font-bold
                            leading-7
                            text-gray-900
                            transition-all
                            duration-200
                            bg-white
                            border border-transparent
                            rounded-md
                            sm:px-6
                            focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-900 focus:ring-white
                            hover:bg-gray-200
                        "
                        role="button"
                    >
                        Start Selling
                    </button>

                    <button
                    onClick={()=>navigate('/chat')}
                        title=""
                        className="
                            inline-flex
                            items-center
                            justify-center
                            px-2
                            py-3
                            text-base
                            font-bold
                            leading-7
                            text-white
                            transition-all
                            duration-200
                            bg-transparent
                            border border-transparent
                            rounded-md
                            sm:px-4
                            focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-900 focus:ring-gray-700
                            hover:bg-gray-700
                        "
                        role="button"
                    >
                        Shop Now
                    </button>
                </div>
                
            </div>
        </div>

        <div className="mt-8 lg:hidden">
            <img className="object-cover w-full h-full" src="https://cdn.rareblocks.xyz/collection/clarity-ecommerce/images/hero/1/bg.png" alt="" />
        </div>
    </div>
</section>


    // <section className="relative overflow-hidden py-24 md:py-32">
    //   <div className="absolute inset-0 bg-gradient-hero opacity-90" />
    //   <div className="absolute inset-0">
    //     <img 
    //       src={marketplaceHero} 
    //       alt="AI Marketplace Hero" 
    //       className="w-full h-full object-cover mix-blend-overlay"
    //     />
    //   </div>
    //   <div className="relative container max-w-5xl text-center">
    //     <Badge className="mb-6 bg-primary/10 text-primary border-primary/20" variant="outline">
    //       <Sparkles className="w-3 h-3 mr-1" />
    //       AI-Powered Marketplace
    //     </Badge>
    //     <h1 className="text-4xl md:text-6xl font-bold text-white mb-6 animate-slide-up">
    //       Buy & Sell with
    //       <span className="bg-gradient-to-r from-blue-200 to-green-200 bg-clip-text text-transparent block">
    //         AI Intelligence
    //       </span>
    //     </h1>
    //     <p className="text-xl text-white/90 mb-8 max-w-2xl mx-auto animate-slide-up">
    //       Upload photos, get AI descriptions, and discover products with voice search. 
    //       Experience the future of online marketplace today.
    //     </p>
    //     <div className="flex flex-col sm:flex-row gap-4 justify-center animate-slide-up">
    //       <Button 
    //         size="lg" 
    //         variant="hero"
    //         onClick={() => navigate('/chat')}
    //         className="text-lg"
    //       >
    //         <Upload className="w-5 h-5 mr-2" />
    //         Start Selling
    //       </Button>
    //       <Button 
    //         size="lg" 
    //         variant="marketplace"
    //         onClick={() => navigate('/chat')}
    //         className="text-lg"
    //       >
    //         <Search className="w-5 h-5 mr-2" />
    //         Shop Now
    //       </Button>
    //     </div>
    //   </div>
    // </section>
  );
};

export default HeroSection;